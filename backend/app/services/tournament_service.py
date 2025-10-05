# app/services/tournament_service.py
from app import db
from app.models import Tournament, Group, ShareLink, AccessLevel
from app.utils.share_link_utils import get_share_link_by_key
from app.service_errors import (
    ServiceValidationError,
    ServicePermissionError,
    ServiceNotFoundError,
)


class TournamentService:
    # -------------------------------------------------
    # 内部ユーティリティ
    # -------------------------------------------------
    @staticmethod
    def _verify_group_access(group_id: int, short_key: str, require_edit: bool = False):
        """共有キーによるグループアクセス権限を確認"""
        link = get_share_link_by_key(short_key)
        if not link or link.resource_type != "group":
            raise ServicePermissionError("無効な共有リンクです。")

        group = Group.query.get_or_404(link.resource_id)
        if group.id != group_id:
            raise ServicePermissionError("共有リンクがこのグループに対応していません。")

        # 編集権限が必要な場合は作成者一致をチェック
        if require_edit and link.created_by != group.created_by:
            raise ServicePermissionError("このグループを編集する権限がありません。")

        return group

    # -------------------------------------------------
    # CRUD
    # -------------------------------------------------
    @staticmethod
    def get_tournaments_by_group(short_key: str):
        """共有キーで大会一覧を取得"""
        link = get_share_link_by_key(short_key)
        if not link or link.resource_type != "group":
            raise PermissionError("無効な共有リンクです。")
        group = Group.query.get_or_404(link.resource_id)
        return Tournament.query.filter_by(group_id=group.id).all()

    @staticmethod
    def get_tournament_by_id(tournament_id: int):
        """大会をIDで取得"""
        return Tournament.query.get_or_404(tournament_id)

    @staticmethod
    def create_tournament(data: dict, short_key: str):
        """大会を作成（要グループ編集権限）"""
        group_id = data.get("group_id")
        group = TournamentService._verify_group_access(group_id, short_key, require_edit=True)
        data["created_by"] = group.created_by
        tournament = Tournament(**data)
        db.session.add(tournament)
        db.session.commit()
        return tournament

    @staticmethod
    def delete_tournament(tournament_id: int, short_key: str):
        """大会削除（要グループ編集権限）"""
        tournament = Tournament.query.get_or_404(tournament_id)
        TournamentService._verify_group_access(
            tournament.group_id, short_key, require_edit=True
        )
        db.session.delete(tournament)
        db.session.commit()
        return True


# -------------------------------------------------
# ExportService（集計用）
# -------------------------------------------------
from app.models import Player, Table, Game, Score, TournamentPlayer


class ExportService:
    @staticmethod
    def export_tournament_results(tournament_id: int):
        """大会スコア結果をエクスポート"""
        tournament = Tournament.query.get_or_404(tournament_id)
        result = {
            "tournament": {"id": tournament.id, "name": tournament.name},
            "groups": [],
        }

        group = tournament.group
        if not group:
            return result

        group_data = {"id": group.id, "name": group.name, "players": []}

        players = (
            db.session.query(Player)
            .join(TournamentPlayer, Player.id == TournamentPlayer.player_id)
            .filter(TournamentPlayer.tournament_id == tournament.id)
            .all()
        )
        for player in players:
            scores = Score.query.filter_by(player_id=player.id).all()
            total_score = sum(s.score for s in scores)
            group_data["players"].append(
                {
                    "id": player.id,
                    "name": player.name,
                    "total_score": total_score,
                    "games_played": len(scores),
                }
            )

        result["groups"].append(group_data)
        return result

    @staticmethod
    def export_score_summary(tournament_id: int):
        """クロステーブル形式のスコア"""
        tournament = Tournament.query.get_or_404(tournament_id)
        players = Player.query.filter_by(tournament_id=tournament.id).order_by(Player.id).all()
        player_map = {p.id: p.name for p in players}

        tables = Table.query.filter_by(tournament_id=tournament.id).all()
        result = {
            "players": [{"id": pid, "name": pname} for pid, pname in player_map.items()],
            "tables": [],
        }

        for table in tables:
            table_data = {"name": table.name, "scores": {}}
            games = Game.query.filter_by(table_id=table.id).order_by(Game.id).all()
            for game in games:
                scores = Score.query.filter_by(game_id=game.id).all()
                for score in scores:
                    table_data["scores"][score.player_id] = (
                        table_data["scores"].get(score.player_id, 0) + score.score
                    )
            result["tables"].append(table_data)
        return result
