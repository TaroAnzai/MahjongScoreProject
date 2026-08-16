"""V2 table endpoints."""
from flask import jsonify, request
from flask_smorest import Blueprint

from app import db
from app.api.services.v2_service import V2Error, cascade_delete_table, table_dashboard


table_v2_bp = Blueprint(
    "tables_v2", __name__, url_prefix="/api/v2/tables", description="V2 table API"
)


@table_v2_bp.errorhandler(V2Error)
def handle_v2_error(error):
    db.session.rollback()
    body = {"code": error.code, "message": error.message}
    if error.details is not None:
        body["details"] = error.details
    return jsonify(body), error.status


@table_v2_bp.route("/<string:table_key>", methods=["DELETE"])
def delete_table_v2(table_key):
    body, status = cascade_delete_table(table_key, request.headers.get("Idempotency-Key"))
    return jsonify(body), status


@table_v2_bp.route("/<string:table_key>/dashboard", methods=["GET"])
def table_dashboard_v2(table_key):
    return jsonify(table_dashboard(table_key))
