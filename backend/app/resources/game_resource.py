# app/resources/game_resource.py
from flask_smorest import Blueprint
from flask_login import login_required
from app.schemas.game_schema import (
    GameCreateSchema, GameUpdateSchema, GameResponseSchema, MessageSchema
)
from app.services.game_service import GameService

blp = Blueprint("Game", "games", url_prefix="/api/games", description="ゲーム管理 API")

@blp.route("/<int:table_id>/games")
class GameListResource:
    @blp.arguments(GameCreateSchema)
    @blp.response(201, GameResponseSchema)
    @login_required
    def post(self, data, table_id):
        """卓に新しいゲームを追加"""
        return GameService.add_game(table_id, scores=data["scores"], memo=data.get("memo"))

    @blp.response(200, GameResponseSchema(many=True))
    def get(self, table_id):
        """卓の全ゲームを取得"""
        return GameService.get_games(table_id)

@blp.route("/<int:game_id>")
class GameResource:
    @blp.arguments(GameUpdateSchema)
    @blp.response(200, MessageSchema)
    def put(self, data, game_id):
        """ゲームを更新"""
        return GameService.update_game(game_id, data)

    @blp.response(200, MessageSchema)
    def delete(self, game_id):
        """ゲームを削除"""
        return GameService.delete_game(game_id)
