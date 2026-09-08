# フロントエンドのテストと調査結果

## 実行方法

```bash
cd frontend
npm ci
npm test
# 編集しながら実行する場合
npm run test:watch
```

Node.js 22.23.2 / npm 10.9.8で確認。Vitest 3・jsdom・React Testing Library・user-event・jest-domを導入した。
`vitest.config.ts`は開発サーバー設定とは独立しており、HTTPS証明書、API生成、バックエンド起動、実際のメール送信やreCAPTCHAは不要。

2026-09-09の実行結果: **52件中43件成功、9件失敗**。失敗は下記5課題の再現であり、通常の`it`として残している。`skip`や`it.fails`で成功扱いにはしていないため、現状の`npm test`は終了コード1になる。

## 対象を選んだ理由

フロントの画面・共通コンポーネント・hooks・通信処理・ユーティリティ・ルーティング・設定を確認し、リポジトリルートREADMEとバックエンドのAPIスキーマ・スコア更新サービスも参照した。データ欠落、誤った得点登録、権限、入力検証、通信障害、削除確認を優先した。

| テスト | 件数 | 対象 |
| --- | ---: | --- |
| `TableScoreBoard.test.tsx` | 13 | 通常卓の合計制約、新規/更新、CHIP、閲覧専用、取消、集計、異常入力 |
| `customFetch.test.ts` | 15 | 一般/管理API、JSON、検索条件、エクスポート、HTTP/通信エラー、管理Cookie、204 |
| `accessLevel.test.ts` | 9 | リンク未取得時のVIEW、OWNER > EDIT > VIEW、配列順序 |
| `TextInputModal.test.tsx` | 4 | 必須入力、メール検証、取消と再表示 |
| `ScoreTable.test.tsx` | 2 | 未取得表示、卓並べ替えと得点の対応、換算点、卓ID通知 |
| `AdminProtected.test.tsx` | 4 | 認証確認中、未認証、管理者のルート制御 |
| `AlertDialogProvider.test.tsx` | 3 | 確定/取消のPromise結果、通知専用表示 |
| `modalRendering.test.tsx` | 2 | 参加者選択・大会編集の描画エラー再現 |

UIのテストでは実際のコンポーネントとRadixを描画して操作する。翻訳はキー表示に固定し、通信テストではfetch、管理者ルートでは認証hookのみをモックする。生成APIの代用品や未定義の実装グローバル変数は追加していない。

全画面のE2E、単にAPIを転送するhooks、生成API、CSS、アイコン、外部ライブラリ自体の網羅テストは作成していない。生成APIのファイルはこのチェックアウトに存在せず、今回の結果は実APIとの結合やアプリ全体のビルド成功を保証しない。既存ESLintはJS/JSXのみを対象にしているため、TS/TSXの型検証の代わりにもならない。

## 再現できた課題

### BUG-01: 保存済みの0点が更新時に欠落する（1件失敗）

- 対象: `src/components/TableScoreBoard.tsx`の`handleRowClick`と`handleConfirm`。
- 再現: `[20, -20, 0, 0]`の既存ゲームを開き、変更せず確定する。
- 期待: 4人全員のスコアを同じゲームIDで送る。
- 実際: `scoreEntry?.score`の真偽判定で0が空欄になり、送信時に後ろの2人が除外される。
- 影響: バックエンドの`game_service.py`は更新時に既存スコアを削除して入力分を作り直すため、0点の参加者のスコア記録が失われる。

### BUG-02: 未完成の数値をNaNとして送信する（3件失敗）

- 対象: `src/components/TableScoreBoard.tsx`の入力検証と確定処理。
- 再現: 通常卓の空行に`-`、`.`、`-.`のいずれかを入力して確定する。
- 期待: 有限の数値になるまで更新コールバックを呼ばない。
- 実際: 合計計算では0扱いされて確定可能になり、`Number(value)`によるNaNを渡す。JSON化するとnullになる。
- 根拠: APIの`ScoreInputSchema.score`は必須の浮動小数値である。

### BUG-03: 小数の合計誤差で正しいスコアを保存できない（1件失敗）

- 対象: `src/components/TableScoreBoard.tsx`の`rowTotal !== 0`。
- 再現: `[0.1, 0.2, -0.3, 0]`を入力する。
- 期待: 数学的に合計0なので保存できる。
- 実際: 浮動小数の丸め誤差で合計が約`5.55e-17`になり、確定ボタンが無効になる。
- 補足: APIもfloatの合計と0を直接比較しているため、修正時はフロントとAPI双方で整合が必要。許容する桁数や丸め方法は別途決定が必要だが、小数第1位の合計0が拒否される現象は再現できる。

### BUG-04: 追加ヘッダー指定で既存ヘッダーが消える（2件失敗）

- 対象: `src/api/customFetch.ts`と`src/api/customFetchAdmin.ts`。
- 再現: configに独自ヘッダーとJSON本文、optionsにAuthorizationヘッダーを渡す。
- 期待: Content-Type、configの独自ヘッダー、Authorizationを併せて送る。
- 実際: 先に作ったマージ済みheadersが末尾の`...options`で丸ごと上書きされる。
- 影響: 追加ヘッダーを渡す呼び出しでJSON形式や既存の付加情報が失われる。今回のテストはラッパー単体の再現で、現在の画面からこのoptionsが渡されることまでは確認していない。

### BUG-05: 未定義のスタイル関数呼び出しで描画できない（2件失敗）

- 再現対象: `src/components/MultiSelectorModal.tsx`と`src/components/EditTournamentModal.tsx`。
- 期待: 参加者選択と大会編集の入力欄を表示できる。
- 実際: `$appButtonVariants is not defined`で描画が中断する。importした識別子は`appButtonVariants`で、`$`がない。
- 静的確認で同じ不一致がある画面: `WelcomePage.tsx`、`GroupPage.tsx`、`TablePage.tsx`、`TournamentPage.tsx`、`GroupPlayerStats.tsx`、`ContactPage.tsx`、`admin/AdminLogin.tsx`。`$containerVariants`、`$sectionVariants`等も該当する。
- 未定義変数をテスト側で補完して問題を隠すことはせず、代表の2ダイアログで再現した。

## 仕様が不明なためテストを作成していない項目

1. **日時変換の契約**: `date_utils.ts`の`toLocalDate`は「ローカル時刻に変換」と「UTCの時刻値をローカルとして解釈」の説明が混在している。`useCreateGroupRequest`ではさらに`formatLocalDateTime`へ渡している。通常の同一時点のローカル表示が目的か、時刻値をずらす特殊用途かを確認したい。日時変換と有効期限表示の期待値テストは作成していない。
2. **通常卓の人数と空欄**: 表示は4列に補完される一方、空欄を除いた少人数のスコアを送れる。3人麻雀や欠席者を許容するか、未入力と不参加をどう区別するかが不明。人数制約・一部空欄の可否はテストしていない。既存の0点保持は、この仕様と無関係なデータ保存の要件としてテストした。
3. **ゼロの集計表示**: `ScoreTable`では得点0と未登録をどちらも空欄表示する。意図した表示か確認が必要なため、その区別に対するテストは作成していない。
4. **削除・複数API操作の失敗時の方針**: 大会作成とCHIP卓作成、大会参加者とCHIP参加者追加などで、一部成功時に取り消すか、再試行するか、画面に残すかが不明。失敗時の業務上の期待結果を推測したテストは作成していない。

変更はテスト、テスト設定、package.jsonとlockfile、本レポートのみ。`src/`とバックエンドの実装コードは変更していない。
