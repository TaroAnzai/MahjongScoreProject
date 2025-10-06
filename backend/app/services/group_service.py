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


def _require_group(short_key: str):
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
    if link.resource_id != group.id:
        raise ServicePermissionError("共有リンクの対象が一致しません。")
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


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
    create_default_share_links("group", group.id, group.created_by)
    db.session.refresh(group)
    return group


def get_group_by_short_key(short_key: str) -> Group:
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "group":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")
    return group


def update_group(group_id: int, data: dict, short_key: str) -> Group:
    group = Group.query.get(group_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")

    link, linked_group = _require_group(short_key)
    _ensure_access(link, linked_group, AccessLevel.OWNER, "グループの更新にはOWNER権限が必要です。")

    if "name" in data:
        group.name = data["name"]
    if "description" in data:
        group.description = data["description"]

    group.last_updated_at = datetime.now(timezone.utc)
    db.session.commit()
    db.session.refresh(group)
    return group


def delete_group(group_id: int, short_key: str) -> None:
    group = Group.query.get(group_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")

    link, linked_group = _require_group(short_key)
    _ensure_access(link, linked_group, AccessLevel.OWNER, "グループの削除にはOWNER権限が必要です。")

    db.session.delete(group)
    db.session.commit()
