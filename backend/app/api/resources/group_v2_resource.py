"""V2 group endpoints."""
from flask import jsonify, request
from flask_smorest import Blueprint

from app import db
from app.api.schemas.v2_schema import (
    GroupBatchGetSchema, StatusBatchRequestSchema, StatusBatchResponseSchema,
    TournamentCreateV2Schema,
)
from app.api.services.v2_service import (
    V2Error, batch_get_groups, batch_group_status, create_tournament_with_tables,
    group_dashboard,
)


group_v2_bp = Blueprint(
    "groups_v2", __name__, url_prefix="/api/v2", description="V2 group API"
)


@group_v2_bp.errorhandler(V2Error)
def handle_v2_error(error):
    db.session.rollback()
    body = {"code": error.code, "message": error.message}
    if error.details is not None:
        body["details"] = error.details
    return jsonify(body), error.status


@group_v2_bp.route("/groups/<string:group_key>/tournaments", methods=["POST"])
@group_v2_bp.arguments(TournamentCreateV2Schema)
def create_tournament_v2(payload, group_key):
    body, status = create_tournament_with_tables(
        group_key, payload, request.headers.get("Idempotency-Key")
    )
    return jsonify(body), status


@group_v2_bp.route("/groups:batch-get", methods=["POST"])
@group_v2_bp.arguments(GroupBatchGetSchema)
def batch_get_groups_v2(payload):
    return jsonify(batch_get_groups(payload))


@group_v2_bp.route("/groups/<string:group_key>/dashboard", methods=["GET"])
def group_dashboard_v2(group_key):
    return jsonify(group_dashboard(group_key))


@group_v2_bp.route("/groups/request-link/status:batch", methods=["POST"])
@group_v2_bp.arguments(StatusBatchRequestSchema)
@group_v2_bp.response(200, StatusBatchResponseSchema)
def batch_group_status_v2(payload):
    return batch_group_status(payload)
