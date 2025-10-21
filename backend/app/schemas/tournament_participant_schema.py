# app/schemas/tournament_participant_schema.py

from marshmallow import Schema, fields


class TournamentParticipantsCreateSchema(Schema):
    """大会への複数プレイヤー登録用"""
    participants = fields.List(
        fields.Nested(
            Schema.from_dict({
                "player_id": fields.Int(required=True, description="大会に登録するプレイヤーID"),
            })
        ),
        required=True,
        description="大会に登録するプレイヤー一覧",
        example=[{"player_id": 1}, {"player_id": 2}],
    )

class TournamentParticipantSchema(Schema):
    """大会参加者レスポンス"""
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
