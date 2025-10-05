# app/resources/tournament_resource.py
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from app.schemas.tournament_schema import (
    TournamentSchema,
    TournamentCreateSchema,
    TournamentQuerySchema,
    TournamentResultSchema,
    ScoreSummarySchema,
)
from app.services.tournament_service import TournamentService, ExportService
from app.service_errors import (
    ServiceError,
    ServiceValidationError,
    ServicePermissionError,
    ServiceNotFoundError,
    ServiceConflictError,
)
from app.decorators import with_common_error_responses


tournament_bp = Blueprint(
    "Tournaments",
    __name__,
    url_prefix="/api/tournaments",
    description="大会管理 API",
)


@tournament_bp.route("")
class TournamentListResource(MethodView):
    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.arguments(TournamentCreateSchema)
    @tournament_bp.response(201, TournamentSchema)
    @with_common_error_responses(tournament_bp)
    def post(self, query_args, new_data):
        """大会を追加（要グループ編集権限）"""
        short_key = query_args["short_key"]
        try:
            return TournamentService.create_tournament(new_data, short_key)
        except ServiceError as e:
            abort(
                e.status_code,
                message=e.message,
                errors={"json": {"message": [e.message]}},
            )

    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.response(200, TournamentSchema(many=True))
    @with_common_error_responses(tournament_bp)
    def get(self, query_args):
        """グループ共有キーで大会一覧を取得"""
        short_key = query_args["short_key"]
        try:
            return TournamentService.get_tournaments_by_group(short_key)
        except ServiceError as e:
            abort(
                e.status_code,
                message=e.message,
                errors={"json": {"message": [e.message]}},
            )


@tournament_bp.route("/<int:tournament_id>")
class TournamentResource(MethodView):
    @tournament_bp.response(200, TournamentSchema)
    @with_common_error_responses(tournament_bp)
    def get(self, tournament_id):
        """大会を取得"""
        try:
            return TournamentService.get_tournament_by_id(tournament_id)
        except ServiceError as e:
            abort(
                e.status_code,
                message=e.message,
                errors={"json": {"message": [e.message]}},
            )

    @tournament_bp.arguments(TournamentQuerySchema, location="query")
    @tournament_bp.response(200)
    @with_common_error_responses(tournament_bp)
    def delete(self, query_args, tournament_id):
        """大会削除（要グループ編集権限）"""
        short_key = query_args["short_key"]
        try:
            TournamentService.delete_tournament(tournament_id, short_key)
            return {"message": "大会を削除しました"}
        except ServiceError as e:
            abort(
                e.status_code,
                message=e.message,
                errors={"json": {"message": [e.message]}},
            )


@tournament_bp.route("/<int:tournament_id>/results")
class TournamentResultsResource(MethodView):
    @tournament_bp.response(200, TournamentResultSchema)
    @with_common_error_responses(tournament_bp)
    def get(self, tournament_id):
        """大会スコア集計結果を取得"""
        try:
            return ExportService.export_tournament_results(tournament_id)
        except ServiceError as e:
            abort(
                e.status_code,
                message=e.message,
                errors={"json": {"message": [e.message]}},
            )


@tournament_bp.route("/<int:tournament_id>/summary")
class TournamentSummaryResource(MethodView):
    @tournament_bp.response(200, ScoreSummarySchema)
    @with_common_error_responses(tournament_bp)
    def get(self, tournament_id):
        """クロステーブル形式スコアを取得"""
        try:
            return ExportService.export_score_summary(tournament_id)
        except ServiceError as e:
            abort(
                e.status_code,
                message=e.message,
                errors={"json": {"message": [e.message]}},
            )
