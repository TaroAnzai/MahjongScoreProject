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


def _require_group(short_key: str):
    """共有キーからグループを特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "group":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")
    return link, group


def _ensure_access(link, required: AccessLevel, message: str):
    """アクセスレベルチェック"""
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


# =========================================================
# プレイヤー一覧
# =========================================================
def list_players_by_group_key(group_key: str):
    """グループ共有キーからプレイヤー一覧取得"""
    link, group = _require_group(group_key)
    _ensure_access(link, AccessLevel.VIEW, "プレイヤーを閲覧する権限がありません。")

    return Player.query.filter_by(group_id=group.id).order_by(Player.id).all()


# =========================================================
# プレイヤー作成
# =========================================================
def create_player(data: dict, group_key: str) -> Player:
    """グループ共有キーからプレイヤー作成"""
    name = data.get("name")
    if not name:
        raise ServiceValidationError("name は必須です。")

    link, group = _require_group(group_key)
    _ensure_access(link, AccessLevel.EDIT, "プレイヤーを追加する権限がありません。")

    player = Player(
        group_id=group.id,
        name=name,
        nickname=data.get("nickname"),
        display_order=data.get("display_order"),
    )
    db.session.add(player)
    db.session.commit()
    return player


# =========================================================
# プレイヤー取得・更新・削除
# =========================================================
def get_player_by_key(group_key: str, player_id: int) -> Player:
    """プレイヤー共有キーから取得"""
    link = get_share_link_by_key(group_key)
    if not link or link.resource_type != "group":
        raise ServicePermissionError("共有リンクが不正です。")

    _ensure_access(link, AccessLevel.VIEW, "プレイヤーを閲覧する権限がありません。")
    player = Player.query.filter_by(id=player_id, group_id=link.resource_id).first()
    if not player:
        raise ServiceNotFoundError("プレイヤーが見つかりません。")
    return player


def update_player(group_key: str, player_id: int, data: dict) -> Player:
    """プレイヤー共有キーから更新"""
    link = get_share_link_by_key(group_key)
    if not link or link.resource_type != "group":
        raise ServicePermissionError("共有リンクが不正です。")
    player = Player.query.filter_by(id=player_id, group_id=link.resource_id).first()
    if not player:
        raise ServiceNotFoundError("プレイヤーが見つかりません。")

    _ensure_access(link, AccessLevel.EDIT, "プレイヤーを更新する権限がありません。")

    if "name" in data:
        player.name = data["name"]
    if "nickname" in data:
        player.nickname = data["nickname"]
    if "display_order" in data:
        player.display_order = data["display_order"]

    db.session.commit()
    return player


def delete_player(group_key: str, player_id: int) -> None:
    """プレイヤー共有キーから削除"""
    link = get_share_link_by_key(group_key)
    if not link or link.resource_type != "group":
        raise ServicePermissionError("共有リンクが不正です。")

    player = Player.query.filter_by(id=player_id, group_id=link.resource_id).first()
    if not player:
        raise ServiceNotFoundError("プレイヤーが見つかりません。")

    _ensure_access(link, AccessLevel.EDIT, "プレイヤーを削除する権限がありません。")

    db.session.delete(player)
    db.session.commit()
