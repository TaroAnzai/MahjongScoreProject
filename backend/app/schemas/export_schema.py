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

from marshmallow import Schema, fields



# =========================================================
#TournamentScoreMapSchema（scoreMap形式）
# =========================================================
class PlayerScoreMapSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    scores = fields.Dict(keys=fields.Str(), values=fields.Float())
    total = fields.Float()
    converted_total = fields.Float()

class TableInfoSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class TournamentScoreMapSchema(Schema):
    tournament_id = fields.Int()
    tables = fields.List(fields.Nested(TableInfoSchema))
    players = fields.List(fields.Nested(PlayerScoreMapSchema))
    rate = fields.Float()


