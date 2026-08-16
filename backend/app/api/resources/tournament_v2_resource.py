"""V2 tournament endpoints."""
from flask import jsonify, request
from flask_smorest import Blueprint

from app import db
from app.api.schemas.v2_schema import ParticipantBatchAddSchema
from app.api.services.v2_service import (
    V2Error, batch_add_participants, delete_participant, tournament_dashboard,
)


tournament_v2_bp = Blueprint(
    "tournaments_v2", __name__, url_prefix="/api/v2/tournaments",
    description="V2 tournament API",
)


@tournament_v2_bp.errorhandler(V2Error)
def handle_v2_error(error):
    db.session.rollback()
    body = {"code": error.code, "message": error.message}
    if error.details is not None:
        body["details"] = error.details
    return jsonify(body), error.status


@tournament_v2_bp.route("/<string:tournament_key>/participants:batch-add", methods=["POST"])
@tournament_v2_bp.arguments(ParticipantBatchAddSchema)
def batch_add_participants_v2(payload, tournament_key):
    body, status = batch_add_participants(
        tournament_key, payload, request.headers.get("Idempotency-Key")
    )
    return jsonify(body), status


@tournament_v2_bp.route("/<string:tournament_key>/participants/<int:player_id>", methods=["DELETE"])
def delete_participant_v2(tournament_key, player_id):
    body, status = delete_participant(
        tournament_key, player_id, request.args.get("propagate_to"),
        request.headers.get("Idempotency-Key"),
    )
    return jsonify(body), status


@tournament_v2_bp.route("/<string:tournament_key>/dashboard", methods=["GET"])
def tournament_dashboard_v2(tournament_key):
    return jsonify(tournament_dashboard(tournament_key))
