from marshmallow import Schema, fields,validates, ValidationError
from app.api.schemas.common_schemas import ShareLinkSchema
from app.api.schemas.mixins.share_link_mixin import ShareLinkMixin



class ScoreInputSchema(Schema):
    player_id = fields.Int(required=True, description="プレイヤーID")
    score = fields.Float(required=True, description="得点（合計0である必要あり）")
class GameUpdateSchema(Schema):
    """対局更新リクエスト"""
    game_index = fields.Int(description="対局インデックス")
    memo = fields.Str(allow_none=True, description="メモ")
    played_at = fields.DateTime(allow_none=True, description="対局日時")
    scores = fields.List(fields.Nested(ScoreInputSchema),  description="スコア一覧")

class GameSchema(ShareLinkMixin, Schema):
    """対局レスポンス"""
    id = fields.Int(dump_only=True)
    table_id = fields.Int(required=True)
    game_index = fields.Int(required=True)
    memo = fields.Str(allow_none=True)
    played_at = fields.DateTime(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
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
    scores = fields.List(fields.Nested(ScoreInputSchema), required=True, description="スコア一覧")
    memo = fields.Str(allow_none=True, description="メモ")






