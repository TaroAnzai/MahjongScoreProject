# app/schemas/table_player_schema.py

from marshmallow import Schema, fields


class TablePlayerCreateSchema(Schema):
    """卓への参加登録"""
    player_id = fields.Int(required=True, description="参加するプレイヤーID")
    seat_position = fields.Int(allow_none=True, description="卓での座席位置")


class TablePlayerSchema(Schema):
    """卓参加者レスポンス"""
    id = fields.Int(dump_only=True)
    table_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    seat_position = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
