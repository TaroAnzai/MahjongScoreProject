from app import db
from app.models import Group, Tournament, Table, Game, Player, Score, TournamentPlayer
from app.service_errors import ServiceNotFoundError
from app.utils.share_link_utils import get_share_link_by_key
from app.service_errors import ServiceNotFoundError
from sqlalchemy.orm import joinedload

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

def get_tournament_score_map(tournament_key: str):
    """大会単位のスコアマップを生成"""

    link = get_share_link_by_key(tournament_key)
    if not link or link.resource_type != "tournament":
        raise ServiceNotFoundError("大会が見つかりません。")

    tournament = Tournament.query.options(
        joinedload(Tournament.tables).joinedload(Table.games).joinedload(Game.scores)
    ).get(link.resource_id)
    if not tournament:
        raise ServiceNotFoundError("大会が存在しません。")

    rate = tournament.rate if tournament.rate else 0.001
    # --- 全テーブル一覧 ---
    tables = [{"id": t.id, "name": t.name} for t in tournament.tables]

    # --- プレイヤー初期辞書 ---
    player_map = {}
    for participant in tournament.participants:
        p = participant.player
        player_map[p.id] = {
            "id": p.id,
            "name": p.name,
            "scores": {},   # table_idごとのスコア
            "total": 0,
            "converted_total": 0,
        }

    # --- 各テーブルのスコアを集計 ---
    for table in tournament.tables:
        for game in table.games:
            for s in game.scores:
                if s.player_id not in player_map:
                    continue
                player_map[s.player_id]["scores"][str(table.id)] = \
                    player_map[s.player_id]["scores"].get(str(table.id), 0) + s.score

    # --- 合計と換算を計算 ---
    for p in player_map.values():
        total = sum(p["scores"].values())
        p["total"] = total
        p["converted_total"] = round(total * rate, 2)

    return {
        "tournament_id": tournament.id,
        "tables": tables,
        "players": list(player_map.values()),
        "rate": rate,
    }
