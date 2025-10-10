from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.table_schema import (
    TableUpdateSchema,
    TableSchema,
)
from app.schemas.game_schema import GameSchema, GameCreateSchema
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.table_service import (
    get_table_by_key,
    update_table,
    delete_table,
)
from app.services.game_service import create_game, get_games_by_table

# ✅ Blueprint設定
table_bp = Blueprint(
    "tables",
    __name__,
    url_prefix="/api/tables",
    description="卓管理API",
)


# =========================================================
# 卓単体操作
# =========================================================
@table_bp.route("/<string:table_key>")
class TableByKeyResource(MethodView):
    """GET / PUT / DELETE: 卓単体操作"""

    @table_bp.response(200, TableSchema)
    @with_common_error_responses(table_bp)
    def get(self, table_key):
        """卓詳細取得"""
        try:
            return get_table_by_key(table_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @table_bp.arguments(TableUpdateSchema)
    @table_bp.response(200, TableSchema)
    @with_common_error_responses(table_bp)
    def put(self, update_data, table_key):
        """卓更新"""
        try:
            return update_table(table_key, update_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @table_bp.response(200, MessageSchema)
    @with_common_error_responses(table_bp)
    def delete(self, table_key):
        """卓削除"""
        try:
            delete_table(table_key)
            return {"message": "Table deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

# =========================================================
# 対局作成
# =========================================================
@table_bp.route("/<string:table_key>/games")
class GameCreateResource(MethodView):
    """GET / POST: 指定卓内の対局一覧・作成"""

    @table_bp.arguments(GameCreateSchema)
    @table_bp.response(201, GameSchema)
    @with_common_error_responses(table_bp)
    def post(self, new_data, table_key):
        """卓共有キーから対局を作成"""
        try:
            return create_game(new_data, table_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @table_bp.response(200, GameSchema(many=True))
    @with_common_error_responses(table_bp)
    def get(self, table_key):
        """卓キーから対局一覧を取得"""
        try:
            return get_games_by_table(table_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
