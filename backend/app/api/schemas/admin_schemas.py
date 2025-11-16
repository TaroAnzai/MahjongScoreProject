from marshmallow import Schema, fields
from app.api.schemas.common_schemas import ShareLinkSchema
from app.api.schemas.mixins.share_link_mixin import ShareLinkMixin
# -------------------------------------------------
# グループ情報スキーマ
# -------------------------------------------------

class AdminGroupSchema(Schema):
    """Admin用グループ情報スキーマ"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_updated_at = fields.DateTime(dump_only=True)
    email = fields.Str(dump_only=True)

    _share_link_field_name = "group_links"

    group_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        description="グループに紐づく共有リンク一覧",
    )
