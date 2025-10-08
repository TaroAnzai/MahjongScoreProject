# app/services/table_player_service.py

from app import db
from app.models import AccessLevel, Group, Table, TablePlayer, TournamentPlayer, Tournament
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
    """共有リンクからGroupを特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")

    if link.resource_type == "group":
        group = Group.query.get(link.resource_id)
    elif link.resource_type == "tournament":
        tournament = Tournament.query.get(link.resource_id)
        group = Group.query.get(tournament.group_id) if tournament else None
    elif link.resource_type == "table":
        table = Table.query.get(link.resource_id)
        tournament = Tournament.query.get(table.tournament_id) if table else None
        group = Group.query.get(tournament.group_id) if tournament else None
    else:
        raise ServicePermissionError("共有リンクの対象が不正です。")

    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")

    return link, group


def _ensure_access(link_access: AccessLevel, required: AccessLevel, message: str):
    if _ACCESS_PRIORITY[link_access] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


class TablePlayerService:
    @staticmethod
    def list_by_table(short_key: str, table_id: int):
        """卓の参加者一覧取得"""
        link, group = _require_group_link(short_key)
        _ensure_access(link.access_level, AccessLevel.VIEW, "卓の参加者を閲覧する権限がありません。")

        table = Table.query.get(table_id)
        if not table:
            raise ServiceNotFoundError("卓が見つかりません。")

        tournament = Tournament.query.get(table.tournament_id)
        if not tournament or tournament.group_id != group.id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")

        return TablePlayer.query.filter_by(table_id=table_id).all()

    @staticmethod
    def create(short_key: str, table_id: int, data: dict):
        """卓に参加者を追加"""
        link, group = _require_group_link(short_key)
        _ensure_access(link.access_level, AccessLevel.EDIT, "卓にプレイヤーを追加する権限がありません。")

        table = Table.query.get(table_id)
        if not table:
            raise ServiceNotFoundError("卓が見つかりません。")

        tournament = Tournament.query.get(table.tournament_id)
        if not tournament or tournament.group_id != group.id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")

        player_id = data.get("player_id")
        seat_position = data.get("seat_position")

        participant = TournamentPlayer.query.get(player_id)
        if not participant or participant.tournament_id != tournament.id:
            raise ServiceNotFoundError("指定された大会参加者が見つかりません。")

        existing = TablePlayer.query.filter_by(
            table_id=table.id, player_id=player_id
        ).first()
        if existing:
            raise ServiceValidationError("この参加者はすでに卓に登録されています。")

        table_player = TablePlayer(
            table_id=table.id,
            player_id=player_id,
            seat_position=seat_position,
        )
        db.session.add(table_player)
        db.session.commit()
        return table_player

    @staticmethod
    def delete(short_key: str, table_id: int, table_player_id: int):
        """卓参加者を削除"""
        link, group = _require_group_link(short_key)
        _ensure_access(link.access_level, AccessLevel.EDIT, "卓参加者を削除する権限がありません。")

        table_player = TablePlayer.query.get(table_player_id)
        if not table_player:
            raise ServiceNotFoundError("卓参加者が見つかりません。")

        table = Table.query.get(table_id)
        tournament = Tournament.query.get(table.tournament_id) if table else None
        if not tournament or tournament.group_id != group.id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")

        db.session.delete(table_player)
        db.session.commit()
