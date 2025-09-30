# app/resources/export_resource.py
from flask_smorest import Blueprint
from app.schemas.export_schema import TournamentResultSchema, ScoreSummarySchema
from app.services.export_service import ExportService

blp = Blueprint("Export", "export", url_prefix="/api/export", description="スコアエクスポート API")

@blp.route("/tournament/<int:tournament_id>")
class ExportTournamentResultsResource:
    @blp.response(200, TournamentResultSchema)
    def get(self, tournament_id):
        """大会単位のスコア集計結果を返す"""
        return ExportService.export_tournament_results(tournament_id)

@blp.route("/tournament/<int:tournament_id>/summary")
class ExportScoreSummaryResource:
    @blp.response(200, ScoreSummarySchema)
    def get(self, tournament_id):
        """卓ごとのクロステーブル用スコアを返す"""
        return ExportService.export_score_summary(tournament_id)
