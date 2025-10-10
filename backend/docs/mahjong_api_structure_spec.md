---
# 🧾 麻雀大会集計システム API仕様書（バックエンド構成）
---

## 🧩 システム概要

Flask + Flask-Smorest + SQLAlchemy をベースにした
麻雀大会管理・集計システムのバックエンド構成。

全リソースは `short_key` により一意に識別され、
作成時（POST）のみ親リソースキーが必要。
取得・更新・削除はリソース単体 URL で完結する。

---

## 📁 ディレクトリ構成

```
backend/
└── app/
    ├── schemas/
    │   ├── common/
    │   │   ├── base_schema.py
    │   │   ├── player_ref_schema.py
    │   │   ├── table_ref_schema.py
    │   │   └── tournament_ref_schema.py
    │   ├── group_schema.py
    │   ├── player_schema.py
    │   ├── tournament_schema.py
    │   ├── tournament_participant_schema.py
    │   ├── table_schema.py
    │   ├── table_player_schema.py
    │   ├── game_schema.py
    │   └── export_schema.py
    │
    ├── resources/
    │   ├── group_resource.py
    │   ├── player_resource.py
    │   ├── tournament_resource.py
    │   ├── tournament_participant_resource.py
    │   ├── table_resource.py
    │   ├── table_player_resource.py
    │   ├── game_resource.py
    │   └── export_resource.py
    │
    ├── services/
    │   ├── group_service.py
    │   ├── player_service.py
    │   ├── tournament_service.py
    │   ├── tournament_participant_service.py
    │   ├── table_service.py
    │   ├── table_player_service.py
    │   ├── game_service.py
    │   └── export_service.py
    │
    └── utils/
        ├── short_key_utils.py
        └── auth_utils.py
```

---

## 🧱 各レイヤーの役割

| 層                 | 役割                                                            |
| ------------------ | --------------------------------------------------------------- |
| **schemas**        | Marshmallow 定義。リクエスト・レスポンス・バリデーション。      |
| **resources**      | Flask-Smorest Blueprint 層。HTTP ルーティングとレスポンス管理。 |
| **services**       | DB 操作・業務ロジック処理。トランザクション管理もここで実施。   |
| **common/schemas** | 共通構造体（Base, Reference, Timestamp など）を集約。           |

---

## 🔑 共通設計ルール

| 項目           | 方針                                                                               |
| -------------- | ---------------------------------------------------------------------------------- |
| リソース識別子 | `short_key`（12 桁程度の英数文字列）を使用。id は内部用。                          |
| 作成(POST)時   | 親リソースキー（group_key, tournament_key 等）を URL に含める。                    |
| 取得/更新/削除 | リソース固有の `short_key` のみでアクセス可能。                                    |
| スキーマ命名   | `<entity>_schema.py`（単数形）。                                                   |
| Blueprint 命名 | `<entity>_resource.py`（複数形 Blueprint 名、単数リソースクラス名）。              |
| サービス命名   | `<entity>_service.py`。関数は `create`, `get`, `update`, `delete` を基本形に統一。 |

---

## 🧭 API ルート仕様一覧

| リソース  | HTTP   | URL                                           | 機能概要           | 実装ファイル                              |
| --------- | ------ | --------------------------------------------- | ------------------ | ----------------------------------------- |
| **Group** | POST   | `/api/groups`                                 | 新規グループ作成   | group_resource.py / group_service.py      |
|           | GET    | `/api/groups`                                 | グループ一覧取得   | 〃                                        |
|           | GET    | `/api/groups/<group_key>`                     | グループ詳細取得   | 〃                                        |
|           | PUT    | `/api/groups/<group_key>`                     | グループ更新       | 〃                                        |
|           | DELETE | `/api/groups/<group_key>`                     | グループ削除       | 〃                                        |
|           | GET    | `/api/groups/<group_key>/players`             | 所属プレイヤー一覧 | 〃                                        |
|           | POST   | `/api/groups/<group_key>/players`             | プレイヤー追加     | 〃                                        |
|           | DELETE | `/api/groups/<group_key>/players/<player_id>` | プレイヤー削除     | 〃                                        |
|           | POST   | `/api/groups/<group_key>/tournaments`         | 大会作成           | group_resource.py + tournament_service.py |
|           | GET    | `/api/groups/<group_key>/tournaments`         | グループ内大会一覧 | 〃                                        |

