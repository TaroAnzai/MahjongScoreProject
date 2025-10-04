# app/schemas/game_schema.py
from marshmallow import Schema, fields

class ScoreSchema(Schema):
    player_id = fields.Int(required=True)
    score = fields.Int(required=True)



class GameUpdateSchema(Schema):
    memo = fields.Str(load_default=None)
    played_at = fields.DateTime(load_default=None)
    scores = fields.List(fields.Nested(ScoreSchema))

