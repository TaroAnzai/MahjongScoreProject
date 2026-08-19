from enum import StrEnum

from marshmallow import Schema, fields, validate

from app.models import AccessLevel, TableTypeEnum


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
    player_id = fields.Int(required=True, validate=validate.Range(min=1))


class ParticipantBatchAddSchema(Schema):
    participants = fields.List(fields.Nested(ParticipantItemSchema), required=True, validate=validate.Length(min=1))


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


class IdempotencyHeaderSchema(Schema):
    idempotency_key = fields.Str(
        data_key="Idempotency-Key", load_default=None,
        validate=validate.Length(max=255),
        metadata={"description": "Retry key for idempotent mutation processing"},
    )


class V2ErrorSchema(Schema):
    code = fields.Str(required=True)
    message = fields.Str(required=True)
    details = fields.Dict(required=False)


class ShareLinkV2Schema(Schema):
    short_key = fields.Str(required=True)
    access_level = fields.Str(required=True, validate=validate.OneOf([item.value for item in AccessLevel]))


class PlayerV2Schema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=1))
    group_id = fields.Int(required=True, validate=validate.Range(min=1))
    name = fields.Str(required=True)


class TableV2Schema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=1))
    tournament_id = fields.Int(required=True, validate=validate.Range(min=1))
    name = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf([item.value for item in TableTypeEnum]))
    created_at = fields.Str(allow_none=True, metadata={"format": "date-time"})
    table_links = fields.List(fields.Nested(ShareLinkV2Schema))


class TournamentV2Schema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=1))
    group_id = fields.Int(required=True, validate=validate.Range(min=1))
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    rate = fields.Float(allow_none=True)
    started_at = fields.Str(allow_none=True, metadata={"format": "date-time"})
    created_at = fields.Str(allow_none=True, metadata={"format": "date-time"})
    tournament_links = fields.List(fields.Nested(ShareLinkV2Schema))


class GroupV2Schema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=1))
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.Str(allow_none=True, metadata={"format": "date-time"})
    group_links = fields.List(fields.Nested(ShareLinkV2Schema), required=True)


class CreatedTableSchema(Schema):
    client_id = fields.Str(required=True)
    table = fields.Nested(TableV2Schema, required=True)


class TournamentCreateV2ResponseSchema(Schema):
    tournament = fields.Nested(TournamentV2Schema, required=True)
    created_tables = fields.List(fields.Nested(CreatedTableSchema), required=True)


class PropagatedTableSchema(Schema):
    table_id = fields.Int(required=True, validate=validate.Range(min=1))
    type = fields.Str(required=True, validate=validate.OneOf([item.value for item in TableTypeEnum]))
    added_count = fields.Int(required=True)


class ParticipantBatchAddResponseSchema(Schema):
    tournament_id = fields.Int(required=True, validate=validate.Range(min=1))
    participants = fields.List(fields.Nested(PlayerV2Schema), required=True)
    added_count = fields.Int(required=True)
    already_registered_count = fields.Int(required=True)
    propagated_tables = fields.List(fields.Nested(PropagatedTableSchema), required=True)


class ParticipantDeletedResourceSchema(Schema):
    tournament_id = fields.Int(required=True, validate=validate.Range(min=1))
    player_id = fields.Int(required=True, validate=validate.Range(min=1))
    propagated_table_ids = fields.List(
        fields.Int(validate=validate.Range(min=1)), required=True
    )


class ParticipantDeleteResponseSchema(Schema):
    deleted = fields.Nested(ParticipantDeletedResourceSchema, required=True)


class TableDeletedResourceSchema(Schema):
    table_id = fields.Int(required=True, validate=validate.Range(min=1))
    game_count = fields.Int(required=True)
    score_count = fields.Int(required=True)
    participant_count = fields.Int(required=True)


class TableDeleteResponseSchema(Schema):
    deleted = fields.Nested(TableDeletedResourceSchema, required=True)


