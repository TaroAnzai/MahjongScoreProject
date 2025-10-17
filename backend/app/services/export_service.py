from app import db
from app.models import Group, Tournament, Table, Game, Player, Score, TournamentPlayer
from app.service_errors import ServiceNotFoundError
from app.utils.share_link_utils import get_share_link_by_key
from app.service_errors import ServiceNotFoundError


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
    """
    プレイヤーごとのスコア詳細を集計し、
    {
        player_id: {
            table_<table.id>: 合計スコア,
            total: 大会合計スコア,
            games_played: 対局数
        }, ...
    }
    の形式で返す。
    """
    # --- 大会キー確認 ---
    link = get_share_link_by_key(tournament_key)
    if not link or link.resource_type != "tournament":
        raise ServiceNotFoundError("大会が見つかりません。")

    tournament = Tournament.query.get(link.resource_id)
    if not tournament:
        raise ServiceNotFoundError("大会が存在しません。")

    score_map = {}

    # --- 大会に含まれる卓を取得 ---
    tables = Table.query.filter_by(tournament_id=tournament.id).all()
    for table in tables:
        games = Game.query.filter_by(table_id=table.id).all()
        for game in games:
            scores = Score.query.filter_by(game_id=game.id).all()
            for s in scores:
                pid = s.player_id
                score_map.setdefault(pid, {})
                key = f"table_{table.id}"
                score_map[pid][key] = score_map[pid].get(key, 0) + s.score

    # --- プレイヤーごとの合計スコアと対局数を追加 ---
    players = (
        db.session.query(Player)
        .join(TournamentPlayer, Player.id == TournamentPlayer.player_id)
        .filter(TournamentPlayer.tournament_id == tournament.id)
        .all()
    )

    for p in players:
        # 合計スコア計算
        player_scores = (
            db.session.query(Score)
            .join(Game, Score.game_id == Game.id)
            .join(Table, Game.table_id == Table.id)
            .filter(Table.tournament_id == tournament.id, Score.player_id == p.id)
            .all()
        )
        total = sum(s.score for s in player_scores)
        score_map.setdefault(p.id, {})
        score_map[p.id]["total"] = total
        score_map[p.id]["games_played"] = len(player_scores)
    print("In service get_tournament_score_map:", score_map)
    return score_map
