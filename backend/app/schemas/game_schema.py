from marshmallow import Schema, fields

from app.schemas.common_schemas import ShareLinkSchema


class GameCreateSchema(Schema):
    table_id = fields.Int(required=True)
    game_index = fields.Int(required=True)
    memo = fields.Str(allow_none=True)
    played_at = fields.DateTime(allow_none=True)


class GameUpdateSchema(Schema):
    game_index = fields.Int()
    memo = fields.Str(allow_none=True)
    played_at = fields.DateTime(allow_none=True)


class GameQuerySchema(Schema):
    short_key = fields.Str(required=True, metadata={"location": "query"})


class GameSchema(Schema):
    id = fields.Int(dump_only=True)
    table_id = fields.Int(required=True)
    game_index = fields.Int(required=True)
    memo = fields.Str(allow_none=True)
    played_at = fields.DateTime(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    share_links = fields.List(
        fields.Nested(ShareLinkSchema), dump_only=True, dump_default=[]
    )
