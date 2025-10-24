# app/resources/table_player_resource.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.table_player_schema import TablePlayerCreateSchema, TablePlayersSchema
from app.service_errors import ServiceError
from flask import jsonify
from app.service_errors import format_error_response
from app.services.table_player_service import (
    list_table_players_by_key,
    create_table_player,
    delete_table_player,
)

table_player_bp = Blueprint(
    "table_players",
    __name__,
    url_prefix="/api/tables",
    description="卓参加者管理API",
)

@table_player_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code

# =========================================================
# 卓参加者一覧・作成
# =========================================================
@table_player_bp.route("/<string:table_key>/players")
class TablePlayerListResource(MethodView):
    """GET: 卓参加者一覧 / POST: 卓に参加者追加"""

    @table_player_bp.response(200, TablePlayersSchema)
    @with_common_error_responses(table_player_bp)
    def get(self, table_key):
        """卓共有キーから参加者一覧を取得"""
        return list_table_players_by_key(table_key)


    @table_player_bp.arguments(TablePlayerCreateSchema)
    @table_player_bp.response(201, TablePlayersSchema)
    @with_common_error_responses(table_player_bp)
    def post(self, new_data, table_key):
        """卓共有キーから大会参加者を登録"""
        return create_table_player(table_key, new_data)


# =========================================================
# 卓参加者削除
# =========================================================
@table_player_bp.route("/<string:table_key>/players/<int:player_id>")
class TablePlayerResource(MethodView):
    """DELETE: 卓参加者削除"""

    @table_player_bp.response(200, MessageSchema)
    @with_common_error_responses(table_player_bp)
    def delete(self, table_key, player_id):
        """卓参加者共有キーから削除"""
        delete_table_player(table_key, player_id)
        return {"message": "Table player deleted"}
