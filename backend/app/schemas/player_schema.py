from marshmallow import Schema, fields


class PlayerCreateSchema(Schema):
    """プレイヤー作成"""
    name = fields.Str(required=True, description="プレイヤー名")
    nickname = fields.Str(allow_none=True, description="ニックネーム")
    display_order = fields.Int(allow_none=True, description="表示順")


class PlayerUpdateSchema(Schema):
    """プレイヤー更新"""
    name = fields.Str()
    nickname = fields.Str(allow_none=True)
    display_order = fields.Int()


class PlayerSchema(Schema):
    """プレイヤーレスポンス"""
    id = fields.Int(required=True, dump_only=True)
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)
    nickname = fields.Str(allow_none=True)
    display_order = fields.Int(allow_none=True)
