from app import db
from app.models import AccessLevel, Group, Player
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.utils.share_link_utils import get_share_link_by_key

_ACCESS_PRIORITY = {
    AccessLevel.VIEW: 1,
    AccessLevel.EDIT: 2,
    AccessLevel.OWNER: 3,
}


def _require_group_link(short_key: str):
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "group":
        raise ServicePermissionError("共有リンクの対象が一致しません。")
    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")
    return link, group


def _ensure_access(link_access: AccessLevel, required: AccessLevel, message: str):
    if _ACCESS_PRIORITY[link_access] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


class PlayerService:
    @staticmethod
    def list_by_group_short_key(short_key: str):
        link, group = _require_group_link(short_key)
        _ensure_access(link.access_level, AccessLevel.VIEW, "プレイヤーを閲覧する権限がありません。")
        return Player.query.filter_by(group_id=group.id).order_by(Player.id).all()

    @staticmethod
    def create_player(data: dict, short_key: str) -> Player:
        group_id = data.get("group_id")
        name = data.get("name")
        if not group_id or not name:
            raise ServiceValidationError("group_id と name は必須です。")

        link, group = _require_group_link(short_key)
        if group.id != group_id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "プレイヤーを追加する権限がありません。")

        player = Player(
            group_id=group.id,
            name=name,
            nickname=data.get("nickname"),
            display_order=data.get("display_order"),
        )
        db.session.add(player)
        db.session.commit()
        return player

    @staticmethod
    def get_player(player_id: int, short_key: str) -> Player:
        player = Player.query.get(player_id)
        if not player:
            raise ServiceNotFoundError("プレイヤーが見つかりません。")
        link, group = _require_group_link(short_key)
        if group.id != player.group_id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")
        _ensure_access(link.access_level, AccessLevel.VIEW, "プレイヤーを閲覧する権限がありません。")
        return player

    @staticmethod
    def update_player(player_id: int, data: dict, short_key: str) -> Player:
        player = Player.query.get(player_id)
        if not player:
            raise ServiceNotFoundError("プレイヤーが見つかりません。")
        link, group = _require_group_link(short_key)
        if group.id != player.group_id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "プレイヤーを更新する権限がありません。")

        if "name" in data:
            player.name = data["name"]
        if "nickname" in data:
            player.nickname = data["nickname"]
        if "display_order" in data:
            player.display_order = data["display_order"]

        db.session.commit()
        return player

    @staticmethod
    def delete_player(player_id: int, short_key: str) -> None:
        player = Player.query.get(player_id)
        if not player:
            raise ServiceNotFoundError("プレイヤーが見つかりません。")
        link, group = _require_group_link(short_key)
        if group.id != player.group_id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "プレイヤーを削除する権限がありません。")

        db.session.delete(player)
        db.session.commit()
