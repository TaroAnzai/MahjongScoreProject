from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.player_schema import (
    PlayerUpdateSchema,
    PlayerSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.player_service import (
    get_player_by_key,
    update_player,
    delete_player,
)

player_bp = Blueprint(
    "players",
    __name__,
    url_prefix="/api/players",
    description="プレイヤー管理API",
)


# =========================================================
# プレイヤー単体操作
# =========================================================
@player_bp.route("/<string:player_key>")
class PlayerByKeyResource(MethodView):
    """GET / PUT / DELETE: プレイヤー単体操作"""

    @player_bp.response(200, PlayerSchema)
    @with_common_error_responses(player_bp)
    def get(self, player_key):
        """プレイヤー詳細取得"""
        try:
            return get_player_by_key(player_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.arguments(PlayerUpdateSchema)
    @player_bp.response(200, PlayerSchema)
    @with_common_error_responses(player_bp)
    def put(self, update_data, player_key):
        """プレイヤー更新"""
        try:
            return update_player(player_key, update_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.response(200, MessageSchema)
    @with_common_error_responses(player_bp)
    def delete(self, player_key):
        """プレイヤー削除"""
        try:
            delete_player(player_key)
            return {"message": "Player deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
