# app/resources/player_resource.py
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_login import login_required
from app.schemas.player_schema import (
    PlayerCreateSchema, PlayerResponseSchema, MessageSchema
)
from app.services.player_service import PlayerService

player_bp = Blueprint("Player", "players", url_prefix="/api/players", description="プレイヤー管理 API")

@player_bp.route("")
class PlayersResource(MethodView):
    @player_bp.arguments(PlayerCreateSchema)
    @player_bp.response(201, PlayerResponseSchema)
    @login_required
    def post(self, data):
        """プレイヤーを追加"""
        return PlayerService.add_player(data)

    @player_bp.response(200, PlayerResponseSchema(many=True))
    def get(self):
        """グループIDでプレイヤー一覧を取得"""
        from flask import request
        group_id = request.args.get("group_id")
        if not group_id:
            abort(400, message="group_id is required")
        return PlayerService.get_players_by_group(group_id)

@player_bp.route("/<int:player_id>")
class PlayerResource(MethodView):
    @player_bp.response(200, PlayerResponseSchema)
    def get(self, player_id):
        """プレイヤー情報を取得"""
        return PlayerService.get_player(player_id)

    @player_bp.response(200, MessageSchema)
    @login_required
    def delete(self, player_id):
        """プレイヤーを削除（大会参加中は不可）"""
        result, status = PlayerService.delete_player(player_id)
        if status != 200:
            abort(status, message=result["error"])
        return result
