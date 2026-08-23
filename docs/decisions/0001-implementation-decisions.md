# 実装上の決定事項

## 2026-08-17 初期実装

- ユーザー指示により Terraform と AWS リソース作成は実装対象外とする。API の Docker イメージ化までは対象とする。
- API の JSON フィールドは仕様例に合わせ camelCase、Python 内部は snake_case とする。
- 成功時は作成 API を `201`、削除・取消 API を `204` とする。
- イベントの公開・終了・キャンセルは専用 API が仕様にないため、管理者の `PATCH /events/{id}` で `status` を変更する。
- イベント削除は予約数が 0 の場合のみ物理削除する。予約履歴があるイベントは整合性維持のため拒否する。
- 一度キャンセルした予約も `(user_id, event_id)` の一意制約を保持し、同じユーザーによる再予約は許可しない。
- 管理者は公開 signup から作成せず、`python -m app.db.seed_admin` で作成または昇格する。
- 予約は PostgreSQL の条件付き atomic update、Reservation/Ticket insert を単一 transaction に含める。認証時の暗黙 read transaction は、その transaction 開始前に終了する。
- API テストは高速な SQLite で契約とユースケースを検証し、PostgreSQL 固有の migration と競合制御は Docker Compose 環境で確認する。
