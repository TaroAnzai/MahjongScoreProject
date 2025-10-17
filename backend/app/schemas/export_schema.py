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
class TableScoreSchema(Schema):
    """各卓のスコア（例: table_10: 25500）"""
    # 卓ごとのスコアは動的キーなので Dict[str, float]
    table_scores = fields.Dict(
        keys=fields.Str(),
        values=fields.Float(),
        required=False,
        description="各卓ごとのスコア"
    )


class PlayerScoreMapSchema(Schema):
    """各プレイヤーの詳細スコア"""
    total = fields.Float(required=False, description="大会全体の合計スコア")
    games_played = fields.Int(required=False, description="参加したゲーム数")
    # 卓スコア部分を直接Dictで表す
    table_scores = fields.Dict(
        keys=fields.Str(),
        values=fields.Float(),
        required=False,
        description="卓ごとのスコア（table_XX → 点数）"
    )


class TournamentScoreMapSchema(Schema):
    """全プレイヤーのスコアマップ（player_idをキー）"""
    score_map = fields.Dict(
        keys=fields.Int(),
        values=fields.Nested(PlayerScoreMapSchema),
        description="player_idをキーにしたスコア詳細マップ"
    )
