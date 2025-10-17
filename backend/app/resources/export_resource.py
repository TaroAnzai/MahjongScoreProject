from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.export_schema import TournamentExportSchema, GroupSummarySchema,PlayerScoreMapSchema
from app.service_errors import ServiceNotFoundError, ServicePermissionError
from app.services.export_service import get_tournament_export, get_group_summary

# Blueprint
export_bp = Blueprint(
    "exports",
    __name__,
    url_prefix="/api",
    description="成績出力API",
)


# =========================================================
# 大会単位の成績出力
# =========================================================
@export_bp.route("/tournaments/<string:tournament_key>/export")
class TournamentExportResource(MethodView):
    """GET: 大会単位のスコア集計結果を取得"""

    @export_bp.response(200, TournamentExportSchema)
    @with_common_error_responses(export_bp)
    def get(self, tournament_key):
        """大会キーからスコア集計を取得"""
        try:
            return get_tournament_export(tournament_key)
        except (ServiceNotFoundError, ServicePermissionError) as e:
            abort(e.status_code, message=e.message)


# =========================================================
# グループ単位の成績サマリー
# =========================================================
@export_bp.route("/groups/<string:group_key>/summary")
class GroupSummaryResource(MethodView):
    """GET: グループ単位の大会成績サマリーを取得"""

    @export_bp.response(200, GroupSummarySchema)
    @with_common_error_responses(export_bp)
    def get(self, group_key):
        """グループキーから大会サマリーを取得"""
        try:
            return get_group_summary(group_key)
        except (ServiceNotFoundError, ServicePermissionError) as e:
            abort(e.status_code, message=e.message)

# =========================================================
# 大会成績（scoreMap形式）
# =========================================================
@export_bp.route("/tournaments/<string:tournament_key>/score_map")
class TournamentScoreMapResource(MethodView):
    """GET: プレイヤーごとの卓別スコアを返す"""

    @export_bp.response(200, PlayerScoreMapSchema)
    @with_common_error_responses(export_bp)
    def get(self, tournament_key):
        from app.services.export_service import get_tournament_score_map
        try:
            result = get_tournament_score_map(tournament_key)
            return {"score_map": result}
        except ServiceNotFoundError as e:
            abort(e.status_code, message=e.message)
