# app/services/table_player_service.py

from app import db
from app.models import AccessLevel, Table, TablePlayer, TournamentPlayer, Tournament, Player
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
    table_player = TablePlayer.query.filter_by(table_id=table.id).all()
    player_ids = [t.player_id for t in table_player]
    result = {
        'table_key' : table_key,
        'table_players' :  Player.query.filter(Player.id.in_(player_ids)).all()
    }
    return result


# =========================================================
# 卓参加者追加
# =========================================================
def create_table_player(table_key: str, data: dict):
    """卓共有キーから大会参加者を複数登録"""
    link, table = _require_table(table_key)
    _ensure_access(link, AccessLevel.EDIT, "卓に参加者を追加する権限がありません。")

    players_data = data.get("players")
    if not players_data or not isinstance(players_data, list):
        raise ServiceValidationError("players は1件以上のリストで指定してください。")

    # 卓が属する大会を取得
    tournament = Tournament.query.get(table.tournament_id)
    if not tournament:
        raise ServiceNotFoundError("対応する大会が見つかりません。")

    created_players = []
    errors = []

    for i,player_data in enumerate(players_data):
        player_id = player_data.get("player_id")
        if not player_id:
            errors.append(f"Data{i + 1}:player_id は必須です。")
            continue

        # 大会内の参加者として存在するかを確認
        participant = (
            TournamentPlayer.query
            .filter_by(tournament_id=tournament.id, player_id=player_id)
            .first()
        )
        if not participant:
            errors.append(f"Data{i + 1}:プレイヤーID {player_id} はこの大会の参加者ではありません。")
            continue

        # すでに同じプレイヤーが卓に登録されていないか確認
        existing = TablePlayer.query.filter_by(
            table_id=table.id, player_id=player_id
        ).first()
        if existing:
            errors.append(f"Data{i + 1}:プレイヤーID {player_id} はすでに登録されています。")
            continue

        # 登録処理
        table_player = TablePlayer(
            table_id=table.id,
            player_id=player_id,
            seat_position=player_data.get("seat_position"),
        )
        db.session.add(table_player)
        player = Player.query.get(player_id)
        created_players.append(player)

    db.session.commit()
    result ={
        "table_key": table_key,
        "created_players": created_players,
        "errors": errors,
        }
    return result



# =========================================================
# 卓参加者削除
# =========================================================
def delete_table_player(table_key: str, player_id: int):
    """卓参加者共有キーから削除"""
    link = get_share_link_by_key(table_key)
    if not link or link.resource_type != "table":
        raise ServicePermissionError("不正な共有リンクです。")

    table_player = TablePlayer.query.filter_by(player_id=player_id, table_id=link.resource_id).first()
    if not table_player:
        raise ServiceNotFoundError("卓参加者が見つかりません。")

    _ensure_access(link, AccessLevel.EDIT, "卓参加者を削除する権限がありません。")

    db.session.delete(table_player)
    db.session.commit()
