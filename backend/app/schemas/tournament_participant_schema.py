# app/schemas/tournament_participant_schema.py

from marshmallow import Schema, fields


class TournamentParticipantCreateSchema(Schema):
    """大会へのプレイヤー登録用"""
    player_id = fields.Int(required=True, description="大会に登録するプレイヤーID")


class TournamentParticipantSchema(Schema):
    """大会参加者レスポンス"""
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
