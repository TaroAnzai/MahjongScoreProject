from marshmallow import Schema, fields

# =========================================================
# 共通ベーススキーマ（dump_defaultを常に出力）
# =========================================================
class BaseSchema(Schema):
    class Meta:
        dump_defaults = True  # Flask-Smorest で Redoc にも反映される
        ordered = True        # ドキュメント表示順を安定化

class PlayerScoreSchema(BaseSchema):
    id = fields.Int(
        required=True,
        description="プレイヤーID"
    )
    name = fields.Str(
        required=True,
        description="プレイヤー名"
    )
    games_played = fields.Int(
        dump_default=0,
        description="参加ゲーム数"
    )

    total_score = fields.Float(
        dump_default=0.0,
        description="合計スコア"
    )


class TournamentExportSchema(BaseSchema):
    tournament = fields.Dict(
        required=True,
        description="大会情報"
    )
    players = fields.List(
        fields.Nested(PlayerScoreSchema),
        dump_default=[],
        description="大会に参加する全プレイヤーとそのスコア情報"
        )


class GroupSummarySchema(BaseSchema):
    group = fields.Dict(
        required=True,
        description="グループ情報"
    )
    tournaments = fields.List(
        fields.Nested(TournamentExportSchema),
        dump_default=[],
        description="グループに含まれる大会一覧"
        )



# =========================================================
#TournamentScoreMapSchema（scoreMap形式）
# =========================================================
class PlayerScoreMapSchema(BaseSchema):
    id = fields.Int(
        required=True,
        description="プレイヤーID"
    )
    name = fields.Str(
        required=True,
        description="プレイヤー名"
    )
    scores = fields.Dict(
        keys=fields.Str(description="テーブルID（文字列）"),
        values=fields.Float(description="各テーブルでのスコア"),
        dump_default={},
        description="各テーブルごとのスコア辞書。例: {'1': 25000, '2': -5000}"
    )
    total = fields.Float(
        dump_default=0.0,
        description="合計スコア（全テーブルの合計）"
    )
    converted_total = fields.Float(
        dump_default=0.0,
        description="換算スコア（合計スコア × レート）"
    )

class TableInfoSchema(Schema):
    id = fields.Int(
        required=True,
        description="テーブル（卓）のID"
    )
    name = fields.Str(
        required=True,
        description="テーブル（卓）の名前"
    )
    type = fields.Str(
        required=True,
        description="テーブル（卓）のタイプ。通常卓は'normal'、チップ卓は'chip'"
    )

class TournamentScoreMapSchema(BaseSchema):
    """大会スコアマップ"""

    tournament_id = fields.Int(
        required=True,
        description="大会ID"
    )
    tables = fields.List(
        fields.Nested(TableInfoSchema),
        required=True,
        dump_default=[],
        description="大会に含まれる卓（テーブル）の一覧"
    )
    players = fields.List(
        fields.Nested(PlayerScoreMapSchema),
        required=True,
        dump_default=[],
        description="大会に参加する全プレイヤーとそのスコア情報"
    )
    rate = fields.Float(
        dump_default=1.0,
        description="換算レート"
    )


