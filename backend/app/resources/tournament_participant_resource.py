# app/resources/tournament_participant_resource.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.tournament_participant_schema import (
    TournamentParticipantCreateSchema,
    TournamentParticipantSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.tournament_participant_service import (
    list_participants_by_key,
    create_participant,
    delete_participant,
)

tournament_participant_bp = Blueprint(
    "tournament_participants",
    __name__,
    url_prefix="/api/tournaments",
    description="大会参加者管理API",
)


# =========================================================
# 大会参加者作成・一覧
# =========================================================
@tournament_participant_bp.route("/<string:tournament_key>/participants")
class TournamentParticipantListResource(MethodView):
    """GET: 大会参加者一覧 / POST: プレイヤー登録"""

    @tournament_participant_bp.response(200, TournamentParticipantSchema(many=True))
    @with_common_error_responses(tournament_participant_bp)
    def get(self, tournament_key):
        """大会共有キーから参加者一覧を取得"""
        try:
            return list_participants_by_key(tournament_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @tournament_participant_bp.arguments(TournamentParticipantCreateSchema)
    @tournament_participant_bp.response(201, TournamentParticipantSchema)
    @with_common_error_responses(tournament_participant_bp)
    def post(self, new_data, tournament_key):
        """大会共有キーからプレイヤーを登録"""
        try:
            return create_participant(tournament_key, new_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)


# =========================================================
# 大会参加者削除
# =========================================================
@tournament_participant_bp.route("/<string:tournament_key>/participants/<int:participant_id>")
class TournamentParticipantResource(MethodView):
    """DELETE: 大会参加者削除"""

    @tournament_participant_bp.response(200, MessageSchema)
    @with_common_error_responses(tournament_participant_bp)
    def delete(self, tournament_key, participant_id):
        """参加者共有キーから削除"""
        try:
            delete_participant(tournament_key, participant_id)
            return {"message": "Tournament participant deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
