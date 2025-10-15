from marshmallow import Schema, fields
from app.schemas.common_schemas import ShareLinkSchema
from app.schemas.mixins.share_link_mixin import ShareLinkMixin

class TableCreateSchema(Schema):
    """卓作成リクエスト"""
    name = fields.Str(required=True, description="卓名")
    type = fields.Str(load_default="normal", description="卓タイプ(normal/chip)")


class TableUpdateSchema(Schema):
    """卓更新リクエスト"""
    name = fields.Str(description="卓名")
    type = fields.Str(description="卓タイプ")


class TableSchema(ShareLinkMixin,Schema):
    """卓レスポンス"""
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int(required=True)
    name = fields.Str(required=True)
    type = fields.Str()
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    _share_link_field_name = "table_links"

    table_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        dump_default=[],
        description="卓に紐づく共有リンク一覧",
    )
