# app/schemas/group_schema.py
from marshmallow import Schema, fields


class ShareLinkSchema(Schema):
    access_level = fields.Str()
    short_key = fields.Str()


class GroupSchema(Schema):
    """グループ詳細・一覧表示用"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_updated_at = fields.DateTime(dump_only=True)
    share_links = fields.List(fields.Nested(ShareLinkSchema), dump_only=True)


class GroupCreateSchema(Schema):
    """新規グループ作成用"""
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)


class GroupUpdateSchema(Schema):
    """グループ更新用"""
    name = fields.Str()
    description = fields.Str()