class GroupLookupErrorSchema(Schema):
    code = fields.Str(required=True)
    message = fields.Str(required=True)


class GroupBatchResultSchema(Schema):
    client_id = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["ok", "not_found", "forbidden", "error"]))
    group = fields.Nested(GroupV2Schema)
    error = fields.Nested(GroupLookupErrorSchema)


class GroupBatchGetResponseSchema(Schema):
    results = fields.List(fields.Nested(GroupBatchResultSchema), required=True)


class GroupDashboardResponseSchema(Schema):
    group = fields.Nested(GroupV2Schema, required=True)
    tournaments = fields.List(fields.Nested(TournamentV2Schema), required=True)
    players = fields.List(fields.Nested(PlayerV2Schema), required=True)


class PlayerScoreMapV2Schema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=1))
    name = fields.Str(required=True)
    scores = fields.Dict(keys=fields.Str(), values=fields.Float(), required=True)
    total = fields.Float(required=True)
    converted_total = fields.Float(required=True)


class TournamentScoreMapV2Schema(Schema):
    tournament_id = fields.Int(required=True, validate=validate.Range(min=1))
    tables = fields.List(fields.Nested(TableV2Schema), required=True)
    players = fields.List(fields.Nested(PlayerScoreMapV2Schema), required=True)
    rate = fields.Float(required=True)


class ParentResourceV2Schema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=1))
    name = fields.Str(required=True)


class TournamentDashboardParentSchema(Schema):
    group = fields.Nested(ParentResourceV2Schema, required=True)


class TournamentDashboardResponseSchema(Schema):
    parent = fields.Nested(TournamentDashboardParentSchema, required=True)
    tournament = fields.Nested(TournamentV2Schema, required=True)
    participants = fields.List(fields.Nested(PlayerV2Schema), required=True)
    available_group_players = fields.List(fields.Nested(PlayerV2Schema), required=True)
    tables = fields.List(fields.Nested(TableV2Schema), required=True)
    score_map = fields.Nested(TournamentScoreMapV2Schema, required=True)


class GameScoreV2Schema(Schema):
    player_id = fields.Int(required=True, validate=validate.Range(min=1))
    score = fields.Int(required=True)


class GameV2Schema(Schema):
    id = fields.Int(required=True, validate=validate.Range(min=1))
    table_id = fields.Int(required=True, validate=validate.Range(min=1))
    game_index = fields.Int(required=True)
    memo = fields.Str(allow_none=True)
    played_at = fields.Str(allow_none=True, metadata={"format": "date-time"})
    scores = fields.List(fields.Nested(GameScoreV2Schema), required=True)


class TableDashboardParentSchema(Schema):
    tournament = fields.Nested(ParentResourceV2Schema, required=True)
    group = fields.Nested(ParentResourceV2Schema, required=True)


class TableDashboardResponseSchema(Schema):
    parent = fields.Nested(TableDashboardParentSchema, required=True)
    table = fields.Nested(TableV2Schema, required=True)
    table_players = fields.List(fields.Nested(PlayerV2Schema), required=True)
    available_tournament_players = fields.List(fields.Nested(PlayerV2Schema), required=True)
    games = fields.List(fields.Nested(GameV2Schema), required=True)


