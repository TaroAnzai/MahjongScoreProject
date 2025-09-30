# app/schemas/group_schema.py
from marshmallow import Schema, fields


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    group_key = fields.Str(dump_only=True)
    edit_key = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class GroupCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)


class GroupUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str()
