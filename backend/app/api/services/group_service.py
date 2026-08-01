from datetime import datetime, timezone, timedelta
import os
from flask import app, current_app, request
import secrets
from app import db
from app.models import AccessLevel, Group, GroupCreationToken
from app.api.schemas.group_schema import GroupRequestSchema, GroupCreateSchema
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.utils.share_link_utils import create_default_share_links, get_share_link_by_key
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_ACCESS_PRIORITY = {
    AccessLevel.VIEW: 1,
    AccessLevel.EDIT: 2,
    AccessLevel.OWNER: 3,
}

from app.tasks.email_tasks import send_group_creation_email_task
from app.utils.recaptcha import verify_recaptcha


# =========================================================
# 内部ユーティリティ
# =========================================================


def _require_group(short_key: str):
    """共有リンクからGroupを特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "group":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")
    return link, group


def _ensure_access(link, group, required: AccessLevel, message: str):
    """アクセスレベルチェック"""
    if link.resource_id != group.id:
        raise ServicePermissionError("共有リンクの対象が一致しません。")
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)

# =========================================================
# グループ作成メール送信
# =========================================================
def get_client_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.remote_addr or "unknown"

def check_group_creation_rate_limit(email: str, ip_address: str) -> None:
    now = datetime.now(timezone.utc)

    ip_count_1h = GroupCreationToken.query.filter(
        GroupCreationToken.ip_address == ip_address,
        GroupCreationToken.created_at >= now - timedelta(hours=1),
    ).count()

    if ip_count_1h >= 5:
        raise ServicePermissionError("同一IPからのリクエストが多すぎます。しばらくしてから再試行してください。")

    email_count_1h = GroupCreationToken.query.filter(
        GroupCreationToken.email == email,
        GroupCreationToken.created_at >= now - timedelta(hours=1),
    ).count()

    if email_count_1h >= 3:
        raise ServicePermissionError("同一メールアドレスへの送信回数が多すぎます。しばらくしてから再試行してください。")

    email_count_1d = GroupCreationToken.query.filter(
        GroupCreationToken.email == email,
        GroupCreationToken.created_at >= now - timedelta(days=1),
    ).count()

    if email_count_1d >= 10:
        raise ServicePermissionError("本日の送信回数上限に達しました。明日以降に再試行してください。")
def create_group_creation_token(data: GroupRequestSchema) -> GroupCreationToken:
    email = data.get('email')
    group_name = data.get('name')
    tz_str = data.get('timezone',"Asia/Tokyo")

    try:
        tz = ZoneInfo(tz_str)
    except ZoneInfoNotFoundError:
        raise ServiceValidationError("タイムゾーンが正しくありません。")

    """グループ作成トークンを発行し、メール送信（30分有効）"""
    if not email:
        raise ServiceValidationError("メールアドレスは必須です。")

    if not group_name:
        raise ServiceValidationError("グループ名は必須です。")

    ip_address = get_client_ip()

    # アクセス制限チェック
    if os.getenv("FLASK_ENV") == "production":
        check_group_creation_rate_limit(email, ip_address)

    # 既存の未使用トークンを無効化
    existing_tokens = GroupCreationToken.query.filter_by(email=email, is_used=False).all()
    for token in existing_tokens:
        token.is_used = True

    # トークン生成
    new_token = GroupCreationToken(
        email=email,
        group_name=group_name,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        is_used=False,
    )

    db.session.add(new_token)
    db.session.commit()

    # メール送信をCeleryで実行
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173/")
    url = f"{frontend_url}/group/create?token={new_token.token}"

    expires_at = new_token.expires_at.astimezone(tz)
    expires_at_str = expires_at.strftime("%Y-%m-%d %H:%M")

    send_group_creation_email_task.delay(new_token.email, url, new_token.group_name,expires_at_str)

    return new_token
# =========================================================
# グループ作成
# =========================================================
def create_group(data: GroupCreateSchema) -> Group:
    token = data.get("token")
    """トークン検証"""
    record = GroupCreationToken.query.filter_by(token=token).first()

    if not record:
        raise ServiceNotFoundError("トークンが無効です。")

    if record.is_used:
        raise ServiceValidationError("このトークンはすでに使用されています。")

    expires_at = record.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise ServiceValidationError("このトークンは有効期限が切れています。")


    group = Group(
        name=record.group_name,
        description=data.get("description"),
        created_by=data.get("created_by", "anonymous"),
        created_at=datetime.now(timezone.utc),
        email = record.email
    )
    db.session.add(group)
    db.session.flush()
    # トークンを作成済みグループに紐付ける
    record.group_id = group.id
    record.is_used = True
    # デフォルト共有リンク作成
    create_default_share_links("group", group.id, group.created_by)
    db.session.refresh(group)
    group.current_user_access = "OWNER"
    return group

def create_group_status(data: GroupRequestSchema) -> dict[str, str]:
    """グループ作成ステータスを取得する"""
    token = data.get("token")
    """トークン検証"""
    record = GroupCreationToken.query.filter_by(token=token).first()

    if not record:
        raise ServiceNotFoundError("トークンが無効です。")

    expires_at = record.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise ServiceValidationError("このトークンは有効期限が切れています。")

    if not record.is_used:
        return {"status": "pending"}

    group = db.session.get(Group, record.group_id)
    if not group:
        raise ServiceNotFoundError("トークンが無効です。")

    group_links = group.group_links
    owner_link = next((link.short_key for link in group_links if link.access_level == AccessLevel.OWNER), None)
    if owner_link is None:
        raise ServiceNotFoundError("オーナーリンクが見つかりません。")

    return {"status": "ready", "owner_link": owner_link}

# =========================================================
# グループ取得
# =========================================================
def get_group_by_key(short_key: str) -> Group:
    """共有リンクキーからグループを取得"""
    link, group = _require_group(short_key)
    group.current_user_access = link.access_level
    return group


# =========================================================
# グループ更新
# =========================================================
def update_group(short_key: str, data: dict) -> Group:
    """共有リンクキーからGroupを特定して更新"""
    link, group = _require_group(short_key)
    _ensure_access(link, group, AccessLevel.OWNER, "グループの更新にはOWNER権限が必要です。")

    if "name" in data:
        group.name = data["name"]
    if "description" in data:
        group.description = data["description"]

    group.last_updated_at = datetime.now(timezone.utc)
    db.session.commit()
    db.session.refresh(group)
    group.current_user_access = link.access_level
    return group


# =========================================================
# グループ削除
# =========================================================
def delete_group(short_key: str) -> None:
    """共有リンクキーからGroupを特定して削除"""
    link, group = _require_group(short_key)
    _ensure_access(link, group, AccessLevel.OWNER, "グループの削除にはOWNER権限が必要です。")

    db.session.delete(group)
    db.session.commit()
