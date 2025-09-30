# app/schemas/table_schema.py
from marshmallow import Schema, fields

class TableBaseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    tournament_id = fields.Int(required=True)
    type = fields.Str(dump_only=True)
    table_key = fields.Str(dump_only=True)
    edit_key = fields.Str(dump_only=True)

class TableCreateSchema(Schema):
    name = fields.Str(required=True)
    tournament_id = fields.Int(required=True)
    player_ids = fields.List(fields.Int(), load_default=[])

class TableUpdateSchema(Schema):
    name = fields.Str()
    type = fields.Str()
    description = fields.Str()

class PlayerSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    nickname = fields.Str()

class TableWithPlayersSchema(Schema):
    table = fields.Nested(TableBaseSchema)
    players = fields.List(fields.Nested(PlayerSchema))

class MessageSchema(Schema):
    message = fields.Str(required=True)
