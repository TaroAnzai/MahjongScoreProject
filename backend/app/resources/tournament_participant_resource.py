# app/resources/tournament_participant_resource.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.tournament_participant_schema import (
    TournamentParticipantCreateSchema,
    TournamentParticipantQuerySchema,
    TournamentParticipantSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.tournament_participant_service import TournamentParticipantService


tournament_participant_bp = Blueprint(
    "TournamentParticipants",
    __name__,
    url_prefix="/api/tournaments/<int:tournament_id>/participants",
    description="Tournament participant operations",
)


@tournament_participant_bp.route("")
class TournamentParticipantListResource(MethodView):
    @tournament_participant_bp.arguments(TournamentParticipantQuerySchema, location="query")
    @tournament_participant_bp.response(200, TournamentParticipantSchema(many=True))
    @with_common_error_responses(tournament_participant_bp)
    def get(self, query_args, tournament_id):
        """大会の参加者一覧を取得"""
        short_key = query_args["short_key"]
        try:
            return TournamentParticipantService.list_by_tournament(short_key, tournament_id)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @tournament_participant_bp.arguments(TournamentParticipantQuerySchema, location="query")
    @tournament_participant_bp.arguments(TournamentParticipantCreateSchema)
    @tournament_participant_bp.response(201, TournamentParticipantSchema)
    @with_common_error_responses(tournament_participant_bp)
    def post(self, query_args, new_data, tournament_id):
        """大会にプレイヤーを登録"""
        short_key = query_args["short_key"]
        try:
            return TournamentParticipantService.create(short_key, tournament_id, new_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)


@tournament_participant_bp.route("/<int:participant_id>")
class TournamentParticipantResource(MethodView):
    @tournament_participant_bp.arguments(TournamentParticipantQuerySchema, location="query")
    @tournament_participant_bp.response(200, MessageSchema)
    @with_common_error_responses(tournament_participant_bp)
    def delete(self, query_args, tournament_id, participant_id):
        """大会参加者を削除"""
        short_key = query_args["short_key"]
        try:
            TournamentParticipantService.delete(short_key, tournament_id, participant_id)
            return {"message": "Tournament participant deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
