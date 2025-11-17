# app/schemas/admin_auth_schema.py
from marshmallow import Schema, fields, validates_schema, ValidationError


class AdminLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    @validates_schema
    def validate_fields(self, data, **kwargs):
        if not data.get("username"):
            raise ValidationError("username is required", field_name="username")
        if not data.get("password"):
            raise ValidationError("password is required", field_name="password")
