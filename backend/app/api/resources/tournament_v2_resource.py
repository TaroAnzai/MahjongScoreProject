"""V2 tournament endpoints."""

from flask import jsonify
from flask_smorest import Blueprint

from app import db
from app.api.schemas.v2_schema import (
    IdempotencyHeaderSchema,
    ParticipantBatchAddResponseSchema,
    ParticipantBatchAddSchema,
    ParticipantDeleteResponseSchema,
    TournamentDashboardResponseSchema,
)
from app.api.services.v2_service import (
    V2Error,
    batch_add_participants,
    delete_participant,
    tournament_dashboard,
)
from app.decorators import with_v2_error_responses

tournament_v2_bp = Blueprint(
    "tournaments_v2",
    __name__,
    url_prefix="/api/v2/tournaments",
    description="V2 tournament API",
)


@tournament_v2_bp.errorhandler(V2Error)
def handle_v2_error(error):
    db.session.rollback()
    body = {"code": error.code, "message": error.message}
    if error.details is not None:
        body["details"] = error.details
    return jsonify(body), error.status


@tournament_v2_bp.route(
    "/<string:tournament_key>/participants:batch-add", methods=["POST"]
)
@tournament_v2_bp.arguments(ParticipantBatchAddSchema)
@tournament_v2_bp.doc(
    summary="大会参加者を一括追加して卓へ同期",
    description="複数プレイヤーを冪等に大会へ追加し、大会配下のすべてのCHIP卓にも同じDBトランザクションで必ず登録します。",
)
@tournament_v2_bp.arguments(IdempotencyHeaderSchema, location="headers", required=False)
@tournament_v2_bp.response(200, ParticipantBatchAddResponseSchema)
@with_v2_error_responses(tournament_v2_bp)
def batch_add_participants_v2(payload, headers, tournament_key):
    body, status = batch_add_participants(
        tournament_key, payload, headers.get("idempotency_key")
    )
    return body, status


@tournament_v2_bp.route(
    "/<string:tournament_key>/participants/<int(min=1):player_id>", methods=["DELETE"]
)
@tournament_v2_bp.arguments(IdempotencyHeaderSchema, location="headers", required=False)
@tournament_v2_bp.response(200, ParticipantDeleteResponseSchema)
@tournament_v2_bp.doc(
    summary="大会参加者を削除してチップ卓へ同期",
    description="大会参加者と大会配下のすべてのCHIP卓の参加者登録を同時に削除します。対象CHIP卓にスコアが存在する場合は409 Conflictを返します。",
    parameters=[
        {
            "name": "player_id",
            "in": "path",
            "required": True,
            "description": "削除するプレイヤーIDです。1以上を指定します。",
            "schema": {"type": "integer", "minimum": 1},
        },
        {
            "name": "Idempotency-Key",
            "in": "header",
            "required": False,
            "description": "同じ更新リクエストの再送を安全に処理するための冪等キーです。最大255文字です。",
            "schema": {"type": "string", "maxLength": 255},
        },
    ],
)
@with_v2_error_responses(tournament_v2_bp)
def delete_participant_v2(headers, tournament_key, player_id):
    body, status = delete_participant(
        tournament_key,
        player_id,
        headers.get("idempotency_key"),
    )
    return body, status


@tournament_v2_bp.route("/<string:tournament_key>/dashboard", methods=["GET"])
@tournament_v2_bp.response(200, TournamentDashboardResponseSchema)
@tournament_v2_bp.doc(
    summary="大会画面用データを一括取得",
    description="大会、参加者、未参加のグループプレイヤー、卓一覧、スコアマップを画面初期表示用の一貫したレスポンスとして返します。",
)
@with_v2_error_responses(tournament_v2_bp)
def tournament_dashboard_v2(tournament_key):
    return tournament_dashboard(tournament_key)
