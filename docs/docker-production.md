# MahjongバックエンドのDocker本番移行

## 調査結果と構成

旧`docker-compose.yml`はMySQL 8.0、Redis 7、Gunicorn API（内部5000）、
`app.celery_app.celery`のworker/beat、開発専用mitmproxy・MailHogで構成されていました。
workerはqueue・concurrency未指定（Celery既定の`celery` queue、CPU数依存）。
beatはAsia/Tokyo、期限切れトークンを5分間隔で削除、サマリーを24時間間隔で生成します。
サマリーはタスク名にmidnightとありますが、午前0時固定のcrontabではありません。変更していません。
APIのリミッターは既存通りプロセス内memoryです。

本番frontendは従来CIから`/home/r6441231/public_html/anzai-home.com/mahjong/`へ静的ファイルを転送していました。
実際のWebサーバー設定やAPI VPSと同一ホストかどうかはリポジトリにはありません。
frontendはDockerに含めず、GitHub ActionsでNode 22ビルド後に既存の静的配信先へ転送します。
Vite base・Router basenameは`/mahjong`、公開URLは`https://anzai-home.com/mahjong/`のままです。
API公開URLは旧frontend本番設定の`https://api.anzai-home.com/mahjong`を維持します。
OrvalクライアントはCIで既存の公開APIスキーマから生成します。

- `compose.yaml`: 共通build、DB/Redis/API/Celery、named volumes、network、healthcheckと起動依存。
- `compose.override.yaml`: 自動適用される開発用。ソースmount、Gunicorn reload、mitmproxy、MailHog、開発ポート。
- `compose.production.yaml`: 明示適用する本番用。全サービス`restart: unless-stopped`、loopback binding、Gunicorn/Celery設定。

