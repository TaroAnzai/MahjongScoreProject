"""V2 group endpoints."""

from flask import jsonify
from flask_smorest import Blueprint

from app import db
from app.api.schemas.v2_schema import (
    GroupBatchGetResponseSchema,
    GroupBatchGetSchema,
    GroupDashboardResponseSchema,
    IdempotencyHeaderSchema,
    StatusBatchRequestSchema,
    StatusBatchResponseSchema,
    TournamentCreateV2ResponseSchema,
    TournamentCreateV2Schema,
)
from app.api.services.v2_service import (
    V2Error,
    batch_get_groups,
    batch_group_status,
    create_tournament_with_tables,
    group_dashboard,
)
from app.decorators import with_v2_error_responses

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
@group_v2_bp.doc(
    summary="大会と初期卓を一括作成",
    description="指定グループに大会を作成し、initial_tablesで指定された卓も同じDBトランザクション内で作成します。途中で失敗した場合は大会を含むすべての作成をロールバックします。",
)
@group_v2_bp.arguments(IdempotencyHeaderSchema, location="headers", required=False)
@group_v2_bp.response(201, TournamentCreateV2ResponseSchema)
@with_v2_error_responses(group_v2_bp)
def create_tournament_v2(payload, headers, group_key):
    body, status = create_tournament_with_tables(
        group_key, payload, headers.get("idempotency_key")
    )
    return body, status


@group_v2_bp.route("/groups:batch-get", methods=["POST"])
@group_v2_bp.arguments(GroupBatchGetSchema)
@group_v2_bp.doc(
    summary="複数のグループを一括取得",
    description="共有キーをリクエストbodyで最大50件受け取り、client_idに対応する検索結果を返します。一部のキーが無効でもHTTP 200で他の結果を返します。",
)
@group_v2_bp.response(200, GroupBatchGetResponseSchema)
@with_v2_error_responses(group_v2_bp)
def batch_get_groups_v2(payload):
    return batch_get_groups(payload)


@group_v2_bp.route("/groups/<string:group_key>/dashboard", methods=["GET"])
@group_v2_bp.response(200, GroupDashboardResponseSchema)
@group_v2_bp.doc(
    summary="グループ画面用データを一括取得",
    description="グループ本体、配下の大会一覧、所属プレイヤー一覧を画面初期表示用の一貫したレスポンスとして返します。",
)
@with_v2_error_responses(group_v2_bp)
def group_dashboard_v2(group_key):
    return group_dashboard(group_key)


@group_v2_bp.route("/groups/request-link/status:batch", methods=["POST"])
@group_v2_bp.arguments(StatusBatchRequestSchema)
@group_v2_bp.response(200, StatusBatchResponseSchema)
@group_v2_bp.doc(
    summary="グループ作成状態を一括確認",
    description="複数のグループ作成トークンを最大50件確認し、pending、ready、expired、invalid_tokenの状態をclient_idごとに返します。",
)
@with_v2_error_responses(group_v2_bp)
def batch_group_status_v2(payload):
    return batch_group_status(payload)
