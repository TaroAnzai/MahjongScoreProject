# app/resources/table_resource.py
from flask_smorest import Blueprint, abort
from flask_login import login_required
from app.schemas.table_schema import (
    TableCreateSchema, TableUpdateSchema,
    TableBaseSchema, TableWithPlayersSchema,
    PlayerSchema, MessageSchema
)
from app.services.table_service import TableService

blp = Blueprint("Table", "tables", url_prefix="/api/tables", description="卓管理 API")

@blp.route("")
class TableListResource:
    @blp.arguments(TableCreateSchema)
    @blp.response(201, TableBaseSchema)
    @login_required
    def post(self, data):
        """卓を作成"""
        table, status = TableService.create_table(data)
        if status != 201:
            abort(status, message=table["error"])
        return table

    @blp.response(200, TableBaseSchema(many=True))
    def get(self):
        """トーナメントIDで卓一覧を取得"""
        from flask import request
        tournament_id = request.args.get("tournament_id")
        if not tournament_id:
            abort(400, message="tournament_id is required")
        return TableService.get_tables_by_tournament(tournament_id)

@blp.route("/<string:table_key>")
class TableByKeyResource:
    @blp.response(200, TableWithPlayersSchema)
    def get(self, table_key):
        """テーブルキーで卓を取得"""
        return TableService.get_table_by_key(table_key)

@blp.route("/by-id/<int:table_id>")
class TableByIdResource:
    @blp.response(200, TableWithPlayersSchema)
    @login_required
    def get(self, table_id):
        """テーブルIDで卓を取得"""
        return TableService.get_table_by_id(table_id)

@blp.route("/<int:table_id>/players")
class TablePlayersResource:
    @blp.response(200, dict(players=PlayerSchema(many=True)))
    @login_required
    def get(self, table_id):
        """卓の参加プレイヤーを取得"""
        players = TableService.get_players_by_table(table_id)
        return {"players": players}

    @login_required
    def post(self, table_id):
        """卓にプレイヤーを追加"""
        from flask import request
        data = request.json
        if not isinstance(data.get("player_ids", []), list):
            abort(400, message="player_ids must be a list")
        return TableService.add_players_to_table(table_id, data["player_ids"])

@blp.route("/<int:table_id>/players/<int:player_id>")
class TablePlayerResource:
    @blp.response(200, MessageSchema)
    @login_required
    def delete(self, table_id, player_id):
        """卓からプレイヤーを削除"""
        result, status = TableService.remove_player_from_table(table_id, player_id)
        if status != 200:
            abort(status, message=result["error"])
        return result

@blp.route("/<int:table_id>")
class TableResource:
    @blp.response(200, MessageSchema)
    @login_required
    def delete(self, table_id):
        """卓を削除"""
        result, status = TableService.delete_table(table_id)
        if status != 200:
            abort(status, message=result["error"])
        return result

    @blp.arguments(TableUpdateSchema)
    @blp.response(200, TableWithPlayersSchema)
    @login_required
    def put(self, data, table_id):
        """卓情報を更新"""
        result, status = TableService.update_table(table_id, data)
        if status != 200:
            abort(status, message=result["error"])
        return result