DB/Redisは本番でportsなし。APIは`127.0.0.1:${BACKEND_PORT}:5000`です。
プロジェクト名が`mahjong-production`ならvolumeは`mahjong-production_db_data`等になります。
Dockerサービス起動待ちは[Compose公式のservice_healthy](https://docs.docker.com/compose/how-tos/startup-order/)を使用します。
API healthcheckはHTTP応答とDBのSELECT 1、DBは認証付きSQL、RedisはPINGを検証します。
APIのhealthはテーブルや業務データの正常性を保証しないため、別途migrationとWeb動作確認が必要です。
restart policyはunhealthyだけでは再起動しません。またDocker daemon再起動時にはComposeの依存順制御は再実行されません。

## 設定の一本化

ルート`.env`だけを運用します。既存のignored `backend/.env.secrets`、`.env.production`等は自動削除しませんが、コードは読みません。
必要値を安全にルートへ移し、旧ファイルはロールバック用にアクセス制限して保管してください。
新しいコードを旧systemdのcheckoutへ直接上書きせず、Docker用に別checkoutを準備してください。

Backend/API/Celeryはルート`.env`をenv_fileで受け取り、`DATABASE_URL`・Celery接続URLを共通environmentで明示します。
設定項目は`.env.example`に列挙しています（DB、SECRET_KEY、管理者認証、reCAPTCHA秘密キー、CORS、cookie、OpenAPI、SMTP、リンクURL、rate limit、Celery）。
DBにはMYSQL_*の4項目だけを渡します。Redisにはアプリの.envを渡しません。

## 1. 本番VPSの事前確認（systemdは稼働を継続）

以下はVPSで管理者が実行します。本作業では実VPS操作・データ移行は実施しません。

```bash
sudo systemctl cat mahjong_backend.service celery-worker-mahjong.service celery-beat-mahjong.service
sudo nginx -T
sudo ss -lntp
sudo systemctl is-enabled docker.service
```

unit本体・Nginx設定はリポジトリにありません。ExecStartのGunicorn worker数、timeout、bind、
Celeryのqueue・concurrency・追加オプション、EnvironmentFile、Nginx upstreamを照合してください。
既定値はリポジトリの起動方法相当であり、本番値の確認済みという意味ではありません。
特殊なworker classやrouting等がunitにあれば切替前にComposeへ反映してください。

旧backendは`~/mahjongscore-api/backend`にデプロイされていました。Docker用checkoutは別ディレクトリを使います。
旧CIのsystemd再起動・ホストDB自動upgradeは今回削除しました。実行中/予約済みworkflowも終了・停止を確認してください。; /VITE_API_BASE_URL=https://api.anzai-home.com/mahjong/d; s/API/worker/beat/frontend/API/worker/beat/

```bash
cd /path/to/docker-checkout
cp .env.example .env
chmod 600 .env
# エディタで以下を本番値へ設定
```

- `COMPOSE_PROJECT_NAME=mahjong-production`（以降固定。開発と分離）
- `FLASK_ENV=production`、`DEBUG=false`、`TESTING=false`
- MYSQL_*は専用DB認証情報。`DATABASE_URL=mysql+pymysql://<user>:<encoded-password>@db:3306/mahjongscore`
- `CELERY_BROKER_URL=redis://redis:6379/1`、`CELERY_RESULT_BACKEND=redis://redis:6379/1`
- SECRET_KEYは既存本番値を維持（セッション・署名互換）、ADMIN_*・RECAPTCHA_SECRET_KEY・SMTP_*・MAIL_*も移行
- CORS_ORIGINSは既存許可origin、SESSION_COOKIE_SECURE=true、SameSite/名前は既存本番に合わせる
- `FRONTEND_URL=https://anzai-home.com/mahjong`（メール確認リンク。末尾に/apiを付けない）
- `RATELIMIT_ENABLED=true`、`OPENAPI_URL_PREFIX=/doc`
- `VITE_API_BASE_URL=https://api.anzai-home.com/mahjong`、公開reCAPTCHAサイトキー
- GUNICORN_WORKERS/TIMEOUT、CELERY_WORKER_CONCURRENCY/QUEUESをunitと照合
以降のコマンドは同じbash・checkoutで実行します。

```bash
prod() { docker compose -f compose.yaml -f compose.production.yaml "$@"; }
# config全出力は秘密値を含む。共有ログへ出さない。
prod config --quiet
prod build
# ここではAPI/worker/beat/frontendを起動しない
prod up -d --wait db redis
prod ps
prod exec redis redis-cli ping
prod exec db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql --protocol=TCP -h db -u"$MYSQL_USER" "$MYSQL_DATABASE" -e "SELECT 1"'
```

MySQLは空volumeからDBとユーザーを作成します。初回初期化中はコンテナを再作成せず、healthcheckの完了を待ちます。DBのvolume設定名`db_data`は既存開発との互換性のため維持しています。
本番では別プロジェクト名なので専用volumeになります。`down -v`やvolume削除を本番で実行しないでください。
.envのMYSQL_*変更は既存volumeのユーザー・パスワードを変更しません。

## 2. 事前dump・restoreテスト

ホストMySQLはDocker backendの接続先にしません。ホストDBはdumpの取得にのみ使用します。
旧DB名・ユーザーを確認して指定してください。dumpは秘密情報を含むため保護します。

```bash
umask 077
mkdir -p "$HOME/mahjong-backups"
# 実際の旧DB名へ変更（system DBやCREATE DATABASE/USEは含めない）
LEGACY_DB=mahjongscore
mysqldump -h 127.0.0.1 -u root -p \
  --single-transaction --quick --routines --triggers --events \
  --no-tablespaces --set-gtid-purged=OFF --hex-blob \
  "$LEGACY_DB" > "$HOME/mahjong-backups/preflight.sql"
# dumpコマンドの成功終了とサイズを確認してからrestore
prod exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot "$MYSQL_DATABASE"' \
  < "$HOME/mahjong-backups/preflight.sql"
prod run --rm --no-deps api flask --app app db current
prod run --rm --no-deps api flask --app app db upgrade
```

事前テストではworker/beatを起動しません。SMTPによる実メール送信や定期タスクを発生させないでください。
本番DBにMyISAM等の非transaction table、MySQL EVENT、他のwriter、DEFINER付きroutineがある場合は
dumpの一貫性・移植性を別途確認します。Docker MySQLのevent_schedulerは有効化しません。
テスト後は最終restore前にDocker DBのスキーマを空に戻します。事前upgradeの余分なテーブルを残さないためです。
この操作は**切替前のDockerのテストDBだけ**が対象です。

```bash
# MYSQL_DATABASEは通常の英数字/underscoreのDB名を使う
prod exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -e "DROP DATABASE \`$MYSQL_DATABASE\`; CREATE DATABASE \`$MYSQL_DATABASE\`;"'
```

Flask-Migrate/Alembicが存在し、初期revisionからテーブルを作成します。アプリ起動にcreate_all/drop_all/upgradeはありません。
`upgrade`には既存列のenum/NOT NULL変更とscoreのDECIMAL変換が含まれるため、事前restoreで検証します。
score migrationのdowngradeはデータ損失防止のため明示的に禁止されています。機械的なdowngradeは行いません。
既存dumpには`alembic_version`も含めます。履歴がなければ安易にstampせず実スキーマと照合してください。
空DBでアプリを新規利用する場合だけ`prod run --rm api flask --app app db upgrade`で全schemaを作ります。
restore予定DBへ先にmigrationを実行する必要はありません。

## 3. 本番切替（書き込み停止後の最終dump）

1. Webをメンテナンス状態にし、他のwriter/定期jobも確認します。
2. 旧beatを止め、APIの新規受付を止めます。旧workerのactive/reserved/scheduledタスクとRedisの待機queueを確認し、
   処理完了させてからworkerを停止します。RedisのqueueはMySQL dumpに含まれません。
   未処理メール等を放置すると欠損します。purgeせず、排出・記録・再送方針を確定してください。
3. **systemd版backend/Celery/beatを全て停止し、書き込みを止めてから最終dumpを取得します。**

```bash
sudo systemctl stop celery-beat-mahjong.service
sudo systemctl stop mahjong_backend.service
# 旧EnvironmentFileが適用された旧仮想環境で、停止前に確認
# celery -A app.celery_app.celery inspect active
# celery -A app.celery_app.celery inspect reserved
# celery -A app.celery_app.celery inspect scheduled
# Redis待機queueも空になったことを確認する（inspectだけでは不十分）
sudo systemctl stop celery-worker-mahjong.service
sudo systemctl is-active mahjong_backend.service celery-worker-mahjong.service celery-beat-mahjong.service
# 3つともinactiveであること。ほかに書き込み元がないこと。
mysqldump -h 127.0.0.1 -u root -p \
  --single-transaction --quick --routines --triggers --events \
  --no-tablespaces --set-gtid-purged=OFF --hex-blob \
  "$LEGACY_DB" > "$HOME/mahjong-backups/final.sql"
# 成功終了を必ず確認。失敗したdumpはrestoreしない。
test -s "$HOME/mahjong-backups/final.sql"
sha256sum "$HOME/mahjong-backups/final.sql"
prod exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot "$MYSQL_DATABASE"' \
  < "$HOME/mahjong-backups/final.sql"
prod run --rm --no-deps api flask --app app db current
prod run --rm --no-deps api flask --app app db upgrade
# 件数・重要レコード・score精度を旧DBと比較してから起動
prod up -d --wait
```

同じタスクをsystemd版とDocker版の両方で実行しないでください。beatはDockerでも1台のみ運用します。
再起動スクリプト`backend/restart_mahjong_services.sh`もDocker版へ変更済みです。

## 4. Nginx・動作確認・disable

APIは既存Nginx upstreamと同じホストポートにbindするため、既存proxy設定を維持できます。
公開APIの`/mahjong` prefixを取り除いてFlaskへ渡す既存rewrite/proxy_passを保持してください。

frontendはComposeやコンテナnginxでは配信しません。mainブランチのFrontend CI/CDが`frontend/dist`を既存の静的配信先へSCP転送し、ホスト側の既存Webサーバーが配信します。

```bash
prod ps
prod logs --tail=100 api celery_worker celery_beat db redis
curl --fail "http://127.0.0.1:<BACKEND_PORT>/healthz"
curl --fail https://api.anzai-home.com/mahjong/healthz
curl --fail https://anzai-home.com/mahjong/
curl --fail https://anzai-home.com/mahjong/group/test-route
```
ブラウザでassets読込、deep link再読み込み、グループ作成メール/reCAPTCHA、ログインcookie、
スコア閲覧・入力・保存・共有URLを確認します。curlのHTML成功だけではAPI正常性を保証しません。
問題なければメンテナンスを解除し、旧systemdの自動起動をdisableします。

```bash
sudo systemctl disable mahjong_backend.service celery-worker-mahjong.service celery-beat-mahjong.service
sudo systemctl enable docker.service
```

Mahjong専用systemd unitは新設しません。ホストMySQL/Redisは他サービスが使っている可能性があるため停止しません。

## 5. ロールバック

**Docker切替後に書き込みがあったかどうかで手順が異なります。**

```bash
# 再度メンテナンスにし、API新規受付とbeatを停止
prod stop celery_beat api
# workerの処理完了・queue状態を確認したうえで停止
prod stop celery_worker
# Docker DBは証跡・復旧用に保持しdumpを確保
prod exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysqldump -uroot --single-transaction --quick --routines --triggers --events --no-tablespaces --set-gtid-purged=OFF "$MYSQL_DATABASE"' \
  > "$HOME/mahjong-backups/docker-rollback.sql"
```

Dockerで新しい書き込みを受ける前なら、ホストDBは最終dump時のままなので、旧checkout・旧環境設定と
バックアップ済みNginx/静的ファイルを復元し、以下で再開できます。

```bash
sudo nginx -t && sudo systemctl reload nginx
sudo systemctl start mahjong_backend.service celery-worker-mahjong.service celery-beat-mahjong.service
# disable済みの場合だけ
sudo systemctl enable mahjong_backend.service celery-worker-mahjong.service celery-beat-mahjong.service
```

Dockerで新しい書き込みが発生した後に、そのまま旧DBへ戻すとデータを失います。
メンテナンスを維持しDocker側dumpから旧側へのデータ反映とschema互換性（特にDECIMAL score）を検証してから再開します。
旧DBへの無条件上書き・Alembic downgradeは禁止です。未処理Celeryタスクも両Redis間で照合します。
互換性を確保できなければDockerを修正して復旧する方針に切り替えます。

## 既存の認証情報の扱い

旧Git管理対象の環境ファイルとDB確認スクリプトには認証値が含まれていました。
今回の変更で設定ファイルを除去し、確認スクリプトをDATABASE_URL参照へ変更していますが、
Git履歴からの削除はしていません。本番で流用していた値は管理者が影響を確認して更新してください。
署名用SECRET_KEYを変更する場合は既存セッション・発行済みリンクへの影響を考慮します。

## 実装時の検証結果（2026-09-10）

- 開発・本番の`docker compose config --quiet`成功。本番は確認用BACKEND_PORTを指定。
- Backend pytest: ホスト・最終Dockerイメージ内とも112件成功（healthcheck 2件を含む）。frontend Vitest: 90件成功。
- 通信障害アドオン: 6件成功。Compose境界検証: 2件成功。frontend lint/build成功。
- 専用の検証プロジェクトでMySQL/Redis/APIのhealthyを確認。
- 空MySQLへ全Alembic revisionを適用し、合成データのdump/restoreでレコードとhead履歴の保持を確認。upgrade再実行も成功。
- Celery ping、Redis→worker→MySQL→結果backendの実タスク往復を確認。Beatの永続scheduler起動を確認。
- Celery子プロセスで`config.Config`を読み込めない問題が実行検証で判明し、backend Dockerfileの`PYTHONPATH=/app`で修正。
- 本番VPS・既存ホストDBの移行や外部メール送信は未実施。旧開発コンテナは再作成していません。

MySQL初回初期化は検証ホストのディスクI/O待ちで約5分かかりました。
初期化途中の設定再適用で検証用DBが一度失敗したため、検証専用volumeを作り直して再確認しています。
本番で初期化中のコンテナを再作成したり、異常時に安易にvolumeを削除したりしないでください。

## 変更ファイル一覧

- `.dockerignore`
- `.env.example`
- `.github/workflows/deploy-backend.yml`
- `.github/workflows/frontend.yml`
- `.gitignore`
- `README.md`
- `backend/.dockerignore`
- `backend/.env.development`（削除）
- `backend/.env.test`（削除）
- `backend/Dockerfile`
- `backend/app/__init__.py`
- `backend/app/celery_app.py`
- `backend/app/mailer/send_test_mail.py`
- `backend/config.py`
- `backend/confirmationMySQL.py`
- `backend/environment.py`
- `backend/restart_mahjong_services.sh`
- `backend/run.py`
- `backend/tests/conftest.py`
- `backend/tests/test_health.py`
- `compose.override.yaml`
- `compose.production.yaml`
- `compose.yaml`
- `docker-compose.yml`（削除）
- `docs/docker-production.md`
- `frontend/.env.development`（削除）
- `frontend/.env.prodapi`（削除）
- `frontend/.env.production`（削除）
- `frontend/orval.config.ts`
- `frontend/src/components/PageTitleBar.tsx`
- `frontend/vite.config.js`
- `scripts/mitmproxy/README.md`
- `scripts/test_compose.py`
