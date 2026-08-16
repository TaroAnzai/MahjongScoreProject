from enum import StrEnum

from marshmallow import Schema, fields, validate

from app.models import TableTypeEnum


class InitialTableSchema(Schema):
    client_id = fields.Str(required=True)
    name = fields.Str(required=True)
    type = fields.Enum(TableTypeEnum, load_default=TableTypeEnum.NORMAL)


class TournamentCreateV2Schema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True, load_default=None)
    rate = fields.Float(load_default=1.0)
    initial_tables = fields.List(fields.Nested(InitialTableSchema), load_default=list)


class ParticipantItemSchema(Schema):
    player_id = fields.Int(required=True)


class PropagateSchema(Schema):
    table_types = fields.List(fields.Enum(TableTypeEnum), required=True)


class ParticipantBatchAddSchema(Schema):
    participants = fields.List(fields.Nested(ParticipantItemSchema), required=True, validate=validate.Length(min=1))
    propagate_to = fields.Nested(PropagateSchema, allow_none=True)


class GroupBatchItemSchema(Schema):
    client_id = fields.Str(required=True)
    group_key = fields.Str(required=True)


class GroupBatchGetSchema(Schema):
    items = fields.List(fields.Nested(GroupBatchItemSchema), required=True, validate=validate.Length(max=50))


class CreationStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    EXPIRED = "expired"
    INVALID_TOKEN = "invalid_token"


class StatusBatchItemSchema(Schema):
    client_id = fields.Str(required=True)
    token = fields.Str(required=True)


class StatusBatchRequestSchema(Schema):
    items = fields.List(fields.Nested(StatusBatchItemSchema), required=True, validate=validate.Length(max=50))


class StatusResultSchema(Schema):
    client_id = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf([item.value for item in CreationStatus]))
    owner_link = fields.Str()


class StatusBatchResponseSchema(Schema):
    results = fields.List(fields.Nested(StatusResultSchema), required=True)
