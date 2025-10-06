from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.table_schema import (
    TableCreateSchema,
    TableQuerySchema,
    TableSchema,
    TableUpdateSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.table_service import TableService


table_bp = Blueprint(
    "Tables",
    __name__,
    url_prefix="/api/tables",
    description="Table operations",
)


@table_bp.route("")
class TableListResource(MethodView):
    @table_bp.arguments(TableQuerySchema, location="query")
    @table_bp.response(200, TableSchema(many=True))
    @with_common_error_responses(table_bp)
    def get(self, query_args):
        short_key = query_args["short_key"]
        try:
            return TableService.list_by_tournament_short_key(short_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @table_bp.arguments(TableQuerySchema, location="query")
    @table_bp.arguments(TableCreateSchema)
    @table_bp.response(201, TableSchema)
    @with_common_error_responses(table_bp)
    def post(self, query_args, new_data):
        short_key = query_args["short_key"]
        try:
            return TableService.create_table(new_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)


@table_bp.route("/<int:table_id>")
class TableResource(MethodView):
    @table_bp.arguments(TableQuerySchema, location="query")
    @table_bp.response(200, TableSchema)
    @with_common_error_responses(table_bp)
    def get(self, query_args, table_id):
        short_key = query_args["short_key"]
        try:
            return TableService.get_table(table_id, short_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @table_bp.arguments(TableQuerySchema, location="query")
    @table_bp.arguments(TableUpdateSchema)
    @table_bp.response(200, TableSchema)
    @with_common_error_responses(table_bp)
    def put(self, query_args, update_data, table_id):
        short_key = query_args["short_key"]
        try:
            return TableService.update_table(table_id, update_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @table_bp.arguments(TableQuerySchema, location="query")
    @table_bp.response(200, MessageSchema)
    @with_common_error_responses(table_bp)
    def delete(self, query_args, table_id):
        short_key = query_args["short_key"]
        try:
            TableService.delete_table(table_id, short_key)
            return {"message": "Table deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
