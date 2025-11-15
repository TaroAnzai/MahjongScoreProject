from marshmallow import Schema, fields
from app.models import TableTypeEnum
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
    type = fields.Enum(TableTypeEnum,
        required=True,
        description="テーブル（卓）のタイプ"
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


# =========================================================
# GroupPlayerStatSchema
# =========================================================
class GroupPlayerStatSchema(BaseSchema):
    """グループ内のプレイヤー統計"""
    player_id = fields.Int(required=True, description="プレイヤーID")
    player_name = fields.Str(required=True, description="プレイヤー名")
    tournament_count = fields.Int(dump_default=0, description="大会参加回数")
    game_count = fields.Int(dump_default=0, description="対局数")
    rank1_rate = fields.Float(dump_default=0.0, description="1位率")
    rank1_count = fields.Int(dump_default=0, description="1位回数")
    rank2_count = fields.Int(dump_default=0, description="2位回数")
    rank3_count = fields.Int(dump_default=0, description="3位回数")
    rank4_or_lower_count = fields.Int(dump_default=0, description="4位以下回数")
    average_rank = fields.Float(dump_default=0.0, description="平均順位")
    total_score = fields.Float(dump_default=0.0, description="得点合計（チップ・換算含まない）")
    total_balance = fields.Float(dump_default=0.0, description="収支（チップ・換算含む）")

class GroupPlayerStatsSchema(BaseSchema):
    """グループ全体のプレイヤー統計リスト"""
    group = fields.Dict(required=True, description="グループ情報（id, nameなど）")
    period = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        description="集計期間",
        dump_default={}
    )
    players = fields.List(fields.Nested(GroupPlayerStatSchema), dump_default=[])

class GroupPlayerStatsQuerySchema(BaseSchema):
    """クエリで受け取る期間指定（大会開始日ベース）"""
    start_date = fields.Date(
        required=False,
        allow_none=True,
        description="集計開始日（Tournament.started_at基準、省略時は全期間）",
        example="2025-01-01"
    )
    end_date = fields.Date(
        required=False,
        allow_none=True,
        description="集計終了日（Tournament.started_at基準、省略時は全期間）",
        example="2025-12-31"
    )
