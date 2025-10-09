# app/resources/table_player_resource.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.table_player_schema import (
    TablePlayerCreateSchema,
    TablePlayerQuerySchema,
    TablePlayerSchema,
)
from app.services.table_player_service import TablePlayerService
from app.service_errors import ServiceNotFoundError, ServicePermissionError, ServiceValidationError

table_player_bp = Blueprint(
    "TablePlayers",
    __name__,
    url_prefix="/api/tables/<int:table_id>/players",
    description="Table player operations",
)


@table_player_bp.route("")
class TablePlayerListResource(MethodView):
    @table_player_bp.arguments(TablePlayerQuerySchema, location="query")
    @table_player_bp.response(200, TablePlayerSchema(many=True))
    @with_common_error_responses(table_player_bp)
    def get(self, query_args, table_id):
        """卓の参加者一覧を取得"""
        short_key = query_args["short_key"]
        try:
            return TablePlayerService.list_by_table(short_key, table_id)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @table_player_bp.arguments(TablePlayerCreateSchema)
    @table_player_bp.arguments(TablePlayerQuerySchema, location="query")
    @table_player_bp.response(201, TablePlayerSchema)
    @with_common_error_responses(table_player_bp)
    def post(self, new_data, query_args, table_id):
        """卓に大会参加者を登録"""
        short_key = query_args["short_key"]
        try:
            return TablePlayerService.create(short_key, table_id, new_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)


@table_player_bp.route("/<int:table_player_id>")
class TablePlayerResource(MethodView):
    @table_player_bp.arguments(TablePlayerQuerySchema, location="query")
    @table_player_bp.response(200, MessageSchema)
    @with_common_error_responses(table_player_bp)
    def delete(self, query_args, table_id, table_player_id):
        """卓から参加者を削除"""
        short_key = query_args["short_key"]
        try:
            TablePlayerService.delete(short_key, table_id, table_player_id)
            return {"message": "Table player deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
