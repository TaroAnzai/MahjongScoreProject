# app/schemas/tournament_schema.py
from marshmallow import Schema, fields


class TournamentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class TournamentCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
