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
    tournament_players = (
        db.session.query(TournamentPlayer)
        .filter_by(tournament_id=tournament.id)
        .all()
    )
    result = {
        "tournament_id": tournament.id,
        "participants": [tp.player for tp in tournament_players],
    }

    return result


# =========================================================
# 参加者追加（複数対応）
# =========================================================
def create_participants(tournament_key: str, data: list[dict]):
    """大会共有キーから複数のプレイヤーを登録"""
    link, tournament = _require_tournament(tournament_key)
    data_list = data.get("participants", [])
    _ensure_access(link, AccessLevel.EDIT, "参加者を追加する権限がありません。")
    if not isinstance(data_list, list) or not data_list:
        raise ServiceValidationError("data_list は空ではいけません。")

    added_participants = []
    errors = []

    for i, data in enumerate(data_list, start=1):
        player_id = data.get("player_id")
        if not player_id:
            errors.append({"index": i, "error": "player_id は必須です。"})
            continue

        player = Player.query.get(player_id)
        if not player:
            errors.append({"index": i, "error": f"プレイヤー（ID={player_id}）が見つかりません。"})
            continue
        if player.group_id != tournament.group_id:
            errors.append({"index": i, "error": f"プレイヤー（ID={player_id}）は別グループに属しています。"})
            continue
        existing = TournamentPlayer.query.filter_by(
            tournament_id=tournament.id, player_id=player_id
        ).first()
        if existing:
            errors.append({"index": i, "error": f"プレイヤー（ID={player_id}）はすでに登録されています。"})
            continue

        participant = TournamentPlayer(tournament_id=tournament.id, player_id=player.id)
        db.session.add(participant)
        added_participants.append(participant)

    # 有効なものが1件以上あればコミット
    if added_participants:
        db.session.commit()

    return {
        "tournament_id": tournament.id,
        "added_count": len(added_participants),
        "errors": errors,
        "participants": added_participants,
    }


# =========================================================
# 参加者削除
# =========================================================
def delete_participant(tournament_key: str, player_id: int):
    """大会参加者共有キーから削除"""
    link = get_share_link_by_key(tournament_key)
    if not link or link.resource_type != "tournament":
        raise ServicePermissionError("不正な共有リンクです。")

    participant = TournamentPlayer.query.filter_by(player_id=player_id, tournament_id=link.resource_id).first()
    if not participant:
        raise ServiceNotFoundError("大会参加者が見つかりません。")

    _ensure_access(link, AccessLevel.EDIT, "大会参加者を削除する権限がありません。")

    db.session.delete(participant)
    db.session.commit()