# Redoc/OpenAPIに表示する利用者向けフィールド説明。
# Schema追加時に説明が不足していればimport時に検出する。
_FIELD_DESCRIPTIONS = {
    "InitialTableSchema": {
        "client_id": "クライアントが初期卓と作成結果を対応付けるための一時IDです。",
        "name": "作成する卓の表示名です。",
        "type": "卓の種類です。NORMALは通常卓、CHIPはチップ集計卓を表します。",
    },
    "TournamentCreateV2Schema": {
        "name": "作成する大会の表示名です。",
        "description": "大会の任意説明です。",
        "rate": "スコアを収支へ換算する際のレートです。",
        "initial_tables": "大会と同じトランザクションで作成する初期卓の一覧です。",
    },
    "ParticipantItemSchema": {"player_id": "大会へ追加するグループプレイヤーのIDです。"},
    "ParticipantBatchAddSchema": {
        "participants": "大会へ一括追加する参加者の一覧です。",
    },
    "GroupBatchItemSchema": {
        "client_id": "クライアントが入力と結果を対応付けるためのIDです。",
        "group_key": "取得対象グループへのアクセス権を持つ共有キーです。",
    },
    "GroupBatchGetSchema": {"items": "一括取得するグループ指定です。最大50件です。"},
    "StatusBatchItemSchema": {
        "client_id": "クライアントが入力と結果を対応付けるためのIDです。",
        "token": "状態を確認するグループ作成トークンです。",
    },
    "StatusBatchRequestSchema": {"items": "状態を一括確認するトークン指定です。最大50件です。"},
    "StatusResultSchema": {
        "client_id": "リクエストで指定された対応付け用IDです。",
        "status": "作成状態です。pending、ready、expired、invalid_tokenのいずれかです。",
        "owner_link": "作成完了時に返されるグループのオーナー共有キーです。",
    },
    "StatusBatchResponseSchema": {"results": "トークンごとの作成状態です。"},
    "IdempotencyHeaderSchema": {
        "idempotency_key": "同じ更新リクエストの再送を安全に処理するための冪等キーです。最大255文字です。"
    },
    "V2ErrorSchema": {
        "code": "クライアントがエラー種別を判定するための機械可読コードです。",
        "message": "利用者または開発者向けのエラー説明です。",
        "details": "エラーに関連する卓IDなどの追加情報です。",
    },
    "ShareLinkV2Schema": {
        "short_key": "リソースへアクセスするための短縮共有キーです。",
        "access_level": "共有キーに付与されたVIEW、EDIT、OWNERのアクセスレベルです。",
    },
    "PlayerV2Schema": {
        "id": "プレイヤーIDです。", "group_id": "プレイヤーが所属するグループIDです。",
        "name": "プレイヤーの表示名です。",
    },
    "TableV2Schema": {
        "id": "卓IDです。", "tournament_id": "卓が所属する大会IDです。", "name": "卓の表示名です。",
        "type": "卓の種類です。", "created_at": "卓作成日時です。", "table_links": "リクエストに使用したアクセスレベル以下の卓共有リンク一覧です。",
    },
    "TournamentV2Schema": {
        "id": "大会IDです。", "group_id": "大会が所属するグループIDです。", "name": "大会の表示名です。",
        "description": "大会の説明です。", "rate": "スコア換算レートです。", "started_at": "大会開始日時です。", "created_at": "大会作成日時です。",
        "tournament_links": "リクエストに使用したアクセスレベル以下の大会共有リンク一覧です。",
    },
    "GroupV2Schema": {
        "id": "グループIDです。", "name": "グループの表示名です。", "description": "グループの説明です。",
        "created_at": "グループ作成日時です。", "group_links": "グループに発行された共有リンク一覧です。",
    },
    "CreatedTableSchema": {
        "client_id": "リクエストの初期卓に指定された対応付け用IDです。", "table": "作成された卓です。",
    },
    "TournamentCreateV2ResponseSchema": {
        "tournament": "作成された大会です。", "created_tables": "大会と同時に作成された初期卓です。",
    },
    "PropagatedTableSchema": {
        "table_id": "同期対象の卓IDです。", "type": "同期対象の卓種別です。",
        "added_count": "この卓へ新たに追加された参加者数です。",
    },
    "ParticipantBatchAddResponseSchema": {
        "tournament_id": "参加者を追加した大会IDです。", "participants": "指定後の対象参加者一覧です。",
        "added_count": "大会へ新たに追加された人数です。",
        "already_registered_count": "すでに大会へ登録済みだった人数です。",
        "propagated_tables": "参加者登録を同期した卓ごとの結果です。",
    },
    "ParticipantDeletedResourceSchema": {
        "tournament_id": "参加者を削除した大会IDです。", "player_id": "削除したプレイヤーIDです。",
        "propagated_table_ids": "参加者削除を同期した卓ID一覧です。",
    },
    "ParticipantDeleteResponseSchema": {"deleted": "削除された大会参加者と同期結果です。"},
    "TableDeletedResourceSchema": {
        "table_id": "削除した卓IDです。", "game_count": "削除したゲーム数です。",
        "score_count": "削除したスコア数です。", "participant_count": "削除した卓参加者数です。",
    },
    "TableDeleteResponseSchema": {"deleted": "カスケード削除された卓と配下データの件数です。"},
    "GroupLookupErrorSchema": {"code": "検索結果単位のエラーコードです。", "message": "検索失敗の説明です。"},
    "GroupBatchResultSchema": {
        "client_id": "リクエストで指定された対応付け用IDです。", "status": "グループごとの検索状態です。",
        "group": "取得できたグループです。statusがokの場合に返します。",
        "error": "検索中のエラー情報です。statusがerrorの場合に返します。",
    },
    "GroupBatchGetResponseSchema": {"results": "指定されたグループごとの検索結果です。"},
    "GroupDashboardResponseSchema": {
        "group": "画面表示対象のグループです。", "tournaments": "グループ配下の大会一覧です。",
        "players": "グループに所属するプレイヤー一覧です。",
    },
    "PlayerScoreMapV2Schema": {
        "id": "プレイヤーIDです。", "name": "プレイヤーの表示名です。", "scores": "卓IDごとの合計スコアです。",
        "total": "全卓の合計スコアです。", "converted_total": "レートを適用した換算後の合計です。",
    },
    "TournamentScoreMapV2Schema": {
        "tournament_id": "集計対象の大会IDです。", "tables": "集計対象の卓一覧です。",
        "players": "プレイヤーごとのスコア集計です。", "rate": "換算に使用した大会レートです。",
    },
    "ParentResourceV2Schema": {
        "id": "親リソースのIDです。", "name": "親リソースの表示名です。",
    },
    "TournamentDashboardParentSchema": {
        "group": "大会が所属するグループです。",
    },
    "TournamentDashboardResponseSchema": {
        "parent": "大会の親リソースです。", "tournament": "画面表示対象の大会です。", "participants": "大会参加者一覧です。",
        "available_group_players": "グループ所属者のうち大会へ未参加のプレイヤーです。",
        "tables": "大会配下の卓一覧です。", "score_map": "大会全体のスコア集計です。",
    },
    "GameScoreV2Schema": {"player_id": "得点対象のプレイヤーIDです。", "score": "このゲームでの得点です。"},
    "GameV2Schema": {
        "id": "ゲームIDです。", "table_id": "ゲームが属する卓IDです。", "game_index": "卓内でのゲーム順です。",
        "memo": "ゲームに記録された任意メモです。", "played_at": "対局日時です。", "scores": "ゲームに登録されたプレイヤー別得点です。",
    },
    "TableDashboardParentSchema": {
        "tournament": "卓が所属する大会です。", "group": "大会が所属するグループです。",
    },
    "TableDashboardResponseSchema": {
        "parent": "卓の親リソースです。", "table": "画面表示対象の卓です。", "table_players": "現在卓へ登録されているプレイヤーです。",
        "available_tournament_players": "大会参加者のうち卓へ未登録のプレイヤーです。",
        "games": "卓で記録されたゲームとスコア一覧です。",
    },
}

for _schema_name, _descriptions in _FIELD_DESCRIPTIONS.items():
    _schema = globals()[_schema_name]
    _missing = set(_schema._declared_fields) - set(_descriptions)
    if _missing:
        raise RuntimeError(f"Missing field descriptions for {_schema_name}: {sorted(_missing)}")
    for _field_name, _description in _descriptions.items():
        _schema._declared_fields[_field_name].metadata["description"] = _description
