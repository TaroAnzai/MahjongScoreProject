# app/schemas/tournament_participant_schema.py

from marshmallow import Schema, fields


class TournamentParticipantQuerySchema(Schema):
    """大会参加者共通クエリパラメータ"""
    short_key = fields.Str(required=True, metadata={"location": "query"})


class TournamentParticipantCreateSchema(Schema):
    """大会へのプレイヤー登録用"""
    player_id = fields.Int(required=True, description="大会に登録するプレイヤーのID")


class TournamentParticipantSchema(Schema):
    """大会参加者レスポンス用"""
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
