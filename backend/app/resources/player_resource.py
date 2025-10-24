from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.player_schema import (
    PlayerCreateSchema,
    PlayerUpdateSchema,
    PlayerSchema,
)
from app.service_errors import ServiceError
from flask import jsonify
from app.service_errors import format_error_response

from app.services.player_service import (
    create_player,
    list_players_by_group_key,
    get_player_by_key,
    update_player,
    delete_player,
)

player_bp = Blueprint(
    "players",
    __name__,
    url_prefix="/api/groups/<string:group_key>/players",
    description="プレイヤー管理API",
)
@player_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code
# =========================================================
# プレイヤー一覧・作成
# =========================================================
@player_bp.route("")
class PlayerListResource(MethodView):
    """GET: プレイヤー一覧 / POST: プレイヤー作成"""

    @player_bp.response(200, PlayerSchema(many=True))
    @with_common_error_responses(player_bp)
    def get(self, group_key):
        """グループ共有キーからプレイヤー一覧を取得"""
        return list_players_by_group_key(group_key)


    @player_bp.arguments(PlayerCreateSchema)
    @player_bp.response(201, PlayerSchema)
    @with_common_error_responses(player_bp)
    def post(self, new_data, group_key):
        """グループ共有キーからプレイヤー作成"""
        return create_player(new_data, group_key)


# =========================================================
# プレイヤー単体操作
# =========================================================
@player_bp.route("/<int:player_id>")
class PlayerByKeyResource(MethodView):
    """GET / PUT / DELETE: プレイヤー単体操作"""

    @player_bp.response(200, PlayerSchema)
    @with_common_error_responses(player_bp)
    def get(self, group_key, player_id):
        """プレイヤー詳細取得"""
        return get_player_by_key(group_key, player_id)


    @player_bp.arguments(PlayerUpdateSchema)
    @player_bp.response(200, PlayerSchema)
    @with_common_error_responses(player_bp)
    def put(self, update_data, group_key, player_id):
        """プレイヤー更新"""
        return update_player(group_key, player_id, update_data)


    @player_bp.response(200, MessageSchema)
    @with_common_error_responses(player_bp)
    def delete(self, group_key, player_id):
        """プレイヤー削除"""
        delete_player(group_key, player_id)
        return {"message": "Player deleted"}

