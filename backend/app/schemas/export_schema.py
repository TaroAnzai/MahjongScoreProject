from marshmallow import Schema, fields


class PlayerScoreSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    games_played = fields.Int()
    total_score = fields.Float()


class TournamentExportSchema(Schema):
    tournament = fields.Dict()
    players = fields.List(fields.Nested(PlayerScoreSchema))


class GroupSummarySchema(Schema):
    group = fields.Dict()
    tournaments = fields.List(fields.Nested(TournamentExportSchema))
