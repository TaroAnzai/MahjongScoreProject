from marshmallow import Schema, fields

from app.schemas.common_schemas import ShareLinkSchema


class TournamentCreateSchema(Schema):
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    rate = fields.Float(allow_none=True)


class TournamentUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str(allow_none=True)
    rate = fields.Float()


class TournamentQuerySchema(Schema):
    short_key = fields.Str(required=True, metadata={"location": "query"})


class TournamentSchema(Schema):
    id = fields.Int(dump_only=True)
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    rate = fields.Float(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    share_links = fields.List(
        fields.Nested(ShareLinkSchema), dump_only=True, dump_default=[]
    )
