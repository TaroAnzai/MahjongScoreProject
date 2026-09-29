# Docker 本番運用

本番 Compose は、リポジトリ内に MySQL を起動しません。既存の本番 `.env` の
`DATABASE_URL` で、external network `common-db-network` 上の
`common-mysql` に接続します。ユーザー名・パスワード・DB名は共通 DB 側で
払い出された値を使用し、パスワードの特殊文字は URL encode してください。

本番サーバーでは、開発用の `compose.override.yaml` を自動ロードさせないため、
常に次の2ファイルを明示します。

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  config --quiet

docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  up -d --build
```

事前に `common-db-network` と、その network 上で `common-mysql` という名前で
到達できる MySQL が必要です。Compose がこの external network や共通 DB を
作成・削除することはありません。

## 環境変数

本番 `.env` では少なくとも次を確認します。値は Git に保存しません。

- `DATABASE_URL`: host が `common-mysql` の SQLAlchemy URL
- `SECRET_KEY`: 十分に長い本番専用値
- `BACKEND_PORT`: 既存 Nginx upstream が接続する loopback port
- Celery、メール、CORS、管理者認証など既存のアプリ設定

`MYSQL_ROOT_PASSWORD`、`MYSQL_DATABASE`、`MYSQL_USER`、`MYSQL_PASSWORD` は
開発用 MySQL コンテナの初期化にだけ使用します。本番 Compose はローカル MySQL
を定義しないため、これらをコンテナ起動用設定としては参照しません。ただし、
共通 DB の運用側で同名変数を別用途に利用している場合は、その管理から削除しないでください。

## migration

起動時の自動 migration は行いません。従来どおり、バックアップと対象 revision を
確認したうえで明示的に実行します。コマンドにも本番 Compose ファイルを指定します。

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  run --rm api flask --app app db upgrade
```

`api` は本番 `.env` の `DATABASE_URL` と `common-db-network` を使用するため、
migration の接続先も `common-mysql` です。`--no-deps` による安全性には依存しません。

## 確認とロールバック

デプロイ前に merge 後モデルを確認し、`db` service、`db_data` volume、`db` への
`depends_on` がなく、API/Celery が `common-db-network` に参加していることを
確認してください。設定値を共有するときは `docker compose config` の全文を貼らず、
秘密情報をマスクしてください。

アプリのロールバックは以前の commit を checkout し、同じ2ファイルを指定して
再 build・起動します。DB migration の downgrade はデータ損失や MySQL DDL の
非トランザクション性を考慮し、migration ごとに個別判断してください。

開発 DB の `db_data` は本番モデルに含まれません。開発データを守るため、
`docker compose down -v` や volume 削除は実行しないでください。
