# app/schemas/auth_schema.py
from marshmallow import Schema, fields

class LoginByKeySchema(Schema):
    edit_key = fields.String(required=True)
    type = fields.String(required=True, validate=lambda x: x in ["group", "tournament"])

class MessageSchema(Schema):
    message = fields.String(required=True)
