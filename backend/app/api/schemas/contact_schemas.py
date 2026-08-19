from marshmallow import Schema, fields

from app.api.schemas.common_schemas import UTCDateTime
from app.models import ContactStatus


class ContactCreateSchema(Schema):
    name = fields.String(required=True, description="名前")
    email = fields.Email(required=True, description="メールアドレス")
    subject = fields.String(required=True, description="件名")
    message = fields.String(required=True, description="メッセージ内容")
    recaptcha_token = fields.Str(required=True, description="reCAPTCHAのトークン")


class ContactUpdateSchema(Schema):
    name = fields.String(required=False, allow_none=True, description="名前")
    email = fields.Email(required=False, allow_none=True, description="メールアドレス")
    subject = fields.String(required=False, allow_none=True, description="件名")
    message = fields.String(
        required=False, allow_none=True, description="メッセージ内容"
    )
    status = fields.Enum(
        ContactStatus,
        by_value=True,
        required=False,
        allow_none=True,
        description="ステータス",
    )


class ContactSchema(Schema):
    id = fields.Integer(required=True, dump_only=True, description="お問い合わせID")
    name = fields.String(required=True, dump_only=True, description="名前")
    email = fields.Email(required=True, dump_only=True, description="メールアドレス")
    subject = fields.String(required=True, dump_only=True, description="件名")
    message = fields.String(required=True, dump_only=True, description="メッセージ内容")
    status = fields.String(required=True, dump_only=True, description="ステータス")
    ip_address = fields.String(dump_only=True, description="IPアドレス")
    user_agent = fields.String(dump_only=True, description="ユーザーエージェント")
    created_at = UTCDateTime(dump_only=True, description="作成日時")
    updated_at = UTCDateTime(dump_only=True, description="更新日時")
