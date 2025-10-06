from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.game_schema import (
    GameCreateSchema,
    GameQuerySchema,
    GameSchema,
    GameUpdateSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.game_service import GameService


game_bp = Blueprint(
    "Games",
    __name__,
    url_prefix="/api/games",
    description="Game operations",
)


@game_bp.route("")
class GameListResource(MethodView):
    @game_bp.arguments(GameQuerySchema, location="query")
    @game_bp.response(200, GameSchema(many=True))
    @with_common_error_responses(game_bp)
    def get(self, query_args):
        short_key = query_args["short_key"]
        try:
            return GameService.list_by_table_short_key(short_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @game_bp.arguments(GameQuerySchema, location="query")
    @game_bp.arguments(GameCreateSchema)
    @game_bp.response(201, GameSchema)
    @with_common_error_responses(game_bp)
    def post(self, query_args, new_data):
        short_key = query_args["short_key"]
        try:
            return GameService.create_game(new_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)


@game_bp.route("/<int:game_id>")
class GameResource(MethodView):
    @game_bp.arguments(GameQuerySchema, location="query")
    @game_bp.response(200, GameSchema)
    @with_common_error_responses(game_bp)
    def get(self, query_args, game_id):
        short_key = query_args["short_key"]
        try:
            return GameService.get_game(game_id, short_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @game_bp.arguments(GameQuerySchema, location="query")
    @game_bp.arguments(GameUpdateSchema)
    @game_bp.response(200, GameSchema)
    @with_common_error_responses(game_bp)
    def put(self, query_args, update_data, game_id):
        short_key = query_args["short_key"]
        try:
            return GameService.update_game(game_id, update_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @game_bp.arguments(GameQuerySchema, location="query")
    @game_bp.response(200, MessageSchema)
    @with_common_error_responses(game_bp)
    def delete(self, query_args, game_id):
        short_key = query_args["short_key"]
        try:
            GameService.delete_game(game_id, short_key)
            return {"message": "Game deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
