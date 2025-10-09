# app/schemas/common_schemas.py
from marshmallow import Schema, fields, INCLUDE


class ShareLinkSchema(Schema):
    """共有リンク情報を表す共通スキーマ"""

    short_key = fields.Str(required=True)
    access_level = fields.Str(required=True)

class MessageSchema(Schema):
    message = fields.Str()

class ValidationErrorField(Schema):
    # errors["json"] に相当する部分
    # 任意のキーとリストを許可
    class Meta:
        unknown = INCLUDE

class ErrorResponseSchema(Schema):
    code = fields.Int(required=True)
    status = fields.Str(required=True)
    errors = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ValidationErrorField),
        required=True
    )
