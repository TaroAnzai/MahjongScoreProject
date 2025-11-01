from datetime import datetime, timezone, timedelta
from flask import current_app
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

_ACCESS_PRIORITY = {
    AccessLevel.VIEW: 1,
    AccessLevel.EDIT: 2,
    AccessLevel.OWNER: 3,
}

from app.tasks.email_tasks import send_group_creation_email_task


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
def create_group_creation_token(data: GroupRequestSchema) -> GroupCreationToken:
    email = data.get('email')
    group_name = data.get('name')
    """グループ作成トークンを発行し、メール送信（30分有効）"""
    if not email:
        raise ServiceValidationError("メールアドレスは必須です。")

    if not group_name:
        raise ServiceValidationError("グループ名は必須です。")

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

    send_group_creation_email_task.delay(new_token.email, url)

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

    if record.expires_at.tzinfo is None:
        record.expires_at = record.expires_at.replace(tzinfo=timezone.utc)
    if record.expires_at < datetime.now(timezone.utc):
        raise ServiceValidationError("このトークンは有効期限が切れています。")

    record.is_used = True
    db.session.commit()
    name = record.group_name

    group = Group(
        name=name,
        description=data.get("description"),
        created_by=data.get("created_by", "anonymous"),
        created_at=datetime.now(timezone.utc),
        email = record.email
    )
    db.session.add(group)
    db.session.flush()

    # デフォルト共有リンク作成
    create_default_share_links("group", group.id, group.created_by)
    db.session.refresh(group)
    group.current_user_access = "OWNER"
    return group


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
