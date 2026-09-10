# BUG-01〜05 修正・検証報告

対象: TaroAnzai/MahjongScoreProject。基準: main / origin/main `87f6bde`。
再開後にもfetchし、HEADとorigin/mainの差分が0であることを確認した。変更は未コミット。

## 根本原因と修正

| BUG | 根本原因 | 修正 |
| --- | --- | --- |
| 01 | 保存済みscoreのtruthy判定が0を空欄へ変換。API更新は既存スコア一覧を置き換えるため欠落がDBへ伝播する | nullish判定に変更。0は編集時に文字列`0`となり、同じgame IDで全員分を送る |
| 02 | 入力途中の文字列を確定時に無検証でNumberへ変換していた | 入力文字列と保存可能値を分離。有限性・小数桁数・DB範囲を検証し、不正ならボタン無効化と確定処理のガードで送信を防ぐ |
| 03 | Web/APIのfloatとDBのIntegerが不整合。float合計の厳密比較も誤判定を起こす | DBをNumeric(15,5)、API入力とサービス計算をDecimal、Webの保存判定を10万倍した整数の合計へ変更 |
| 04 | マージしたheadersを末尾のoptionsで上書きしていた | Headersでdefault → config → optionsの順に統合し、最後に設定。headers以外のoptions優先順位は保持 |
| 05 | import/exportにない、先頭に`$`を付けたvariant名を呼び出していた | 各ファイルのimportとmahjong.tsxのexportを照合し、該当9ファイルの参照を修正 |

## 数値契約とAPI後方互換

- 符号付き数値、小数第5位まで。整数・0も有効。
- DBは`Numeric(15, 5)`。範囲は`-9999999999.99999`〜`9999999999.99999`。
- Webは桁数と有限性を検証した後、`Math.round(score * 100000)`を合計する。epsilon判定は使用しない。
- 通常卓は正確な合計0を要求。CHIP卓の合計0制約なし、全空欄を登録しない動作、部分空欄の扱いは維持。
- APIはJSON読み取り時に`parse_float=Decimal`を使用。先にfloatへ変換すると`9999999999.000001`等が丸められ、検証を通過する問題も防いだ。
- カスタム`ScoreNumber(fields.Float)`は入力を検証済みDecimalに変換し、出力にはFloatの数値シリアライズを使用する。文字列・bool・非有限値・精度超過・範囲超過は入力エラー。
- サービス層でも正規化を行い、Decimalで合計・順位比較・保存を行う。小数を黙って丸めて保存しない。
- 既存のゲーム作成・取得・更新APIを使用し、新規V2ゲームAPIは追加していない。
- 既存のexport_serviceとv2_serviceには、DBのDecimalとfloatレートの乗算によるTypeErrorを防ぐため、レートを`Decimal(str(rate))`へ変換する修正だけを加えた。換算結果を小数第2位へ丸める既存仕様は維持。

| 境界 | scoreの型 |
| --- | --- |
| JSON入力・出力 | number |
| OpenAPI | number |
| Orval | `score: number` |
| サービス・SQLAlchemy取得値 | Decimal |
| MySQL | DECIMAL(15,5) NOT NULL |

現行アプリからOpenAPIを出力し、既存の`ORVAL_API_URL=/tmp/mahjong-openapi.json npm run orval`で再生成した。generatedファイルは直接編集していない。生成物は既存のgitignore対象で、変更ファイル一覧には含まれない。

## DB migration

追加revision: `e5a103bc9201`、親revision: `cd831af184a2`。
`tbl_scores.score`のみをINTEGERからNUMERIC(15,5)へ変更し、NOT NULLを維持する。
MySQLでは既存行を保持するALTERとなり、DB削除・初期化は行わない。

Downgradeは常にRuntimeErrorで拒否する。小数だけでなく、旧INT範囲を超えた整数も格納可能になるため、無条件な整数化は安全ではない。整数型へ戻す場合は書き込み停止、全件の整数性・INT範囲検証、バックアップを含む別途レビュー済みのmigrationが必要。自動的な切り捨て・丸めは行わない。

本番適用は未実施。既存READMEの適用手順は`docker compose exec api flask --app app db upgrade`。MySQLのDDLは通常のトランザクションで取り消せないため、適用前にバックアップとALTERの実行時間・ロック影響を確認する必要がある。

### migration検証結果

