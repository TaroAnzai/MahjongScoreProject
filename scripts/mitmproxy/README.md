# network_fault.py 使用方法

`network_fault.py` は、開発・E2E テスト時に API 通信の障害を再現するための
mitmproxy アドオンです。次の状態を、実行中に制御 API から切り替えられます。

- 通常通信
- オフライン（接続を切断）
- すべての API リクエストに HTTP 500 を返す
- request-link の pending status を、指定した対象だけ `expired` に上書きする

設定はメモリ上にだけ保持されます。mitmproxy コンテナを再起動すると、モードは
`normal` に戻り、expired の指定もすべて消去されます。

## 起動

リポジトリのルートで、API と mitmproxy を起動します。

```bash
docker compose up -d api mitmproxy
```

既存の `docker-compose.yml` では、次のポートを使用します。

| URL | 用途 |
| --- | --- |
| `http://localhost:6080` | mitmproxy 経由の API 入口 |
| `http://localhost:8090` | mitmweb GUI（パスワード: `mahjong`） |
| `http://localhost:9099` | 障害を切り替える制御 API |

障害を適用するには、クライアントの API ベース URL をバックエンドへ直接向けず、
`http://localhost:6080` に向けてください。

現在のモードは次のコマンドで確認できます。

```bash
curl http://localhost:9099/mode
```

初期状態では `{"mode": "normal"}` が返ります。

## 通信モード

### 通常通信

リクエストを通常どおりバックエンドへ転送します。

```bash
curl -X POST http://localhost:9099/mode/normal
```

### オフライン

mitmproxy が受け取った接続を切断し、ネットワークに接続できない状態を再現します。

```bash
curl -X POST http://localhost:9099/mode/offline
```

### HTTP 500

すべての API リクエストに、次のレスポンスを返します。

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{"message":"Internal Server Error"}
```

設定コマンド:

```bash
curl -X POST http://localhost:9099/mode/500
```

テスト後は、ほかの操作に影響しないよう `normal` に戻してください。

```bash
curl -X POST http://localhost:9099/mode/normal
```

## pending status を expired にする

通常通信を維持したまま、次のエンドポイントの成功レスポンスだけを書き換えられます。

```text
POST /api/v2/groups/request-link/status:batch
```

指定方法は `token` または `client_id` のどちらか一方です。

### token で指定

```bash
curl -X POST http://localhost:9099/pending-status/expired \
  -H 'Content-Type: application/json' \
  -d '{"token":"対象のtoken"}'
```

リクエストの `items` に含まれる token から対応する `client_id` を特定し、その
`client_id` のレスポンスを `status: "expired"` に変更します。

### client_id で指定

```bash
curl -X POST http://localhost:9099/pending-status/expired \
  -H 'Content-Type: application/json' \
  -d '{"client_id":"対象のclient_id"}'
```

指定した `client_id` のレスポンスを `status: "expired"` に変更します。対象結果に
`owner_link` がある場合は削除されます。それ以外の結果とレスポンスヘッダーは維持
されます。

指定は追加式で、複数回呼び出すと対象が蓄積します。現在の指定は次のコマンドで
確認できます。

```bash
curl http://localhost:9099/pending-status
```

レスポンス例:

```json
{
  "expiredTokens": ["token-a"],
  "expiredClientIds": ["client-id-b"]
}
```

すべての指定を解除するには、JSON オブジェクトを送信します。

```bash
curl -X POST http://localhost:9099/pending-status/reset \
  -H 'Content-Type: application/json' \
  -d '{}'
```

この上書きが行われるのは、通信モードが `normal` で、対象エンドポイントから
HTTP 200 が返った場合だけです。`offline` または `500` モードでは適用されません。

## 制御 API 一覧

| メソッド | パス | 説明 |
| --- | --- | --- |
| `GET` | `/mode` | 現在の通信モードを取得 |
| `POST` | `/mode/normal` | 通常通信へ切り替え |
| `POST` | `/mode/offline` | 接続切断へ切り替え |
| `POST` | `/mode/500` | HTTP 500 応答へ切り替え |
| `GET` | `/pending-status` | expired 対象の一覧を取得 |
| `POST` | `/pending-status/expired` | token または client_id を expired 対象に追加 |
| `POST` | `/pending-status/reset` | expired 対象をすべて解除 |

`/pending-status/expired` には、空でない文字列の `token` または `client_id` を
必ず一つだけ指定してください。両方を指定した場合や値が空の場合は HTTP 400 が
返ります。

## 動作確認とトラブルシューティング

コンテナのログを確認するには、次を実行します。

```bash
docker compose logs -f mitmproxy
```

制御 API に接続できない場合は、mitmproxy コンテナが起動していることと、ホストの
9099 番ポートが使用可能であることを確認してください。API に障害が反映されない
場合は、クライアントが 6080 番ポートを経由していることを確認してください。

アドオンのユニットテストは次のコマンドで実行できます。

```bash
python -m pytest scripts/mitmproxy/test_network_fault.py
```

制御 API はコンテナ内では `0.0.0.0:9099` で待ち受けますが、Compose のポート公開は
`127.0.0.1:9099` に限定されています。外部へ公開する環境では、認証機能がない点に
注意してください。
