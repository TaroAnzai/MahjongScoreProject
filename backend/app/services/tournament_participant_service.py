# app/services/tournament_participant_service.py

from app import db
from app.models import AccessLevel, Tournament, TournamentPlayer, Player
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


def _require_tournament(short_key: str):
    """共有キーから大会を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "tournament":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    tournament = Tournament.query.get(link.resource_id)
    if not tournament:
        raise ServiceNotFoundError("大会が見つかりません。")
    return link, tournament


def _ensure_access(link, required: AccessLevel, message: str):
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


# =========================================================
# 参加者一覧
# =========================================================
def list_participants_by_key(tournament_key: str):
    """大会共有キーから参加者一覧を取得"""
    link, tournament = _require_tournament(tournament_key)
    _ensure_access(link, AccessLevel.VIEW, "参加者一覧を閲覧する権限がありません。")

    return TournamentPlayer.query.filter_by(tournament_id=tournament.id).all()


# =========================================================
# 参加者追加
# =========================================================
def create_participant(tournament_key: str, data: dict):
    """大会共有キーからプレイヤーを登録"""
    link, tournament = _require_tournament(tournament_key)
    _ensure_access(link, AccessLevel.EDIT, "参加者を追加する権限がありません。")

    player_id = data.get("player_id")
    if not player_id:
        raise ServiceValidationError("player_id は必須です。")

    player = Player.query.get(player_id)
    if not player:
        raise ServiceNotFoundError("プレイヤーが見つかりません。")
    if player.group_id != tournament.group_id:
        raise ServicePermissionError("プレイヤーが別グループに属しています。")

    existing = TournamentPlayer.query.filter_by(
        tournament_id=tournament.id, player_id=player_id
    ).first()
    if existing:
        raise ServiceValidationError("このプレイヤーはすでに大会に登録されています。")

    participant = TournamentPlayer(tournament_id=tournament.id, player_id=player.id)
    db.session.add(participant)
    db.session.commit()
    return participant


# =========================================================
# 参加者削除
# =========================================================
def delete_participant(participant_key: str):
    """大会参加者共有キーから削除"""
    link = get_share_link_by_key(participant_key)
    if not link or link.resource_type != "tournament_player":
        raise ServicePermissionError("不正な共有リンクです。")

    participant = TournamentPlayer.query.get(link.resource_id)
    if not participant:
        raise ServiceNotFoundError("大会参加者が見つかりません。")

    tournament = Tournament.query.get(participant.tournament_id)
    if not tournament:
        raise ServiceNotFoundError("大会が見つかりません。")

    _ensure_access(link, AccessLevel.OWNER, "大会参加者を削除する権限がありません。")

    db.session.delete(participant)
    db.session.commit()
