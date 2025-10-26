from marshmallow import Schema, fields, post_dump
from app.schemas.common_schemas import ShareLinkSchema
from app.schemas.mixins.share_link_mixin import ShareLinkMixin
from app.schemas.tournament_schema import TournamentSchema
from app.models import TableTypeEnum

class TableCreateSchema(Schema):
    """卓作成リクエスト"""
    name = fields.Str(required=True, description="卓名")
    type = fields.Enum(TableTypeEnum, load_default=TableTypeEnum.NORMAL, description="卓タイプ(NORMAL or CHIP)")


class TableUpdateSchema(Schema):
    """卓更新リクエスト"""
    name = fields.Str(description="卓名")
    type = fields.Str(description="卓タイプ")


class TournamentLinkSchema(ShareLinkMixin,Schema):
    """グループ共有リンク情報（短縮版）"""
    _share_link_field_name = "tournament_links"
    tournament_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        description="親トーナメントに紐づく共有リンク一覧",
    )
class TableSchema(ShareLinkMixin,Schema):
    """卓レスポンス"""
    id = fields.Int(required=True, dump_only=True, description="卓ID")
    tournament_id = fields.Int(required=True, dump_only=True, description="大会ID")
    name = fields.Str(required=True, description="卓名")
    type = fields.Str(required=True, description="卓タイプ")
    created_by = fields.Str(dump_only=True, description="作成時のKey")
    created_at = fields.DateTime(dump_only=True, description="卓作成日時（ISO 8601形式）")
    parent_tournament_link = fields.Nested(
        TournamentLinkSchema,
        required=True,
        dump_only=True,
        attribute="tournament",
        description="卓が所属する大会の情報"
    )

    _share_link_field_name = "table_links"

    table_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        dump_default=[],
        description="卓に紐づく共有リンク一覧",
    )

