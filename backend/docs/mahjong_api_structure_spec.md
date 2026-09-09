---
# 📏 麻雀大会集計システム API仕様書（更新版）

最終更新日: 2026-09-09（JST）

今回の記述の対象実装: [`4e28e409cb1cbe2ad4c3511d96246ab0747839fc`](https://github.com/TaroAnzai/MahjongScoreProject/commit/4e28e409cb1cbe2ad4c3511d96246ab0747839fc)

外部システムでゲームAPIを利用する場合は、[2026-09-09 小数スコアAPI変更説明書](changes/2026-09-09_decimal_score_api.md)を参照してください。入力例、エラー、既存クライアントへの影響、DB移行、実装コミットをまとめています。

本書は主要APIの構成概要です。全エンドポイントと詳細スキーマは対象環境のOpenAPIを参照してください。今回の更新はゲームスコア契約と関連構成の訂正であり、既存のV2 API全体を再定義するものではありません。
---

## 🧩 システム概要

Flask + Flask-Smorest + SQLAlchemy をベースにした
麻雀大会管理・集計システムのバックエンド構成。

Group / Tournament / TableへのアクセスにはShareLinkの`short_key`を使用します。
Playerは親グループキーとplayer ID、Gameは親卓の`table_key`と数値の`game_id`をURLに指定します。
共有リンクがモデル上に存在することと、そのキーを単独で受け取るHTTPエンドポイントが存在することは同義ではありません。

---

## 🗁 ディレクトリ構成

```text
backend/
├── app/
│   ├── __init__.py              # create_app / Api初期化
│   ├── extensions.py            # db / migrateなど
│   ├── models.py                # Score.score: Numeric(15, 5)
│   ├── api/
│   │   ├── __init__.py          # register_blueprints(api)
│   │   ├── score_parser.py      # 卓・ゲームのJSON数値をDecimalで読み取る
│   │   ├── schemas/             # game_schema.py / common_schemas.pyなど
│   │   ├── resources/           # table_resource.py / game_resource.pyなど
│   │   └── services/            # game_service.py / export_service.pyなど
│   └── utils/
│       ├── score_utils.py       # スコアの精度・範囲・有限性検証
│       ├── share_link_utils.py
│       └── auth.py
├── migrations/versions/         # Alembic revision
├── tests/                      # API / サービス / migration回帰テスト
└── docs/
    ├── mahjong_api_structure_spec.md
    └── changes/                # 日付・実装コミット別の変更説明書
```

---

## 🧱 各レイヤーの役割

| 層                 | 役割                                                            |
| ------------------ | --------------------------------------------------------------- |
| **schemas**        | Marshmallow 定義。リクエスト・レスポンス・バリデーション。      |
| **resources**      | Flask-Smorest Blueprint 層。HTTP ルーティングとレスポンス管理。 |
| **services**       | DB 操作・業務ロジック処理。トランザクション管理もここで実施。   |
| **schemas/common_schemas.py** | ShareLinkSchema / UTCDateTime / MessageSchema / ErrorResponseSchemaなど。 |
| **score_parser / score_utils** | JSON読み取り時のDecimal化と、スコアの正確な精度検証。 |

---

## 🔑 共通設計ルール

| 項目           | 方針                                                          |
| -------------- | ------------------------------------------------------------- |
| リソース識別子 | 共有リンクキー、または親キーと数値ID。リソースごとのURLを参照 |
| 作成(POST)時   | 親リソースキー（group_key, tournament_key 等）を URL に含める |
| 取得/更新/削除 | Gameは`table_key`と`game_id`が必要。全リソース共通のキー単独方式ではない |
| スキーマ命名   | `<entity>_schema.py`（単数形）                                |
| Blueprint 命名 | `<entity>_resource.py`（複数形 Blueprint 名）                 |
| サービス命名   | `<entity>_service.py`                                         |

---

## 🧭 API ルート仕様一覧

| リソース  | HTTP   | URL                                   | 機能概要           | 実装ファイル                              |
| --------- | ------ | ------------------------------------- | ------------------ | ----------------------------------------- |
| **Group** | POST   | `/api/groups`                         | 新規グループ作成   | group_resource.py / group_service.py      |
|           | GET    | `/api/groups/<group_key>`             | グループ詳細取得   | 〃                                        |
|           | PUT    | `/api/groups/<group_key>`             | グループ更新       | 〃                                        |
|           | DELETE | `/api/groups/<group_key>`             | グループ削除       | 〃                                        |
|           | POST   | `/api/groups/<group_key>/tournaments` | 大会作成           | group_resource.py + tournament_service.py |
|           | GET    | `/api/groups/<group_key>/tournaments` | グループ内大会一覧 | 〃                                        |

---

| リソース   | HTTP   | URL                                           | 機能概要           | 実装ファイル                           |
| ---------- | ------ | --------------------------------------------- | ------------------ | -------------------------------------- |
| **Player** | GET    | `/api/groups/<group_key>/players`             | 所属プレイヤー一覧 | player_resource.py / player_service.py |
|            | POST   | `/api/groups/<group_key>/players`             | プレイヤー追加     | 〃                                     |
|            | DELETE | `/api/groups/<group_key>/players/<player_id>` | プレイヤー削除     | 〃                                     |
|            | GET    | `/api/groups/<group_key>/players/<player_id>` | プレイヤー詳細取得 | 〃                                     |
|            | PUT    | `/api/groups/<group_key>/players/<player_id>` | プレイヤー更新     | 〃                                     |

---

| リソース       | HTTP   | URL                                        | 機能概要     | 実装ファイル                                   |
| -------------- | ------ | ------------------------------------------ | ------------ | ---------------------------------------------- |
| **Tournament** | POST   | `/api/groups/<group_key>/tournaments`      | 大会作成     | tournament_resource.py / tournament_service.py |
|                | GET    | `/api/tournaments/<tournament_key>`        | 大会取得     | 〃                                             |
|                | PUT    | `/api/tournaments/<tournament_key>`        | 大会更新     | 〃                                             |
|                | DELETE | `/api/tournaments/<tournament_key>`        | 大会削除     | 〃                                             |
|                | GET    | `/api/tournaments/<tournament_key>/export` | 大会成績出力 | export_resource.py / export_service.py         |

---

| リソース                  | HTTP   | URL                                                          | 機能概要       | 実装ファイル                                                           |
| ------------------------- | ------ | ------------------------------------------------------------ | -------------- | ---------------------------------------------------------------------- |
| **TournamentParticipant** | GET    | `/api/tournaments/<tournament_key>/participants`             | 大会参加者一覧 | tournament_participant_resource.py / tournament_participant_service.py |
|                           | POST   | `/api/tournaments/<tournament_key>/participants`             | 参加者登録     | 〃                                                                     |
|                           | DELETE | `/api/tournaments/<tournament_key>/participants/<player_id>` | 参加者削除     | 〃                                                                     |

---

| リソース  | HTTP   | URL                                           | 機能概要           | 実装ファイル                         |
| --------- | ------ | --------------------------------------------- | ------------------ | ------------------------------------ |
| **Table** | POST   | `/api/tournaments/<tournament_key>/tables`    | 卓作成             | table_resource.py / table_service.py |
|           | GET    | `/api/tables/<table_key>`                     | 卓取得             | 〃                                   |
|           | PUT    | `/api/tables/<table_key>`                     | 卓更新             | 〃                                   |
|           | DELETE | `/api/tables/<table_key>`                     | 卓削除             | 〃                                   |
|           | GET    | `/api/tables/<table_key>/players`             | 卓内プレイヤー一覧 | 〃                                   |
|           | POST   | `/api/tables/<table_key>/players`             | 卓プレイヤー追加   | 〃                                   |
|           | DELETE | `/api/tables/<table_key>/players/<player_id>` | 卓プレイヤー削除   | 〃                                   |
|           | GET    | `/api/tables/<table_key>/games`               | 卓内対局一覧       | 〃                                   |

---

| リソース        | HTTP   | URL                                           | 機能概要           | 実装ファイル                                       |
| --------------- | ------ | --------------------------------------------- | ------------------ | -------------------------------------------------- |
| **TablePlayer** | GET    | `/api/tables/<table_key>/players`             | 卓内プレイヤー取得 | table_player_resource.py / table_player_service.py |
|                 | POST   | `/api/tables/<table_key>/players`             | 卓内プレイヤー登録 | 〃                                                 |
|                 | DELETE | `/api/tables/<table_key>/players/<player_id>` | 卓プレイヤー削除   | 〃                                                 |

---

| リソース | HTTP | URL | 機能 / 成功ステータス | 実装ファイル |
| --- | --- | --- | --- | --- |
| **Game** | POST | `/api/tables/<table_key>/games` | 対局作成 / 201 | table_resource.py / game_service.py |
| | GET | `/api/tables/<table_key>/games` | 対局一覧 / 200 | table_resource.py / game_service.py |
| | GET | `/api/tables/<table_key>/games/<game_id>` | 対局詳細 / 200 | game_resource.py / game_service.py |
| | PUT | `/api/tables/<table_key>/games/<game_id>` | 対局更新 / 200 | game_resource.py / game_service.py |
| | DELETE | `/api/tables/<table_key>/games/<game_id>` | 対局削除 / 200 | game_resource.py / game_service.py |

旧記載の`/api/games/<game_key>`は上記実装のURLではありません。今回の変更で新規V2ゲームAPIへの切り替えは不要です。

### ゲームスコアの公開契約（2026-09-09更新）

- `scores`の各要素は`{"player_id": 1, "score": 1.5}`。`score`はリクエスト・レスポンスともにJSON numberです。
- 符号付き、小数第5位まで正確に表現可能な有限数値を許可します。範囲は`-9999999999.99999`〜`9999999999.99999`。整数・0も有効です。
- `1.123456`のような精度超過、範囲超過、文字列、null、bool、NaN、Infinityは保存しません。暗黙の切り捨て・丸めは行いません。
- NORMAL卓はスコア合計が正確に0である必要があります。`[0.1, 0.2, -0.3, 0]`は許可し、`[0.1, 0.2, -0.29999, 0]`は拒否します。CHIP卓には合計0の制約はありません。
- POSTでは非空の`scores`一覧が必要です。PUTで`scores`を省略した場合はスコアを変更しません。指定した場合は差分更新ではなく既存一覧の置換です。保持する全員分を、0点も含めて同じgame IDへ送信してください。
- スキーマの入力エラーは422、サービスの合計不一致は400です。詳細は[変更説明書のエラー仕様](changes/2026-09-09_decimal_score_api.md#エラーと入力検証)を参照してください。
- JSON number / OpenAPI `number` / Orval `score: number`を維持します。内部ではDecimal、DBでは`Numeric(15, 5)`です。

この更新では参加人数・欠席・未入力と不参加の区別は新たに定義していません。

---

| リソース             | HTTP | URL                                        | 機能概要                    | 実装ファイル                           |
| -------------------- | ---- | ------------------------------------------ | --------------------------- | -------------------------------------- |
| **Export / Summary** | GET  | `/api/tournaments/<tournament_key>/export` | 大会の成績出力（CSV/Excel） | export_resource.py / export_service.py |
|                      | GET  | `/api/groups/<group_key>/summary`          | グループ集計出力            | 〃                                     |

---

## 🧩 共通スキーマ設計（`app/api/schemas/common_schemas.py`）

- UTCDateTime
- ShareLinkSchema
- MessageSchema
- ValidationErrorField / ErrorResponseSchema

---

## 🔗 共有リンク関連仕様（ShareLink リレーション命名）

各リソースは共有リンクを持ち、
リレーションは以下の命名ルールに従います。

| リソース       | モデル上のリレーション名 | スキーマ上のフィールド名 | `ShareLink.resource_type` |
| -------------- | ------------------------ | ------------------------ | ------------------------- |
| **Group**      | `group_links`            | `group_links`            | `'group'`                 |
| **Tournament** | `tournament_links`       | `tournament_links`       | `'tournament'`            |
| **Table**      | `table_links`            | `table_links`            | `'table'`                 |
| **Game**       | `game_links`             | `game_links`             | `'game'`                  |

> Player, Score, TournamentPlayer は共有リンク非対象。

---

### 📊 ShareLink スキーマ

```python
class ShareLinkSchema(Schema):
    short_key = fields.Str(required=True, description="共有アクセス用キー")
    access_level = fields.Str(
        required=True, description="アクセスレベル (VIEW/EDIT/OWNER)"
    )
    created_by = fields.Str(dump_only=True, description="作成者")
    created_at = fields.DateTime(dump_only=True, description="作成日時")
```

---

### 🗺️ 各リソーススキーマ例

```python
# フィールド構成の抜粋。完全な定義はapp/api/schemas/group_schema.pyを参照。
class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_by = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_updated_at = fields.DateTime(dump_only=True)
    group_links = fields.List(fields.Nested(ShareLinkSchema), dump_only=True)
```

Tournament / Table / Game も同様に：

- `tournament_links`
- `table_links`
- `game_links`

---

## ⚙️ Blueprint 登録構成

`app/__init__.py`で`api = Api(app)`を初期化し、`app/api/__init__.py`の`register_blueprints(api)`で各Blueprintを登録します。

```python
# ゲーム関連の抜粋。全登録はapp/api/__init__.pyを参照。
from app.api.resources.table_resource import table_bp
from app.api.resources.game_resource import game_bp


def register_blueprints(api):
    api.register_blueprint(table_bp)
    api.register_blueprint(game_bp)
```

上記2つのBlueprintは`ScoreJSONParser`を使用します。JSONの小数を先にfloatへ変換せず、Decimalとしてスキーマへ渡すことで、入力検証前の精度損失を防ぎます。ゲーム以外のフィールドはそれぞれの既存スキーマで型変換されます。

---

## 🔒 補足仕様

- **ゲーム更新権限**：卓の共有リンクでEDIT以上（EDIT / OWNER）を要求。キーの値はアクセス権を持つため公開しないでください。
- **共有リンク処理**：`app/utils/share_link_utils.py`を参照。
- **エラーハンドリング**：`with_common_error_responses()` デコレーターで統一。
- **トランザクション管理**：`service` 層で `db.session` 管理。

---
