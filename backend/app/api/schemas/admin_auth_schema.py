# app/schemas/admin_auth_schema.py
from marshmallow import Schema, fields, validates_schema, ValidationError

# ----------------------------------------
# 管理者ログイン（リクエスト）
# ----------------------------------------

class AdminLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    @validates_schema
    def validate_fields(self, data, **kwargs):
        if not data.get("username"):
            raise ValidationError("username is required", field_name="username")
        if not data.get("password"):
            raise ValidationError("password is required", field_name="password")
from marshmallow import Schema, fields


# ----------------------------------------
# /me（管理者ステータス）
# ----------------------------------------
class AdminMeResponseSchema(Schema):
    is_admin = fields.Boolean(
        required=True,
        metadata={"description": "管理者としてログイン中かどうか"}
    )

