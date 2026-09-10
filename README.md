# MahjongScoreProject

麻雀大会のスコア集計システムです。グループ・大会・卓・参加者の管理、スコア入力、成績集計・エクスポートなどを提供します。

フロントエンドは React + TypeScript + Vite、バックエンドは Flask + flask-smorest + MySQL で構成しています。非同期処理・定期処理には Celery + Redis を使用します。

## プロジェクト構成

```text
MahjongScoreProject/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── resources/   # API エンドポイント（管理用・v2 を含む）
│   │   │   ├── schemas/     # リクエスト・レスポンスのスキーマ
│   │   │   └── services/    # 業務ロジック
│   │   ├── mailer/          # メール送信
│   │   ├── tasks/           # Celery タスク・メールテンプレート
│   │   ├── utils/           # 認証・共有リンクなど
│   │   ├── models.py        # SQLAlchemy モデル
│   │   ├── extensions.py    # Flask 拡張の初期化
│   │   └── celery_app.py    # Celery 設定
│   ├── migrations/         # Alembic / Flask-Migrate
│   ├── tests/              # pytest によるテスト
│   ├── docs/               # API 構造の仕様書
│   ├── scripts/            # 管理用スクリプト
│   ├── config.py           # 環境別設定の読み込み
│   ├── run.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/            # 通信処理・Orval 生成先（generated/ は Git 管理外）
│   │   ├── components/     # 共通 UI コンポーネント
│   │   ├── hooks/          # API 呼び出し・状態管理
│   │   ├── pages/          # 各画面・管理画面
│   │   ├── i18n/           # 日本語・英語の翻訳
│   │   ├── assets/
│   │   ├── styles/
│   │   └── utils/
│   ├── public/
│   ├── orval.config.ts     # OpenAPI からの API クライアント生成設定
│   ├── vite.config.js
│   └── package.json
├── scripts/mitmproxy/      # 通信障害を再現するアドオン・テスト・操作手順
├── .github/workflows/     # バックエンド・フロントエンドの CI/CD
├── compose.yaml           # 共通サービス
├── compose.override.yaml  # 開発用（自動適用）
├── compose.production.yaml # 本番用（明示適用）
└── README.md
```

## 開発環境のセットアップ

Python 3.12（venv・pip を含む）、Docker Compose、Node.js 22（CI と同じバージョン）、npm を事前にインストールしてください。以下のコマンドは bash を想定しています。

### 1. リポジトリのクローン

```bash
git clone git@github.com:TaroAnzai/MahjongScoreProject.git
cd MahjongScoreProject
```

### 2. Python 仮想環境の構築と依存パッケージのインストール

リポジトリのルートで仮想環境を作成し、バックエンドの開発・テストに使用するパッケージをインストールします。

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

新しいターミナルで Python の開発用コマンドを実行する際は、リポジトリのルートで `source .venv/bin/activate` を実行してください。Docker コンテナ内の Python 環境は、ビルド時に `backend/Dockerfile` に従って別途構築されます。

### 3. 環境変数と起動

設定ファイルはルート `.env` のみです。初回は以下を実行し、必要な設定を編集してください。

```bash
cp .env.example .env
chmod 600 .env
docker compose config --quiet
docker compose up -d
# 新規DBのみ。起動時の自動migrationは行いません。
docker compose exec api flask --app app db upgrade
```

既存開発DBを継続利用する場合、以前と同じComposeプロジェクト名・`db_data`を使用し、
`.env`の`MYSQL_ROOT_PASSWORD`と`DATABASE_URL`を既存の認証情報に合わせます。
既存volumeでは`MYSQL_USER`等の変更によるユーザー自動作成は行われません。
`docker compose down -v` はデータを削除するため実行しないでください。

| サービス | 接続先 |
| --- | --- |
| Frontend（ホストのVite） | http://localhost:5173/mahjong/ |
| API（mitmproxy） | http://localhost:6080 |
| Swagger / OpenAPI | http://localhost:6080/doc/swagger-ui / http://localhost:6080/doc/openapi.json |
| mitmweb / 障害制御API | http://localhost:8090 / http://localhost:9099 |
| MySQL（開発のみ） | 127.0.0.1:3307 |
| MailHog UI / SMTP | localhost:8025 / localhost:1025 |

APIはGunicornのreloadを使用します。フロントエンドはホスト上のViteで起動します。Celeryは従来通りコードをマウントし、変更時はworker/beatを再起動します。
コンテナからのSMTPは`mailhog:1025`です。通信障害機能は[scripts/mitmproxy/README.md](scripts/mitmproxy/README.md)を参照してください。

### 4. フロントエンドの起動

```bash
cd frontend
npm ci
npm run orval
npm run dev
```

Viteはルート`.env`の`VITE_*`のみを公開します。旧`FRONTEND_URL`のブラウザ参照は
`VITE_SHARE_ORIGIN`へ移しました（backend用`FRONTEND_URL`とは独立）。
`npm run dev-prod-api`を使用する場合もルート`.env`の`VITE_API_BASE_URL`と
`VITE_USE_HTTPS=true`を設定し、従来通り`frontend/ssl/localhost.key`と`.crt`を用意してください。
Orvalの取得先を変更する場合は`ORVAL_API_URL=... npm run orval`で明示できます。

バックエンドの本番構成・環境変数・移行・切替・ロールバックは[Docker本番移行手順](docs/docker-production.md)を参照してください。

## テスト・ビルド

### バックエンド

セットアップ済みの仮想環境を有効化し、リポジトリのルートから実行します。

```bash
source .venv/bin/activate
cd backend
python -m pytest
```

`backend/pytest.ini` により `backend/tests/` を対象に実行します。API テストは SQLite のインメモリ DB を使用します。

通信障害アドオンのテストは、同じ仮想環境でリポジトリのルートから実行します。

```bash
python -m pytest scripts/mitmproxy/test_network_fault.py scripts/test_compose.py
```

### フロントエンド

依存関係のインストールと API クライアントの生成後、`frontend/` で実行します。

```bash
npm test
npm run lint
npm run build
```

ビルド成果物は `frontend/dist/` に出力されます。`npm run preview` でビルド結果を確認できます。`npm test`でVitestを実行します。

## CI/CD

GitHub ActionsはbackendのpytestとfrontendのOrval生成・test・lint・buildを行います。mainブランチのfrontendビルド成功後、distを既存の静的配信先へSCP転送します。
frontend CIの公開reCAPTCHAキーは
Repository variable `VITE_RECAPTCHA_SITE_KEY`、スキーマ取得先は既存Secret `ORVAL_API_URL`を使用します。
