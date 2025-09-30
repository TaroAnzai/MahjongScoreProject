# app/schemas/player_schema.py
from marshmallow import Schema, fields

class PlayerBaseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    group_id = fields.Int(required=True)

class PlayerCreateSchema(Schema):
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)

class PlayerResponseSchema(PlayerBaseSchema):
    pass

class MessageSchema(Schema):
    message = fields.Str(required=True)
