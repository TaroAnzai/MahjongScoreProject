from datetime import datetime, timezone

from app import db
from app.models import AccessLevel, Group
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
# グループ作成
# =========================================================
def create_group(data: dict) -> Group:
    name = data.get("name")
    if not name:
        raise ServiceValidationError("グループ名は必須です。")

    group = Group(
        name=name,
        description=data.get("description"),
        created_by=data.get("created_by", "anonymous"),
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(group)
    db.session.flush()

    # デフォルト共有リンク作成
    create_default_share_links("group", group.id, group.created_by)
    db.session.refresh(group)
    return group


# =========================================================
# グループ取得
# =========================================================
def get_group_by_key(short_key: str) -> Group:
    """共有リンクキーからグループを取得"""
    _, group = _require_group(short_key)
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
