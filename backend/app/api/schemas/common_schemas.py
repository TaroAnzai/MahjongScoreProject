# app/schemas/common_schemas.py
from datetime import timezone

from marshmallow import INCLUDE, Schema, fields

RFC3339_UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class UTCDateTime(fields.DateTime):
    """RFC 3339で受け取り、UTCへ正規化してUTCのRFC 3339で返す日時フィールド。"""

    def __init__(self, *args, **kwargs):
        # 独自formatを指定しない。
        # OpenAPIでは type: string / format: date-time として生成される。
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        # DateTimeのデフォルトISO 8601解析を利用する。
        parsed = super()._deserialize(value, attr, data, **kwargs)

        if parsed is None:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        return value.strftime(RFC3339_UTC_FORMAT)


class ShareLinkSchema(Schema):
    """共有リンク情報を表す共通スキーマ"""

    short_key = fields.Str(required=True, description="共有アクセス用キー")
    access_level = fields.Str(
        required=True, description="アクセスレベル（VIEW/EDIT/OWNER）"
    )
    created_by = fields.Str(dump_only=True, description="作成者")
    created_at = UTCDateTime(dump_only=True, description="作成日時")


class MessageSchema(Schema):
    message = fields.Str()


class ValidationErrorField(Schema):
    """errors[json] に相当する部分"""

    class Meta:
        unknown = INCLUDE


class ErrorResponseSchema(Schema):
    code = fields.Int(required=True)
    status = fields.Str(required=True)
    errors = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ValidationErrorField),
        required=True,
    )