---

| リソース   | HTTP   | URL                        | 機能概要           | 実装ファイル                           |
| ---------- | ------ | -------------------------- | ------------------ | -------------------------------------- |
| **Player** | POST   | `/api/players`             | プレイヤー登録     | player_resource.py / player_service.py |
|            | GET    | `/api/players/<player_id>` | プレイヤー詳細取得 | 〃                                     |
|            | PUT    | `/api/players/<player_id>` | プレイヤー更新     | 〃                                     |
|            | DELETE | `/api/players/<player_id>` | プレイヤー削除     | 〃                                     |

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

| リソース | HTTP   | URL                             | 機能概要       | 実装ファイル                       |
| -------- | ------ | ------------------------------- | -------------- | ---------------------------------- |
| **Game** | POST   | `/api/tables/<table_key>/games` | 新しい対局登録 | game_resource.py / game_service.py |
|          | GET    | `/api/games/<game_key>`         | 対局詳細取得   | 〃                                 |
|          | PUT    | `/api/games/<game_key>`         | 対局更新       | 〃                                 |
|          | DELETE | `/api/games/<game_key>`         | 対局削除       | 〃                                 |

---

| リソース             | HTTP | URL                                        | 機能概要                    | 実装ファイル                           |
| -------------------- | ---- | ------------------------------------------ | --------------------------- | -------------------------------------- |
| **Export / Summary** | GET  | `/api/tournaments/<tournament_key>/export` | 大会の成績出力（CSV/Excel） | export_resource.py / export_service.py |
|                      | GET  | `/api/groups/<group_key>/summary`          | グループ集計出力            | 〃                                     |

---

## 🧩 共通スキーマ設計（`schemas/common/`）

| ファイル                   | 内容                                             |
| -------------------------- | ------------------------------------------------ |
| `base_schema.py`           | BaseResponseSchema, TimestampMixinSchema         |
| `player_ref_schema.py`     | PlayerReferenceSchema（id, name）                |
| `table_ref_schema.py`      | TableReferenceSchema（id, name, short_key）      |
| `tournament_ref_schema.py` | TournamentReferenceSchema（id, name, short_key） |

---

## ⚙️ Blueprint 登録構成（`app/api/__init__.py`）

```python
from app.extensions import api
from app.resources.group_resource import group_bp
from app.resources.player_resource import player_bp
from app.resources.tournament_resource import tournament_bp
from app.resources.tournament_participant_resource import tournament_participant_bp
from app.resources.table_resource import table_bp
from app.resources.table_player_resource import table_player_bp
from app.resources.game_resource import game_bp
from app.resources.export_resource import export_bp

def register_blueprints(app):
    api.register_blueprint(group_bp)
    api.register_blueprint(player_bp)
    api.register_blueprint(tournament_bp)
    api.register_blueprint(tournament_participant_bp)
    api.register_blueprint(table_bp)
    api.register_blueprint(table_player_bp)
    api.register_blueprint(game_bp)
    api.register_blueprint(export_bp)
```

---

## 🔒 補足仕様

- **認証**：未実装（今後 `auth_utils.py` に JWT/SSO 連携を導入予定）
- **キー生成**：`short_key_utils.py` に共通関数 `generate_short_key()` を定義
- **エラーハンドリング**：`with_common_error_responses()` デコレーターで統一
- **トランザクション管理**：`service` 層で `db.session` 管理

---
