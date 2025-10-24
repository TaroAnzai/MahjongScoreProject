# app/resources/tournament_participant_resource.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.tournament_participant_schema import (
    TournamentParticipantsCreateSchema,
    TournamentParticipantsSchema,
)
from app.service_errors import ServiceError
from flask import jsonify
from app.service_errors import format_error_response
from app.services.tournament_participant_service import (
    list_participants_by_key,
    create_participants,
    delete_participant,
)

tournament_participant_bp = Blueprint(
    "tournament_participants",
    __name__,
    url_prefix="/api/tournaments",
    description="大会参加者管理API",
)

@tournament_participant_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code

# =========================================================
# 大会参加者作成・一覧
# =========================================================
@tournament_participant_bp.route("/<string:tournament_key>/participants")
class TournamentParticipantListResource(MethodView):
    """GET: 大会参加者一覧 / POST: プレイヤー登録"""

    @tournament_participant_bp.response(200, TournamentParticipantsSchema)
    @with_common_error_responses(tournament_participant_bp)
    def get(self, tournament_key):
        """大会共有キーから参加者一覧を取得"""
        return list_participants_by_key(tournament_key)

    @tournament_participant_bp.arguments(TournamentParticipantsCreateSchema)
    @tournament_participant_bp.response(201, TournamentParticipantsSchema)
    @with_common_error_responses(tournament_participant_bp)
    def post(self, new_data, tournament_key):
        """大会共有キーからプレイヤーを登録"""
        return create_participants(tournament_key, new_data)


# =========================================================
# 大会参加者削除
# =========================================================
@tournament_participant_bp.route("/<string:tournament_key>/participants/<int:player_id>")
class TournamentParticipantResource(MethodView):
    """DELETE: 大会参加者削除"""

    @tournament_participant_bp.response(200, MessageSchema)
    @with_common_error_responses(tournament_participant_bp)
    def delete(self, tournament_key, player_id):
        """参加者共有キーから削除"""
        delete_participant(tournament_key, player_id)
        return {"message": "Tournament participant deleted"}
