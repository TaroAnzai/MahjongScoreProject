from app import db
from app.models import Group, Tournament, Table, Game, Player, Score, TournamentPlayer
from app.service_errors import ServiceNotFoundError
from app.utils.share_link_utils import get_share_link_by_key
from app.service_errors import ServiceNotFoundError
from sqlalchemy.orm import joinedload
from sqlalchemy import func, case
from datetime import datetime
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
    # tables = [{"id": t.id, "name": t.name} for t in tournament.tables]
    tables = tournament.tables

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



# =========================================================
# グループ内プレイヤーごとの成績出力
# =========================================================
def get_group_player_stats(group_key: str, start_date: str | None = None, end_date: str | None = None):
    """期間指定でグループ内プレイヤーごとの統計を取得（Tournament.started_at基準）"""
    group = _require_group(group_key)

    # --- 期間変換 ---
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except Exception:
            raise ServiceNotFoundError("start_dateの形式が不正です（YYYY-MM-DD）")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except Exception:
            raise ServiceNotFoundError("end_dateの形式が不正です（YYYY-MM-DD）")

    # --- ベースクエリ ---
    query = (
        db.session.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            func.count(func.distinct(TournamentPlayer.tournament_id)).label("tournament_count"),
            func.count(Score.id).label("game_count"),
            func.sum(case((Score.rank == 1, 1), else_=0)).label("rank1_count"),
            func.sum(case((Score.rank == 2, 1), else_=0)).label("rank2_count"),
            func.sum(case((Score.rank == 3, 1), else_=0)).label("rank3_count"),
            func.sum(case((Score.rank >= 4, 1), else_=0)).label("rank4_or_lower_count"),
            func.avg(Score.rank).label("average_rank"),
            func.coalesce(func.sum(Score.score), 0).label("total_score"),
            func.coalesce(func.sum(Score.total_score), 0).label("total_balance"),
        )
        .join(Score, Score.player_id == Player.id)
        .join(Game, Game.id == Score.game_id)
        .join(Table, Table.id == Game.table_id)
        .join(Tournament, Tournament.id == Table.tournament_id)
        .join(TournamentPlayer, TournamentPlayer.player_id == Player.id)
        .filter(Player.group_id == group.id)
    )

    # --- 期間フィルタ（Tournament.started_atベース）---
    if start_dt:
        query = query.filter(Tournament.started_at >= start_dt)
    if end_dt:
        query = query.filter(Tournament.started_at <= end_dt)

    query = query.group_by(Player.id)

    players = []
    for r in query.all():
        players.append({
            "player_id": r.player_id,
            "player_name": r.player_name,
            "tournament_count": r.tournament_count or 0,
            "game_count": r.game_count or 0,
            "rank1_count": r.rank1_count or 0,
            "rank2_count": r.rank2_count or 0,
            "rank3_count": r.rank3_count or 0,
            "rank4_or_lower_count": r.rank4_or_lower_count or 0,
            "average_rank": round(r.average_rank or 0, 2),
            "total_score": round(r.total_score or 0, 1),
            "total_balance": round(r.total_balance or 0, 1),
        })

    return {
        "group": {"id": group.id, "name": group.name},
        "period": {"start": start_date or None, "end": end_date or None},
        "players": players,
    }
