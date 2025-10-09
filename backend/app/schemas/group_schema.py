from marshmallow import Schema, fields

from app.schemas.common_schemas import ShareLinkSchema


class GroupCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)


class GroupUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str(allow_none=True)


class GroupQuerySchema(Schema):
    short_key = fields.Str(required=True, metadata={"location": "query"})


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_updated_at = fields.DateTime(dump_only=True)
    share_links = fields.List(
        fields.Nested(ShareLinkSchema), dump_only=True, dump_default=[]
    )
