# app/services/tournament_participant_service.py

from app import db
from app.models import AccessLevel, Group, Tournament, TournamentPlayer, Player
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
    """共有リンクからGroupとTournamentを特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type not in ["group", "tournament"]:
        raise ServicePermissionError("共有リンクの対象が不正です。")

    if link.resource_type == "group":
        group = Group.query.get(link.resource_id)
    else:
        tournament = Tournament.query.get(link.resource_id)
        if not tournament:
            raise ServiceNotFoundError("大会が見つかりません。")
        group = Group.query.get(tournament.group_id)

    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")
    return link, group


def _ensure_access(link_access: AccessLevel, required: AccessLevel, message: str):
    if _ACCESS_PRIORITY[link_access] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


class TournamentParticipantService:
    @staticmethod
    def list_by_tournament(short_key: str, tournament_id: int):
        """大会参加者一覧を取得"""
        link, group = _require_group_link(short_key)
        _ensure_access(link.access_level, AccessLevel.VIEW, "参加者一覧を閲覧する権限がありません。")

        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            raise ServiceNotFoundError("大会が見つかりません。")
        if tournament.group_id != group.id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")

        return (
            db.session.query(TournamentPlayer)
            .filter_by(tournament_id=tournament.id)
            .all()
        )

    @staticmethod
    def create(short_key: str, tournament_id: int, data: dict):
        """大会にプレイヤーを追加"""
        player_id = data.get("player_id")
        if not player_id:
            raise ServiceValidationError("player_id は必須です。")

        link, group = _require_group_link(short_key)
        _ensure_access(link.access_level, AccessLevel.EDIT, "大会参加者を追加する権限がありません。")

        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            raise ServiceNotFoundError("大会が見つかりません。")
        if tournament.group_id != group.id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")

        player = Player.query.get(player_id)
        if not player or player.group_id != group.id:
            raise ServiceNotFoundError("プレイヤーが見つからないか、別グループに属しています。")

        existing = TournamentPlayer.query.filter_by(
            tournament_id=tournament_id, player_id=player_id
        ).first()
        if existing:
            raise ServiceValidationError("このプレイヤーはすでに大会に登録されています。")

        participant = TournamentPlayer(tournament_id=tournament.id, player_id=player.id)
        db.session.add(participant)
        db.session.commit()
        return participant

    @staticmethod
    def delete(short_key: str, tournament_id: int, participant_id: int):
        """大会参加者を削除"""
        link, group = _require_group_link(short_key)
        _ensure_access(link.access_level, AccessLevel.EDIT, "大会参加者を削除する権限がありません。")

        participant = TournamentPlayer.query.get(participant_id)
        if not participant:
            raise ServiceNotFoundError("大会参加者が見つかりません。")

        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            raise ServiceNotFoundError("大会が見つかりません。")
        if tournament.group_id != group.id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")

        db.session.delete(participant)
        db.session.commit()
