# app/services/group_service.py
from datetime import datetime, timezone
from app import db
from app.models import Group, AccessLevel
from app.utils.share_link_utils import (
    get_share_link_by_key,
    create_default_share_links,
)
from app.service_errors import (
    ServicePermissionError,
    ServiceValidationError,
    ServiceNotFoundError,
)


def get_group_by_short_key(short_key: str):
    """短縮キーでグループを取得"""
    link = get_share_link_by_key(short_key)
    if not link or link.resource_type != "group":
        raise ServiceNotFoundError("無効または期限切れの共有リンクです。")

    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("対象のグループが見つかりません。")

    return group


def create_group(data: dict):
    """グループを作成し、OWNER/EDIT/VIEWリンクを発行"""
    group = Group(
        name=data["name"],
        description=data.get("description", ""),
        created_by="anonymous",
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(group)
    db.session.commit()

    # ✅ 全権限リンクを作成してDBに反映
    create_default_share_links("group", group.id, group.created_by)
    db.session.commit()

    # ✅ リレーションを最新化
    db.session.refresh(group)
    return group


def update_group(group_id: int, data: dict, short_key: str):
    """OWNERリンクのみグループを更新可能"""
    link = get_share_link_by_key(short_key)
    group = Group.query.get_or_404(group_id)

    if not link or link.resource_type != "group":
        raise ServiceNotFoundError("無効な共有リンクです。")

    if link.access_level != AccessLevel.OWNER:
        raise ServicePermissionError("グループを更新できるのはOWNER権限のみです。")

    if "name" in data:
        group.name = data["name"]
    if "description" in data:
        group.description = data["description"]

    group.last_updated_at = datetime.now(timezone.utc)
    db.session.commit()
    db.session.refresh(group)
    return group


def delete_group(group_id: int, short_key: str):
    """OWNERリンクのみグループ削除可能"""
    link = get_share_link_by_key(short_key)
    group = Group.query.get_or_404(group_id)

    if not link or link.resource_type != "group":
        raise ServiceNotFoundError("無効な共有リンクです。")

    if link.access_level != AccessLevel.OWNER:
        raise ServicePermissionError("グループを削除できるのはOWNER権限のみです。")

    db.session.delete(group)
    db.session.commit()
    return True
