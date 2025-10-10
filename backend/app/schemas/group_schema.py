# app/schemas/group_schema.py
from marshmallow import Schema, fields
from app.schemas.common_schemas import ShareLinkSchema


class GroupCreateSchema(Schema):
    """グループ作成用リクエスト"""
    name = fields.Str(required=True, description="グループ名")
    description = fields.Str(allow_none=True, description="説明")


class GroupUpdateSchema(Schema):
    """グループ更新用リクエスト"""
    name = fields.Str(description="グループ名")
    description = fields.Str(allow_none=True, description="説明")


class GroupSchema(Schema):
    """グループレスポンス"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_updated_at = fields.DateTime(dump_only=True)

    # ✅ リレーション名を group_links に変更
    group_links = fields.List(
        fields.Nested(ShareLinkSchema),
        dump_only=True,
        dump_default=[],
        description="グループに紐づく共有リンク一覧",
    )
