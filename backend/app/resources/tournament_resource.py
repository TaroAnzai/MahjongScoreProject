from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.tournament_schema import (
    TournamentCreateSchema,
    TournamentQuerySchema,
    TournamentSchema,
    TournamentUpdateSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.tournament_service import TournamentService


tournament_bp = Blueprint(
    "Tournaments",
    __name__,
    url_prefix="/api/tournaments",
    description="Tournament operations",
)


@tournament_bp.route("")
class TournamentListResource(MethodView):
    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.response(200, TournamentSchema(many=True))
    @with_common_error_responses(tournament_bp)
    def get(self, query_args):
        short_key = query_args["short_key"]
        try:
            return TournamentService.list_by_group_short_key(short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.arguments(TournamentCreateSchema)
    @tournament_bp.response(201, TournamentSchema)
    @with_common_error_responses(tournament_bp)
    def post(self, query_args, new_data):
        short_key = query_args["short_key"]
        try:
            return TournamentService.create_tournament(new_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)


@tournament_bp.route("/<int:tournament_id>")
class TournamentResource(MethodView):
    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.response(200, TournamentSchema)
    @with_common_error_responses(tournament_bp)
    def get(self, query_args, tournament_id):
        short_key = query_args["short_key"]
        try:
            return TournamentService.get_tournament(tournament_id, short_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.arguments(TournamentUpdateSchema)
    @tournament_bp.response(200, TournamentSchema)
    @with_common_error_responses(tournament_bp)
    def put(self, query_args, update_data, tournament_id):
        short_key = query_args["short_key"]
        try:
            return TournamentService.update_tournament(tournament_id, update_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.response(200, MessageSchema)
    @with_common_error_responses(tournament_bp)
    def delete(self, query_args, tournament_id):
        short_key = query_args["short_key"]
        try:
            TournamentService.delete_tournament(tournament_id, short_key)
            return {"message": "Tournament deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
