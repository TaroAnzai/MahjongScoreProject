# app/resources/player_resource.py
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request
from app.schemas.player_schema import (
    PlayerCreateSchema, PlayerResponseSchema, MessageSchema
)
from app.services.player_service import PlayerService

player_bp = Blueprint("Player", "players", url_prefix="/api/players", description="プレイヤー管理 API")


@player_bp.route("")
class PlayersResource(MethodView):
    @player_bp.arguments(PlayerCreateSchema)
    @player_bp.response(201, PlayerResponseSchema)
    def post(self, data):
        """プレイヤーを追加（要グループ編集権限）"""
        short_key = request.args.get("short_key")
        if not short_key:
            abort(400, message="short_key is required")
        try:
            return PlayerService.add_player(data, short_key)
        except PermissionError as e:
            abort(403, message=str(e))

    @player_bp.response(200, PlayerResponseSchema(many=True))
    def get(self):
        """グループの共有キーでプレイヤー一覧を取得"""
        short_key = request.args.get("short_key")
        if not short_key:
            abort(400, message="short_key is required")
        return PlayerService.get_players_by_group(short_key)


@player_bp.route("/<int:player_id>")
class PlayerResource(MethodView):
    @player_bp.response(200, PlayerResponseSchema)
    def get(self, player_id):
        """プレイヤー情報を取得"""
        return PlayerService.get_player(player_id)

    @player_bp.response(200, MessageSchema)
    def delete(self, player_id):
        """プレイヤー削除（要グループ編集権限）"""
        short_key = request.args.get("short_key")
        if not short_key:
            abort(400, message="short_key is required")
        try:
            result, status = PlayerService.delete_player(player_id, short_key)
        except PermissionError as e:
            abort(403, message=str(e))
        if status != 200:
            abort(status, message=result.get("error", "Delete failed"))
        return result
