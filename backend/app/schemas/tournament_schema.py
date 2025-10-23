from marshmallow import Schema, fields,post_dump
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
    started_at = fields.DateTime(allow_none=True, description="大会開始日時（ISO 8601形式）")

class GroupLinkSchema(ShareLinkMixin,Schema):
    """グループ共有リンク情報（短縮版）"""
    _share_link_field_name = "group_links"
    group_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        description="グループに紐づく共有リンク一覧",
    )

class TournamentSchema(ShareLinkMixin,Schema):
    """大会レスポンス"""
    id = fields.Int(required=True, dump_only=True, description="大会ID")
    group_id = fields.Int(required=True, dump_only=True, description="グループID")
    name = fields.Str(required=True, description="大会名")
    description = fields.Str(allow_none=True, description="大会説明")
    rate = fields.Float(required=True, description="レート")
    created_by = fields.Str(dump_only=True, description="作成時のKey")
    created_at = fields.DateTime(dump_only=True, description="大会作成日時（ISO 8601形式）")
    started_at = fields.DateTime(allow_none=True, description="大会開始日時（ISO 8601形式）")
    parent_group_link = fields.Nested(
        GroupLinkSchema,
        required=True,
        dump_only=True,
        attribute="group",
        description="大会が所属するグループ情報"
    )
    _share_link_field_name = "tournament_links"

    tournament_links = fields.List(
        fields.Nested(ShareLinkSchema),
        required=True,
        dump_only=True,
        dump_default=[],
        description="大会に紐づく共有リンク一覧",
    )

