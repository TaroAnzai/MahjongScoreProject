# app/resources/export_resource.py
from flask_smorest import Blueprint
from flask.views import MethodView
from app.schemas.export_schema import TournamentResultSchema, ScoreSummarySchema
from app.services.export_service import ExportService

export_bp = Blueprint("Export", "export", url_prefix="/api/export", description="スコアエクスポート API")

@export_bp.route("/tournament/<int:tournament_id>")
class ExportTournamentResultsResource(MethodView):
    @export_bp.response(200, TournamentResultSchema)
    def get(self, tournament_id):
        """大会単位のスコア集計結果を返す"""
        return ExportService.export_tournament_results(tournament_id)

@export_bp.route("/tournament/<int:tournament_id>/summary")
class ExportScoreSummaryResource(MethodView):
    @export_bp.response(200, ScoreSummarySchema)
    def get(self, tournament_id):
        """卓ごとのクロステーブル用スコアを返す"""
        return ExportService.export_score_summary(tournament_id)
