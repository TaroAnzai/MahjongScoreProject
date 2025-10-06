from marshmallow import Schema, fields

from app.schemas.common_schemas import ShareLinkSchema


class TableCreateSchema(Schema):
    tournament_id = fields.Int(required=True)
    name = fields.Str(required=True)
    type = fields.Str(load_default="normal")


class TableUpdateSchema(Schema):
    name = fields.Str()
    type = fields.Str()


class TableQuerySchema(Schema):
    short_key = fields.Str(required=True, metadata={"location": "query"})


class TableSchema(Schema):
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int(required=True)
    name = fields.Str(required=True)
    type = fields.Str()
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    share_links = fields.List(
        fields.Nested(ShareLinkSchema), dump_only=True, dump_default=[]
    )
