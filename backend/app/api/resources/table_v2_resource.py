"""V2 table endpoints."""

from flask import jsonify
from flask_smorest import Blueprint

from app import db
from app.api.schemas.v2_schema import (
    IdempotencyHeaderSchema,
    TableDashboardResponseSchema,
    TableDeleteResponseSchema,
)
from app.api.services.v2_service import V2Error, cascade_delete_table, table_dashboard
from app.decorators import with_v2_error_responses

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
@table_v2_bp.doc(
    summary="卓と配下データをカスケード削除",
    description="卓、卓参加者、ゲーム、スコア、共有リンクを同じDBトランザクションで削除し、削除した各データの件数を返します。",
)
@table_v2_bp.arguments(IdempotencyHeaderSchema, location="headers", required=False)
@table_v2_bp.response(200, TableDeleteResponseSchema)
@with_v2_error_responses(table_v2_bp)
def delete_table_v2(headers, table_key):
    body, status = cascade_delete_table(table_key, headers.get("idempotency_key"))
    return body, status


@table_v2_bp.route("/<string:table_key>/dashboard", methods=["GET"])
@table_v2_bp.response(200, TableDashboardResponseSchema)
@table_v2_bp.doc(
    summary="卓画面用データを一括取得",
    description="卓、卓参加者、卓へ未登録の大会参加者、ゲームとスコアを画面初期表示用の一貫したレスポンスとして返します。",
)
@with_v2_error_responses(table_v2_bp)
def table_dashboard_v2(table_key):
    return table_dashboard(table_key)
