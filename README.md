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
│   ├── package.json
│   └── Dockerfile
├── scripts/mitmproxy/      # 通信障害を再現するアドオン・テスト・操作手順
├── .github/workflows/     # バックエンド・フロントエンドの CI/CD
├── docker-compose.yml     # API・プロキシ・DB・Redis・Celery・MailHog
└── README.md
```

## 開発環境のセットアップ

Python 3.12（venv・pip を含む）、Docker Compose、Node.js 20（CI と同じバージョン）、npm を事前にインストールしてください。以下のコマンドは bash を想定しています。

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

### 3. バックエンドと関連サービスの起動

リポジトリのルートで実行します。

```bash
docker compose up -d --build
```

MySQL の起動完了後、初回起動時やマイグレーション追加後に DB スキーマを更新します。

```bash
docker compose exec api flask --app app db upgrade
```

| サービス | 接続先・役割 |
| --- | --- |
| API（mitmproxy 経由） | http://localhost:6080 |
| Swagger UI | http://localhost:6080/doc/swagger-ui |
| OpenAPI JSON | http://localhost:6080/doc/openapi.json |
| mitmweb | http://localhost:8090 （パスワード: `mahjong`） |
| 通信障害の制御 API | http://localhost:9099 |
| MySQL | `localhost:3307`（DB: `mahjongscore`、ユーザー: `root`、パスワード: `secret`） |
| Redis | コンテナ内の `redis:6379` |
| Celery worker / beat | 非同期タスクの実行・定期タスクのスケジュール |
| MailHog | Web UI: http://localhost:8025 / SMTP: `localhost:1025` |

API コンテナは内部の5000番ポートで Gunicorn を起動し、ホストからは mitmproxy 経由でアクセスします。コンテナから MailHog への SMTP 接続先は `mailhog:1025` です。

通信の遅延・切断・エラーレスポンスを再現する手順は、[mitmproxy の README](scripts/mitmproxy/README.md) を参照してください。

### 4. フロントエンドの起動

バックエンドの起動後、別のターミナルで実行します。

```bash
cd frontend
npm ci
npm run orval
npm run dev
```

フロントエンドは http://localhost:5173/mahjong/ で開きます。

`npm run orval` は、既定で `http://localhost:6080/doc/openapi.json` を取得し、`src/api/generated/` に React Query 用の API クライアントと型を生成します。生成ファイルは Git 管理外のため、初回起動・ビルド前と API スキーマ変更後に生成してください。取得先は環境変数 `ORVAL_API_URL` で変更できます。

### 環境設定

- バックエンドは `backend/.env.secrets` を読み込んだ後、`FLASK_ENV` に応じて `.env.development`、`.env.test`（`testing`）、`.env.production` を読み込みます。Docker Compose は DB・Redis の接続先を環境変数で設定します。
- フロントエンドの API 接続先は `VITE_API_BASE_URL` です。`frontend/.env.development` では `http://localhost:6080` が設定されています。
- `npm run dev-prod-api` は `.env.prodapi` を使います。このモードは HTTPS が有効なため、`frontend/ssl/localhost.key` と `frontend/ssl/localhost.crt` が必要です。
- 開発用・テスト用の一部の `.env.*` は Git 管理されています。`backend/.env`、`backend/.env.production`、`backend/.env.secrets` は Git 管理外です。
- グループ作成メールのリンク先はバックエンドの `FRONTEND_URL` で決まります。現在の開発設定はアプリ用スキームなので、ブラウザで確認する場合は `backend/.env.secrets` などで `http://localhost:5173/mahjong` に設定し、関連サービスを再起動してください。

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
python -m pytest scripts/mitmproxy/test_network_fault.py
```

### フロントエンド

依存関係のインストールと API クライアントの生成後、`frontend/` で実行します。

```bash
npm run lint
npm run build
```

ビルド成果物は `frontend/dist/` に出力されます。`npm run preview` でビルド結果を確認できます。現在、フロントエンドのテスト実行スクリプトはありません。

## CI/CD

GitHub Actions のワークフローを配置しています。デプロイには接続先・認証情報などの GitHub Secrets 設定が必要です。

- [Backend CI/CD](.github/workflows/deploy-backend.yml): `main` への `backend/**` の変更、または手動実行で pytest を実行します。成功後に VPS 上のコード・依存関係・DB スキーマを更新し、バックエンドと Celery worker / beat の systemd サービスを再起動します。
- [Frontend CI/CD](.github/workflows/frontend.yml): `main` への `frontend/**` の変更、`main` 向けのプルリクエスト、または手動実行で API クライアント生成・lint・ビルドを行います。`main` ではビルド成果物を本番サーバーに転送します。API スキーマ取得先は Secret `ORVAL_API_URL` で指定します。