1. 実DBボリューム`mahjongscoreproject_db_data`を読み取り専用でコピーし、ネットワーク公開なしの独立したMySQL 8.0で確認した。元DBのscoreは`int NOT NULL`、revisionは`84926889b30b`だった。
2. 複製へ、現在revisionからheadまでのAlembic生成SQLを適用。`decimal(15,5) NOT NULL`、revision `e5a103bc9201`となった。全2件について、score ID・game ID・player ID・score値を適用前後で比較し、全行一致した。
3. 別の独立したMySQL 8.0検証DBでも既存Alembic全履歴を適用後、関連するGroup/Tournament/Table/Game/Playerと整数スコアを作成し、新migrationを適用。外部キーを含めデータ保持を確認した。
4. `100, 0, -100, 25000, -12000`とINT境界値`2147483647, -2147483648`が同じ数値として保持されることを確認。`-12.34567`および`0.00001`の小数保存も確認した。
5. SQLiteの通常pytestにもmigration回帰テストを追加。precision/scale/NOT NULL、整数保持、小数保存、downgrade拒否を確認した。SQLiteの生SQL結果はfloatになり得るため、テストではSQLAlchemyのNumeric型付き取得でDecimalを確認する。

元の既存DB・ボリュームは変更していない。今回作成した検証用コンテナ2個と名前付きコピーボリュームは削除済み。

## テスト一覧・結果

| 対象 | 追加・変更内容 |
| --- | --- |
| frontend/tests/TableScoreBoard.test.tsx | 既存BUG-01〜03を維持。編集時0表示を明示確認。第5位許可・第6位拒否・合計0.00001拒否・CHIPでの未完成入力とNaN/Infinity拒否を追加 |
| frontend/tests/customFetch.test.ts | 既存の期待するヘッダー値を維持し、Headers.getで検証。Headers/タプル形式、優先順位、method/body/signal/credentialsの上書き動作、追加ヘッダー時のadmin credentialsを確認 |
| frontend/tests/pageRendering.test.tsx | Welcome/Group/Table/Tournament/GroupPlayerStats/Contact/AdminLoginの7画面を実コンポーネント・実hook・実variantでrender。サーバーデータはQueryClientへ投入し、未定義変数の補完は行わない |
| frontend/tests/modalRendering.test.tsx | 既存の2モーダルのrenderテストを変更せず成功 |
| backend/tests/test_decimal_scores.py | POST/PUTで整数・小数・第5位・合計0・合計不一致・第6位・JSON number・DB Decimal・game ID保持を検証。CHIP、OpenAPI、無効入力、raw JSON精度超過・非有限値の拒否と既存全行保持も確認 |
| backend/tests/test_score_migration.py | 上記SQLite migration回帰テスト |

| コマンド | 最終結果 |
| --- | --- |
| `npm test` | 9ファイル、70件成功 |
| `npm run lint` | 成功 |
| `npm run build` | 成功。500kB超のchunk警告あり |
| backendの`../.venv/bin/pytest -p no:cacheprovider` | 110件成功。全テストを実行し、sandbox外へのpytestキャッシュ書き込みだけを無効化 |
| Orval生成 | 成功。グローバルprettier未インストールの警告あり |
| MySQL migration | ALTER・全履歴からの更新・既存DB複製の全行保持が成功 |
| `git diff --check` / 未定義variant横断検索 | 問題なし / `$xxxVariants`参照なし |

既存の正常系の期待値は削除・緩和していない。デザインや画面構成の変更は行っていない。

## 変更ファイル一覧

Backend:

- app/api/resources/game_resource.py
- app/api/resources/table_resource.py
- app/api/schemas/game_schema.py
- app/api/score_parser.py（追加）
- app/api/services/game_service.py
- app/api/services/export_service.py
- app/api/services/v2_service.py
- app/models.py
- app/utils/score_utils.py（追加）
- migrations/versions/e5a103bc9201_score_decimal.py（追加）
- tests/test_decimal_scores.py（追加）
- tests/test_score_migration.py（追加）

Frontend:

- src/api/customFetch.ts
- src/api/customFetchAdmin.ts
- src/components/TableScoreBoard.tsx
- src/components/MultiSelectorModal.tsx
- src/components/EditTournamentModal.tsx
- src/pages/WelcomePage.tsx
- src/pages/GroupPage.tsx
- src/pages/TablePage.tsx
- src/pages/TournamentPage.tsx
- src/pages/GroupPlayerStats.tsx
- src/pages/ContactPage.tsx
- src/pages/admin/AdminLogin.tsx
- tests/TableScoreBoard.test.tsx
- tests/customFetch.test.ts
- tests/pageRendering.test.tsx（追加）
- BUGFIX_REPORT.md（本報告、追加）

## 意図的に変更しなかった仕様判断事項

- date_utils.tsの日時変換契約。
- 通常卓の参加人数、3人麻雀、欠席者、未入力と不参加の区別。
- ScoreTableの0点と未登録を空欄表示する動作。
- 複数API操作が途中失敗した場合のrollback/retry/部分成功の扱い。
