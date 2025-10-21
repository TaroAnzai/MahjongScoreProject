# app/schemas/tournament_participant_schema.py

from marshmallow import Schema, fields

class TournamentParticipantSchema(Schema):
    """大会参加者"""
    player_id = fields.Int(required=True,description="大会に登録するプレイヤーID")
    created_at = fields.DateTime(dump_only=True)
class TournamentParticipantsCreateSchema(Schema):
    """大会への複数プレイヤー登録用"""
    participants = fields.List(
        fields.Nested(TournamentParticipantSchema),
        required=True,
        description="大会に登録するプレイヤー一覧",
        example=[{"player_id": 1}, {"player_id": 2}],
    )

class TournamentParticipantsSchema(Schema):
    """大会参加者レスポンス"""
    tournament_id = fields.Int(required=True)
    participants = fields.List(
        fields.Nested(TournamentParticipantSchema),
        required=True,
        description="大会に登録されているプレイヤー一覧",
    )
    errors = fields.List(
        fields.Dict(),
        description="登録時のエラー情報一覧",
    )
    added_count = fields.Int(description="追加された参加者の数")

