# app/schemas/game_schema.py
from marshmallow import Schema, fields

class ScoreSchema(Schema):
    player_id = fields.Int(required=True)
    score = fields.Int(required=True)

class GameCreateSchema(Schema):
    scores = fields.List(fields.Nested(ScoreSchema), required=True)
    memo = fields.Str(load_default=None)

class GameUpdateSchema(Schema):
    memo = fields.Str(load_default=None)
    played_at = fields.DateTime(load_default=None)
    scores = fields.List(fields.Nested(ScoreSchema))

class GameResponseSchema(Schema):
    game_id = fields.Int(required=True)
    scores = fields.List(fields.Nested(ScoreSchema))

class MessageSchema(Schema):
    message = fields.Str(required=True)
