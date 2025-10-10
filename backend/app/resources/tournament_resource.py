from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.tournament_schema import (
    TournamentCreateSchema,
    TournamentUpdateSchema,
    TournamentSchema,
)
from app.schemas.table_schema import TableSchema, TableCreateSchema
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.tournament_service import (
    get_tournament_by_key,
    update_tournament,
    delete_tournament,
)
from app.services.table_service import create_table

# ✅ Blueprint設定を仕様書V2に準拠
tournament_bp = Blueprint(
    "tournaments",
    __name__,
    url_prefix="/api/tournaments",
    description="大会管理API",
)





# =========================================================
# 大会単体操作
# =========================================================
@tournament_bp.route("/<string:tournament_key>")
class TournamentByKeyResource(MethodView):
    """GET / PUT / DELETE: 大会単体操作"""

    @tournament_bp.response(200, TournamentSchema)
    @with_common_error_responses(tournament_bp)
    def get(self, tournament_key):
        """大会詳細取得"""
        try:
            return get_tournament_by_key(tournament_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @tournament_bp.arguments(TournamentUpdateSchema)
    @tournament_bp.response(200, TournamentSchema)
    @with_common_error_responses(tournament_bp)
    def put(self, update_data, tournament_key):
        """大会更新"""
        try:
            return update_tournament(tournament_key, update_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @tournament_bp.response(200, MessageSchema)
    @with_common_error_responses(tournament_bp)
    def delete(self, tournament_key):
        """大会削除"""
        try:
            delete_tournament(tournament_key)
            return {"message": "Tournament deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

# =========================================================
# 卓作成
# =========================================================
@tournament_bp.route("/<string:tournament_key>/tables")
class TableCreateResource(MethodView):
    """POST: 指定大会内に卓を作成"""

    @tournament_bp.arguments(TableCreateSchema)
    @tournament_bp.response(201, TableSchema)
    @with_common_error_responses(tournament_bp)
    def post(self, new_data, tournament_key):
        """大会共有キーから卓を作成"""
        try:
            return create_table(new_data, tournament_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
