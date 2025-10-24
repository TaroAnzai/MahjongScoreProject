from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.game_schema import GameCreateSchema, GameUpdateSchema, GameSchema
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.game_service import (
    create_game,
    get_game_by_key,
    update_game,
    delete_game,
)

# ✅ Blueprint設定
game_bp = Blueprint(
    "games",
    __name__,
    url_prefix="/api/tables/<string:table_key>/games",
    description="対局管理API",
)



# =========================================================
# 対局単体操作
# =========================================================
@game_bp.route("/<int:game_id>")
class GameByKeyResource(MethodView):
    """GET / PUT / DELETE: 対局単体操作"""

    @game_bp.response(200, GameSchema)
    @with_common_error_responses(game_bp)
    def get(self, table_key, game_id):
        """対局詳細取得"""
        try:
            return get_game_by_key(table_key, game_id)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @game_bp.arguments(GameUpdateSchema)
    @game_bp.response(200, GameSchema)
    @with_common_error_responses(game_bp)
    def put(self, update_data, table_key, game_id):
        """対局更新"""
        try:
            return update_game(table_key, game_id, update_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @game_bp.response(200, MessageSchema)
    @with_common_error_responses(game_bp)
    def delete(self, table_key, game_id):
        """対局削除"""
        try:
            delete_game(table_key, game_id)
            return {"message": "Game deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
