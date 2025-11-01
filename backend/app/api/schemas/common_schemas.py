# app/schemas/common_schemas.py
from marshmallow import Schema, fields, INCLUDE


class ShareLinkSchema(Schema):
    """共有リンク情報を表す共通スキーマ"""
    short_key = fields.Str(required=True, description="共有アクセス用キー")
    access_level = fields.Str(required=True, description="アクセスレベル（VIEW/EDIT/OWNER）")
    created_by = fields.Str(dump_only=True, description="作成者")
    created_at = fields.DateTime(dump_only=True, description="作成日時")


class MessageSchema(Schema):
    message = fields.Str()


class ValidationErrorField(Schema):
    """errors[json] に相当する部分"""
    class Meta:
        unknown = INCLUDE


class ErrorResponseSchema(Schema):
    code = fields.Int(required=True)
    status = fields.Str(required=True)
    errors = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ValidationErrorField),
        required=True,
    )
