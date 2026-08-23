# Event Ticket Sample - FastAPI

FastAPI / SQLModel / PostgreSQL と React を使った、イベント・チケット予約サービスのリファレンス実装です。認証、ロール認可、イベント管理、atomic update による残席制御、予約・発券・キャンセルを含みます。

## 構成

- `apps/api`: FastAPI、SQLModel、Alembic、pytest、Ruff
- `apps/web`: React、TypeScript、Vite、React Router
- `docker-compose.yml`: PostgreSQL、API、Web
- `docs/spec.md`: 元仕様
- `docs/decisions`: 仕様で未定義だった点の実装判断

Terraform / AWS リソースは今回の実装対象外です。

## Docker Compose で起動

```bash
docker compose up --build
```

- Web: <http://localhost:5173>
- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

ホストの PostgreSQL ポートが使用中の場合は変更できます。

```bash
POSTGRES_PORT=55432 docker compose up --build
```

API コンテナは起動時にレビュー済み Alembic migration を適用します。

## 管理者作成

公開 signup は常に `USER` を作成します。イベントを管理する `ADMIN` は API コンテナで次のコマンドを実行してください。

```bash
docker compose exec api python -m app.db.seed_admin \
  --email admin@example.com \
  --password change-me-please \
  --name Administrator
```

既存ユーザーのメールアドレスを指定すると、管理者へ昇格してパスワードを更新します。

## ホストで開発

バックエンド:

```bash
cd apps/api
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

フロントエンド:

```bash
corepack enable
pnpm install
pnpm dev
```

## 検証

```bash
cd apps/api
uv run ruff check app tests alembic
uv run pytest

cd ../..
pnpm lint
pnpm build
```

API テストは認証、管理者権限、イベント CRUD・検索・validation、予約、発券、満席、所有権、キャンセルを網羅します。SQLite を使う高速な API テストに加え、migration と PostgreSQL 固有の挙動は Docker Compose で確認できます。

## 主な API

- `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`
- `GET /events`, `GET /events/{id}`
- `POST /events`, `PATCH /events/{id}`, `DELETE /events/{id}`（ADMIN）
- `POST /events/{id}/reservations`
- `GET /me/reservations`, `GET /me/reservations/{id}`, `DELETE /me/reservations/{id}`

API の JSON は camelCase、エラーは `statusCode`, `code`, `message`, `timestamp`, `path` の共通形式です。
