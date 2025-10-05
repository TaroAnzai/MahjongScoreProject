# app/schemas/tournament_schema.py
from marshmallow import Schema, fields


# ---------------------------------------------------
# 共通スキーマ
# ---------------------------------------------------
class TournamentSchema(Schema):
    id = fields.Int(dump_only=True)
    group_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TournamentCreateSchema(Schema):
    """大会作成用"""
    group_id = fields.Int(required=True, description="大会を所属させるグループID")
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)


class TournamentQuerySchema(Schema):
    """クエリパラメータ（short_key）"""
    short_key = fields.Str(required=True, description="グループ共有リンクキー")


class TournamentResultSchema(Schema):
    """大会スコア結果"""
    tournament = fields.Dict()
    groups = fields.List(fields.Dict())


class ScoreSummarySchema(Schema):
    """クロステーブル用スコア"""
    players = fields.List(fields.Dict())
    tables = fields.List(fields.Dict())
