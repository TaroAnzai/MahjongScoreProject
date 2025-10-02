# app/schemas/table_schema.py
from marshmallow import Schema, fields
from app.schemas.game_schema import ScoreSchema

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
class GameCreateSchema(Schema):
    scores = fields.List(fields.Nested(ScoreSchema), required=True)
    memo = fields.Str(load_default=None)

class GameResponseSchema(Schema):
    game_id = fields.Int(required=True)
    scores = fields.List(fields.Nested(ScoreSchema))

class GetTableQuerySchema(Schema):
    key = fields.Int(required=False,
                     metadata={"description": "get table by Table Key"})
    tournament_id = fields.Int(required=False,
                               metadata={"description": "get tables by Tournament ID"})