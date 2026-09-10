# ゲームAPIの小数スコア対応 — 外部システム開発者向け変更説明書

## 変更の識別情報

| 項目 | 値 |
| --- | --- |
| リポジトリ | TaroAnzai/MahjongScoreProject |
| 実装変更日 | **2026-09-09 17:05:11 +09:00（JST、コミット日時）** |
| 対象実装コミット | **`4e28e409cb1cbe2ad4c3511d96246ab0747839fc`** |
| コミット件名 | Fix score precision and frontend regression bugs |
| GitHub | [対象コミットと差分](https://github.com/TaroAnzai/MahjongScoreProject/commit/4e28e409cb1cbe2ad4c3511d96246ab0747839fc) |
| 文書作成日 | 2026-09-09（JST） |
| DB migration | `cd831af184a2` → `e5a103bc9201` |

これは**実装変更日**です。各環境のデプロイ日・migration適用日を示すものではありません。対象コミットにはフロント修正も含まれますが、本書はバックエンドAPIの変更と連携側への影響を説明します。本書自体は対象実装コミットの後に作成しています。

関連: [API構成仕様書](../mahjong_api_structure_spec.md) / [全体の修正・検証報告](../../../frontend/BUGFIX_REPORT.md)。

## 連携側で押さえる変更

既存ゲームAPIをそのまま使用し、scoreを**JSON number**で送受信してください。新しいV2ゲームAPIへの移行や、scoreの文字列化は不要です。

以前はAPIがFloat、DBがIntegerで、入力可能な小数と保存形式が一致していませんでした。今回、小数第5位まで正確に保存できるDBとDecimal計算へ統一しました。通常卓の`0.1 + 0.2 - 0.3 + 0`も正しく合計0になります。

| 項目 | 今回の契約 / 連携側の対応 |
| --- | --- |
| 有効な既存整数 | 引き続き利用可能 |
| 小数スコア | 小数第5位まで正確に表現可能な値を許可 |
| 数値範囲 | `-9999999999.99999`〜`9999999999.99999` |
| 非有限値・精度超過 | 保存せず入力エラー。クライアントで勝手に丸めて送信しない |
| `"1.5"`などの数値文字列 | 不可。以前のFloatフィールドで変換されていた入力も、現在は拒否される |
| `null`・bool | scoreとして不可 |
| JSON出力 | number。`100`と`100.0`、`1.5`などの数値表記を同じ数値として扱う。固定5桁の文字列表記は保証しない |
| 通常卓 NORMAL | 送信スコアの合計が正確に0であること |
| CHIP卓 | 合計0の制約なし。精度・型・有限性・範囲の検証は同じ |
| 更新 | 同じgame IDへ、保持したい全員のスコアを送信する。0点も省略しない |

既存の有効なJSON number契約は維持していますが、従来偶然通っていた不正な入力まで維持する変更ではありません。

## エンドポイント

| 操作 | HTTP | URL | 成功時 |
| --- | --- | --- | --- |
| 作成 | POST | `/api/tables/{table_key}/games` | 201 / Game |
| 一覧取得 | GET | `/api/tables/{table_key}/games` | 200 / Game配列 |
| 詳細取得 | GET | `/api/tables/{table_key}/games/{game_id}` | 200 / Game |
| 更新 | PUT | `/api/tables/{table_key}/games/{game_id}` | 200 / Game |
| 削除 | DELETE | `/api/tables/{table_key}/games/{game_id}` | 200 / 削除メッセージ |

`table_key`は卓の共有リンクキー、`game_id`は作成・取得レスポンスに含まれる数値IDです。作成・更新・削除はEDIT以上の共有リンクを使用します。旧構成資料の`/api/games/{game_key}`を使用しないでください。

### 作成例

`Content-Type: application/json`でPOSTします。以下のplayer IDは例示であり、対象卓に登録済みの実際のIDへ置き換えてください。

```json
{
  "scores": [
    { "player_id": 1, "score": 0.1 },
    { "player_id": 2, "score": 0.2 },
    { "player_id": 3, "score": -0.3 },
    { "player_id": 4, "score": 0 }
  ],
  "memo": "小数スコアの対局"
}
```

成功レスポンスの関連フィールド抜粋（id等は例示）:

```json
{
  "id": 10,
  "table_id": 1,
  "game_index": 1,
  "scores": [
    { "player_id": 2, "score": 0.2 },
    { "player_id": 1, "score": 0.1 },
    { "player_id": 4, "score": 0.0 },
    { "player_id": 3, "score": -0.3 }
  ]
}
```

スコアはplayer_idで対応付けてください。リクエストとレスポンスの配列順が同じであることに依存しないでください。

### 更新時の0点保持

保存済み`[20, -20, 0, 0]`を変更せず再保存する例です。`PUT /api/tables/{table_key}/games/10`へ送信します。

```json
{
  "scores": [
    { "player_id": 1, "score": 20 },
    { "player_id": 2, "score": -20 },
    { "player_id": 3, "score": 0 },
    { "player_id": 4, "score": 0 }
  ]
}
```

PUTで`scores`を指定すると、サービスは既存スコアを削除して送信一覧から再作成します。差分だけを送ると、省略したプレイヤーのスコアが失われます。`scores`を省略すればスコアは変更されません。空配列は「変更しない」と同義ではなく、現在の更新処理ではスコア一覧の消去になります。この挙動は今回変更していません。

プレイヤー数、欠席、未入力と不参加の区別は今回確定していません。本書の例は4人ですが、今回新たに4人必須の仕様を導入したものではありません。Webの全空欄はAPIを呼ばず、APIのPOSTでは非空の`scores`を要求します。

## エラーと入力検証

| 入力例 / 条件 | 結果 |
| --- | --- |
| `100`, `-100`, `0`, `1.5`, `-12.34567`, `0.00001` | score単体として有効。NORMALでは一覧合計も検証 |
| `1.123456`, `9999999999.000001`, `1.00000000000000001` | 422 / 小数精度超過 |
| `10000000000` | 422 / DB範囲超過 |
| `"1.5"`, `"NaN"`, `"Infinity"`, `null`, `true` | 422 / scoreの型・値が不正 |
| 非標準JSONの裸の`NaN`, `Infinity`, `-Infinity` | JSON number契約外。現在の実装でも422で拒否し、保存しない |
| NORMALで`[0.1, 0.2, -0.29999, 0]` | 400 / 合計が0でない |
| JSONとして壊れた本文 | JSON解析エラー。小数精度の422とは区別する |

スキーマエラーはFlask-Smorestの`errors.json`配下に項目別エラーが入り、配列要素の位置とscoreフィールドを特定できます。サービスの合計不一致は`errors.json.message`に入ります。文言の完全一致ではなく、HTTPステータスとエラー構造で処理してください。

JSON読み取り時からDecimalを使用するため、`9999999999.000001`をfloatへ丸めて整数扱いにすることはありません。検証で使うquantizeも、丸めた値を保存するためではなく元の値と一致するかの確認に使用しています。

## クライアント側の実装方針

- 編集用の文字列と保存可能な数値を分けます。空欄と0をtruthy判定で同一視しないでください。
- `-`、`.`、`-.`などは入力途中に表示しても、確定時は送信しません。
- 有限性・精度・範囲を確認してから数値へ変換し、JSON numberとして送信します。APIへDecimalの文字列表現を送らないでください。
- JavaScriptの生のfloat合計に対して`=== 0`で判定しません。第5位以内であることを確認してから10万倍の整数単位で合計するか、正確な十進演算を使います。
- JavaScriptで`Math.round(score * 100000)`を用いる場合は、個々の値と合計が安全な整数範囲内にあることを確認してください。`Math.round`を第6位以降の入力を受け入れるために使ってはいけません。
- 422や400の場合は入力修正を促し、エラーになった値を自動丸め・無条件再送しません。

型の対応:

| 境界 | 型 |
| --- | --- |
| JSON入力 / 出力 | number |
| OpenAPI ScoreInput.score | number |
| Orval ScoreInput.score | `score: number` |
| サーバー内部 / SQLAlchemy取得値 | Decimal |
| MySQL tbl_scores.score | DECIMAL(15,5) NOT NULL |

OpenAPIは対象環境の設定に従って取得してください（開発環境の既定は`/doc/openapi.json`。`OPENAPI_URL_PREFIX`等で変更可能）。既存Webの型再生成は`frontend`で`ORVAL_API_URL=<OpenAPIのURLまたはJSONファイル> npm run orval`です。生成ファイルを手修正する必要はありません。

## バックエンド内部の変更ファイル

パスはbackendからの相対パスです。

| ファイル | 変更点 |
| --- | --- |
| [app/api/score_parser.py](../../app/api/score_parser.py) | JSONの小数をDecimalで読み取るScoreJSONParserを追加 |
| [app/api/resources/table_resource.py](../../app/api/resources/table_resource.py) / [game_resource.py](../../app/api/resources/game_resource.py) | 卓・ゲームBlueprintにパーサーを適用。URLは維持 |
| [app/api/schemas/game_schema.py](../../app/api/schemas/game_schema.py) | ScoreNumberで入力Decimal化・精度検証。出力とOpenAPIはnumberを維持 |
| [app/utils/score_utils.py](../../app/utils/score_utils.py) | 型・有限性・範囲・5桁での正確な表現可能性を共通検証 |
| [app/api/services/game_service.py](../../app/api/services/game_service.py) | 作成・更新時のDecimal正規化、正確な合計・順位比較 |
| [app/models.py](../../app/models.py) | Score.scoreをNumeric(15,5)へ変更 |
| [app/api/services/export_service.py](../../app/api/services/export_service.py) / [v2_service.py](../../app/api/services/v2_service.py) | スコアとレートの乗算でDecimalとfloatのTypeErrorを防ぐ。既存の換算結果を第2位へ丸める仕様は維持 |
| [migrations/versions/e5a103bc9201_score_decimal.py](../../migrations/versions/e5a103bc9201_score_decimal.py) | データ保持型の列変更。危険なdowngradeを拒否 |
| [tests/test_decimal_scores.py](../../tests/test_decimal_scores.py) / [test_score_migration.py](../../tests/test_score_migration.py) | API・DB・OpenAPI・migration回帰テストを追加 |

既存v2_serviceの変更は既存集計への型整合修正です。V2ゲームAPIを追加した変更ではありません。

## DB適用と運用上の注意

DBがIntegerのままの環境に、小数入力を解放しないでください。デプロイ担当者は対象コミットとmigrationの適用状態をそれぞれ確認します。commitが存在するだけではDBの移行済みを意味しません。

既存READMEの適用手順（リポジトリルートで実行）:

```bash
docker compose exec api flask --app app db current
docker compose exec api flask --app app db upgrade
docker compose exec api flask --app app db current
```

変更revisionは`e5a103bc9201`、親は`cd831af184a2`です。既存の整数データを保持してscore列を変更し、NOT NULLを維持します。DB削除・作り直しは不要です。MySQLのDDLは通常のトランザクションで取り消せないため、バックアップとALTER時の書き込み停止・ロック影響を事前に確認します。

**自動downgradeは常に拒否します。** 小数の切り捨てだけでなく旧INT範囲を超えた整数でも情報損失が起こり得ます。INTEGERに戻す必要がある場合は、書き込み停止と全データ検証を伴う別途レビュー済みのmigrationを用意してください。

実装時の検証では、MySQL 8.0で既存Alembic履歴からの更新、正負整数・0・INT境界値の保持、小数第5位の保存を確認しました。既存ローカルDBの読み取り専用コピーでも全2行のID・関連ID・値が更新前後で一致しました。元DBと本番DBにはこの作業でmigrationを適用していません。

## 検証記録と変更対象外

対象実装の検証結果: backend全110件成功（`pytest -p no:cacheprovider`、キャッシュ書き込みのみ無効化）。POST/PUTの整数・小数・第5位・第6位・通常卓合計・CHIP、DB取得値のJSON number、OpenAPI、raw JSONの精度損失防止、不正入力時の既存データ保持、migrationを含みます。

関連するWeb検証: 70件成功、lint成功、build成功。これらは対象実装時の記録であり、各連携システムのテスト結果ではありません。

日時変換、参加人数・未入力と不参加、ScoreTableの0点表示、複数API操作の途中失敗に対するrollback/retry/部分成功の業務仕様は変更対象外です。
