from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.player_schema import (
    PlayerCreateSchema,
    PlayerUpdateSchema,
    PlayerSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
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
        try:
            return list_players_by_group_key(group_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.arguments(PlayerCreateSchema)
    @player_bp.response(201, PlayerSchema)
    @with_common_error_responses(player_bp)
    def post(self, new_data, group_key):
        """グループ共有キーからプレイヤー作成"""
        try:
            return create_player(new_data, group_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

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
        try:
            return get_player_by_key(group_key, player_id)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.arguments(PlayerUpdateSchema)
    @player_bp.response(200, PlayerSchema)
    @with_common_error_responses(player_bp)
    def put(self, update_data, group_key, player_id):
        """プレイヤー更新"""
        try:
            return update_player(group_key, player_id, update_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.response(200, MessageSchema)
    @with_common_error_responses(player_bp)
    def delete(self, group_key, player_id):
        """プレイヤー削除"""
        try:
            delete_player(group_key, player_id)
            return {"message": "Player deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
