# app/schemas/tournament_schema.py
from marshmallow import Schema, fields


class TournamentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class TournamentCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)


class PlayerScoreSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    total_score = fields.Int(required=True)
    games_played = fields.Int(required=True)

class GroupSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    players = fields.List(fields.Nested(PlayerScoreSchema))

class TournamentResultSchema(Schema):
    tournament = fields.Dict(keys=fields.Str(), values=fields.Raw())
    groups = fields.List(fields.Nested(GroupSchema))

class ScoreSummaryPlayerSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)

class ScoreSummaryTableSchema(Schema):
    name = fields.Str(required=True)
    scores = fields.Dict(keys=fields.Int(), values=fields.Int())

class ScoreSummarySchema(Schema):
    players = fields.List(fields.Nested(ScoreSummaryPlayerSchema))
    tables = fields.List(fields.Nested(ScoreSummaryTableSchema))
