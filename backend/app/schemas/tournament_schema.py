from marshmallow import Schema, fields
from app.schemas.common_schemas import ShareLinkSchema
from app.schemas.mixins.share_link_mixin import ShareLinkMixin
from app.schemas.group_schema import GroupSchema

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
    id = fields.Int(required=True, dump_only=True, description="大会ID")
    group_id = fields.Int(required=True, dump_only=True, description="グループID")
    name = fields.Str(required=True, description="大会名")
    description = fields.Str(allow_none=True)
    rate = fields.Float(required=True, description="レート")
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    group = fields.Nested(
        GroupSchema,
        required=True,
        exclude=("description", "id", "created_by", "created_at", "last_updated_at"),
        dump_only=True,
        description="大会が所属するグループ情報（short_keyとグループ名のみ）"
    )
    _share_link_field_name = "tournament_links"

    tournament_links = fields.List(
        fields.Nested(ShareLinkSchema),
        required=True,
        dump_only=True,
        dump_default=[],
        description="大会に紐づく共有リンク一覧",
    )
