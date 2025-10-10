# app/services/table_player_service.py

from app import db
from app.models import AccessLevel, Table, TablePlayer, TournamentPlayer, Tournament
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


# =========================================================
# 内部ユーティリティ
# =========================================================
def _require_table(short_key: str):
    """共有キーから卓を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "table":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    table = Table.query.get(link.resource_id)
    if not table:
        raise ServiceNotFoundError("卓が見つかりません。")
    return link, table


def _ensure_access(link, required: AccessLevel, message: str):
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


# =========================================================
# 卓参加者一覧
# =========================================================
def list_table_players_by_key(table_key: str):
    """卓共有キーから卓参加者一覧を取得"""
    link, table = _require_table(table_key)
    _ensure_access(link, AccessLevel.VIEW, "卓の参加者を閲覧する権限がありません。")

    return TablePlayer.query.filter_by(table_id=table.id).all()


# =========================================================
# 卓参加者追加
# =========================================================
def create_table_player(table_key: str, data: dict):
    """卓共有キーから大会参加者を登録"""
    link, table = _require_table(table_key)
    _ensure_access(link, AccessLevel.EDIT, "卓に参加者を追加する権限がありません。")

    player_id = data.get("player_id")
    if not player_id:
        raise ServiceValidationError("player_id は必須です。")
    print("in create_table_player:", player_id)
    participant = TournamentPlayer.query.get(player_id)
    if not participant:
        raise ServiceNotFoundError("大会参加者が見つかりません。")

    tournament = Tournament.query.get(table.tournament_id)
    if not tournament or participant.tournament_id != tournament.id:
        raise ServicePermissionError("指定された大会参加者がこの大会に属していません。")

    existing = TablePlayer.query.filter_by(
        table_id=table.id, player_id=player_id
    ).first()
    if existing:
        raise ServiceValidationError("この参加者はすでに卓に登録されています。")

    table_player = TablePlayer(
        table_id=table.id,
        player_id=player_id,
        seat_position=data.get("seat_position"),
    )
    db.session.add(table_player)
    db.session.commit()
    return table_player


# =========================================================
# 卓参加者削除
# =========================================================
def delete_table_player(table_key: str, player_id: int):
    """卓参加者共有キーから削除"""
    link = get_share_link_by_key(table_key)
    if not link or link.resource_type != "table":
        raise ServicePermissionError("不正な共有リンクです。")

    table_player = TablePlayer.query.filter_by(id=player_id, table_id=link.resource_id).first()
    if not table_player:
        raise ServiceNotFoundError("卓参加者が見つかりません。")

    _ensure_access(link, AccessLevel.EDIT, "卓参加者を削除する権限がありません。")

    db.session.delete(table_player)
    db.session.commit()
