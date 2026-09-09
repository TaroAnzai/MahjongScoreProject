from marshmallow import Schema, ValidationError, fields

from app.api.schemas.common_schemas import ShareLinkSchema, UTCDateTime
from app.api.schemas.mixins.share_link_mixin import ShareLinkMixin
from app.utils.score_utils import normalize_score


class ScoreNumber(fields.Float):
    """Expose JSON/OpenAPI number while deserializing to exact Decimal."""

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return normalize_score(value)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc


class ScoreInputSchema(Schema):
    player_id = fields.Int(required=True, description="プレイヤーID")
    score = ScoreNumber(required=True, description="符号付き得点（小数第5位まで、絶対値9999999999.99999以下。通常卓は合計0）")


class GameUpdateSchema(Schema):
    """対局更新リクエスト"""

    game_index = fields.Int(description="対局インデックス")
    memo = fields.Str(allow_none=True, description="メモ")
    played_at = UTCDateTime(allow_none=True, description="対局日時")
    scores = fields.List(fields.Nested(ScoreInputSchema), description="スコア一覧")


class GameSchema(ShareLinkMixin, Schema):
    """対局レスポンス"""

    id = fields.Int(dump_only=True)
    table_id = fields.Int(required=True)
    game_index = fields.Int(required=True)
    memo = fields.Str(allow_none=True)
    played_at = UTCDateTime(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = UTCDateTime(dump_only=True)
    scores = fields.List(fields.Nested(ScoreInputSchema))

    _share_link_field_name = "game_links"

    game_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        dump_default=[],
        description="対局に紐づく共有リンク一覧",
    )


class GameCreateSchema(Schema):
    """卓に対局（ゲーム）を追加"""

    scores = fields.List(
        fields.Nested(ScoreInputSchema), required=True, description="スコア一覧"
    )
    memo = fields.Str(allow_none=True, description="メモ")
