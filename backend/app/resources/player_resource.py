from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.player_schema import (
    PlayerCreateSchema,
    PlayerQuerySchema,
    PlayerSchema,
    PlayerUpdateSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.player_service import PlayerService


player_bp = Blueprint(
    "Players",
    __name__,
    url_prefix="/api/players",
    description="Player operations",
)


@player_bp.route("")
class PlayerListResource(MethodView):
    @player_bp.arguments(PlayerQuerySchema, location="query")
    @player_bp.response(200, PlayerSchema(many=True))
    @with_common_error_responses(player_bp)
    def get(self, query_args):
        short_key = query_args["short_key"]
        try:
            return PlayerService.list_by_group_short_key(short_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.arguments(PlayerQuerySchema, location="query")
    @player_bp.arguments(PlayerCreateSchema)
    @player_bp.response(201, PlayerSchema)
    @with_common_error_responses(player_bp)
    def post(self, query_args, new_data):
        short_key = query_args["short_key"]
        print("DATA", short_key, new_data)
        try:
            return PlayerService.create_player(new_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)


@player_bp.route("/<int:player_id>")
class PlayerResource(MethodView):
    @player_bp.arguments(PlayerQuerySchema, location="query")
    @player_bp.response(200, PlayerSchema)
    @with_common_error_responses(player_bp)
    def get(self, query_args, player_id):
        short_key = query_args["short_key"]
        try:
            return PlayerService.get_player(player_id, short_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.arguments(PlayerQuerySchema, location="query")
    @player_bp.arguments(PlayerUpdateSchema)
    @player_bp.response(200, PlayerSchema)
    @with_common_error_responses(player_bp)
    def put(self, query_args, update_data, player_id):
        short_key = query_args["short_key"]
        try:
            return PlayerService.update_player(player_id, update_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @player_bp.arguments(PlayerQuerySchema, location="query")
    @player_bp.response(200, MessageSchema)
    @with_common_error_responses(player_bp)
    def delete(self, query_args, player_id):
        short_key = query_args["short_key"]
        try:
            PlayerService.delete_player(player_id, short_key)
            return {"message": "Player deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
