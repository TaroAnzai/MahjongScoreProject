from marshmallow import Schema, fields

from app.schemas.common_schemas import ShareLinkSchema


class PlayerCreateSchema(Schema):
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)
    nickname = fields.Str(allow_none=True)
    display_order = fields.Int(allow_none=True)


class PlayerUpdateSchema(Schema):
    name = fields.Str()
    nickname = fields.Str(allow_none=True)
    display_order = fields.Int()


class PlayerQuerySchema(Schema):
    short_key = fields.Str(required=True, metadata={"location": "query"})


class PlayerSchema(Schema):
    id = fields.Int(dump_only=True)
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)
    nickname = fields.Str(allow_none=True)
    display_order = fields.Int(allow_none=True)
    share_links = fields.List(
        fields.Nested(ShareLinkSchema), dump_only=True, dump_default=[]
    )
