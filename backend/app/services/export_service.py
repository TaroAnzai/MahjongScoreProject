from app import db
from app.models import Group, Tournament, Table, Game, Player, Score, TournamentPlayer
from app.service_errors import ServiceNotFoundError
from app.utils.share_link_utils import get_share_link_by_key


# =========================================================
# 内部ユーティリティ
# =========================================================
def _require_tournament(short_key: str):
    link = get_share_link_by_key(short_key)
    if not link or link.resource_type != "tournament":
        raise ServiceNotFoundError("大会が見つかりません。")
    tournament = Tournament.query.get(link.resource_id)
    if not tournament:
        raise ServiceNotFoundError("大会が存在しません。")
    return tournament


def _require_group(short_key: str):
    link = get_share_link_by_key(short_key)
    if not link or link.resource_type != "group":
        raise ServiceNotFoundError("グループが見つかりません。")
    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("グループが存在しません。")
    return group


# =========================================================
# 大会単位の成績出力
# =========================================================
def get_tournament_export(tournament_key: str):
    """大会キーからスコア集計を取得"""
    tournament = _require_tournament(tournament_key)

    players = (
        db.session.query(Player)
        .join(TournamentPlayer, Player.id == TournamentPlayer.player_id)
        .filter(TournamentPlayer.tournament_id == tournament.id)
        .all()
    )

    player_results = []
    for p in players:
        scores = (
            db.session.query(Score)
            .join(Game, Score.game_id == Game.id)
            .join(Table, Game.table_id == Table.id)
            .filter(Table.tournament_id == tournament.id, Score.player_id == p.id)
            .all()
        )
        total_score = sum([s.score for s in scores])
        player_results.append({
            "id": p.id,
            "name": p.name,
            "games_played": len(scores),
            "total_score": total_score,
        })

    return {
        "tournament": {"id": tournament.id, "name": tournament.name},
        "players": player_results,
    }


# =========================================================
# グループ単位の成績サマリー出力
# =========================================================
def get_group_summary(group_key: str):
    """グループキーから大会・スコアサマリーを取得"""
    group = _require_group(group_key)
    tournaments = Tournament.query.filter_by(group_id=group.id).all()

    result = {
        "group": {"id": group.id, "name": group.name},
        "tournaments": [],
    }

    for t in tournaments:
        t_data = get_tournament_export(
            next(
                (link.short_key for link in t.tournament_links if link.access_level.value == "VIEW"),
                None,
            )
        )
        result["tournaments"].append(t_data)

    return result
