# Frontend decisions

- API のベース URL は `VITE_API_URL` で指定し、未指定時は `http://localhost:8000` とする。
- API のフィールド名は仕様例に合わせた camelCase を利用する。
- Access Token はデモ UI の簡潔さを優先して `localStorage` に保存する。本番運用では HttpOnly Cookie と CSRF 対策を検討する。
- 一覧 API は配列と `{ items: [...] }` の両形式を受け入れる。
