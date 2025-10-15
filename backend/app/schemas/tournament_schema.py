from marshmallow import Schema, fields
from app.schemas.common_schemas import ShareLinkSchema
from app.schemas.mixins.share_link_mixin import ShareLinkMixin

class TournamentCreateSchema(Schema):
    """大会作成用リクエスト"""
    name = fields.Str(required=True, description="大会名")
    description = fields.Str(allow_none=True, description="大会説明")
    rate = fields.Float(allow_none=True, description="レート")


class TournamentUpdateSchema(Schema):
    """大会更新用リクエスト"""
    name = fields.Str(description="大会名")
    description = fields.Str(allow_none=True, description="大会説明")
    rate = fields.Float(description="レート")


class TournamentSchema(ShareLinkMixin,Schema):
    """大会レスポンス"""
    id = fields.Int(dump_only=True)
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    rate = fields.Float(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    _share_link_field_name = "tournament_links"

    tournament_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        dump_default=[],
        description="大会に紐づく共有リンク一覧",
    )
