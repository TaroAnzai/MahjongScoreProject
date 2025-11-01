# app/schemas/table_player_schema.py

from marshmallow import Schema, fields, validate
from app.api.schemas.player_schema import PlayerSchema

class TablePlayerItemSchema(Schema):
    """卓への1人分の参加情報"""
    player_id = fields.Int(required=True, description="参加するプレイヤーID")
    seat_position = fields.Int(allow_none=True, description="卓での座席位置")
class TablePlayerCreateSchema(Schema):
    """卓への参加登録（複数対応）"""
    players = fields.List(
        fields.Nested(TablePlayerItemSchema),
        required=True,
        description="卓に参加するプレイヤー一覧（player_id, seat_position のリスト）",
        validate=validate.Length(min=1),
    )


class TablePlayerSchema(Schema):
    """卓参加者レスポンス"""
    id = fields.Int(dump_only=True)
    table_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    seat_position = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

class TablePlayersSchema(Schema):
    """複数卓参加者レスポンス"""
    table_key = fields.Str(required=True)
    table_players = fields.List(fields.Nested(PlayerSchema),required=True, dump_only=True, description="卓に参加するプレイヤー一覧")
    errors = fields.List(fields.Str(), description="登録時のエラー情報一覧")
