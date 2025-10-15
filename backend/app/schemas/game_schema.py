from marshmallow import Schema, fields
from app.schemas.common_schemas import ShareLinkSchema
from app.schemas.mixins.share_link_mixin import ShareLinkMixin

class GameCreateSchema(Schema):
    """対局作成リクエスト"""
    game_index = fields.Int(required=True, description="対局インデックス（半荘番号など）")
    memo = fields.Str(allow_none=True, description="メモ")
    played_at = fields.DateTime(allow_none=True, description="対局日時")


class GameUpdateSchema(Schema):
    """対局更新リクエスト"""
    game_index = fields.Int(description="対局インデックス")
    memo = fields.Str(allow_none=True, description="メモ")
    played_at = fields.DateTime(allow_none=True, description="対局日時")


class GameSchema(ShareLinkMixin, Schema):
    """対局レスポンス"""
    id = fields.Int(dump_only=True)
    table_id = fields.Int(required=True)
    game_index = fields.Int(required=True)
    memo = fields.Str(allow_none=True)
    played_at = fields.DateTime(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    _share_link_field_name = "game_links"

    game_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        dump_default=[],
        description="対局に紐づく共有リンク一覧",
    )
