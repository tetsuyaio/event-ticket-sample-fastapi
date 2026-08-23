# Event Ticket Reservation App - FastAPI Specification

## 1. Overview

新しいバックエンド言語・フレームワークを学習するときのリファレンス実装として利用できる、イベント・チケット予約サービスを作成する。

今回の主目的は **FastAPI を使った実践的な API 開発を一通り経験すること**。
認証・認可・DB・トランザクション・競合制御・テスト・Docker・AWS デプロイまで実装する。

フロントエンドは API の動作確認を分かりやすくするための簡易 UI として実装する。

---

# 2. Goals

- FastAPI の基本構造を理解する
- Router / Service / Repository / Dependency の責務を理解する
- Pydantic による Request / Response Schema と Validation を実装する
- メールアドレス + パスワード認証を実装する
- JWT による API 認証を実装する
- Role ベースの認可を実装する
- SQLModel + PostgreSQL を利用する
- ORM自体の深掘りは目的とせず、FastAPIでのAPI設計・認証・トランザクション等を優先する
- Alembic による DB Migration を実装する
- DB Transaction を実装する
- 同時予約時の競合を考慮する
- REST API の設計を経験する
- OpenAPI / Swagger UI を利用する
- Unit / Integration / API E2E Test を実装する
- Docker を利用したローカル開発環境を構築する
- AWS へのデプロイを想定した構成にする

---

# 3. Non Goals

初期実装では以下は対象外とする。

- 実際の決済
- OAuth / Social Login
- モバイルアプリ
- 複雑な座席指定
- QR コードによる入場管理
- メール送信
- Push 通知
- マイクロサービス化
- Event Sourcing
- CQRS の本格導入
- Redis
- Kafka / SQS などの非同期メッセージング
- Kubernetes

必要に応じて後から追加する。

---

# 4. Technology Stack

## Frontend

- TypeScript
- React
- Vite
- React Router
- fetch または Axios
- UI は最低限

## Backend

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic v2
- SQLModel
- Alembic
- PostgreSQL
- JWT Authentication
- REST API
- OpenAPI / Swagger UI

## Python Tooling

- uv
- Ruff
- pytest

Python の package / virtual environment 管理には `uv` を利用する。

## Development

- Docker
- Docker Compose
- pnpm
- pnpm workspace
- ESLint / Prettier（Frontend）
- Ruff（Backend）
- `.env`

## Infrastructure

- AWS
- Terraform
- ECR
- ECS Fargate
- ALB
- RDS PostgreSQL
- S3
- CloudFront
- CloudWatch Logs
- Secrets Manager または SSM Parameter Store

---

# 5. Monorepo

本プロジェクトは **モノレポ** とする。

```text
event-ticket-app/
├── apps/
│   ├── web/                    # Vite + React
│   │   ├── src/
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── api/                    # FastAPI
│       ├── app/
│       ├── alembic/
│       ├── tests/
│       ├── pyproject.toml
│       ├── uv.lock
│       └── Dockerfile
│
├── packages/
│   └── ...                     # 必要になった場合のみ
│
├── infra/
│   └── terraform/
│
├── docs/
│   └── specification-fastapi.md
│
├── docker-compose.yml
├── package.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
└── README.md
```

Frontend は pnpm workspace の対象とする。
Backend は Python プロジェクトなので pnpm package として無理に扱わない。

`pnpm-workspace.yaml`:

```yaml
packages:
  - "apps/web"
  - "packages/*"
```

## Monorepo Policy

- Frontend は `apps/web`
- Backend は `apps/api`
- Infrastructure は `infra/terraform`
- Frontend package manager は pnpm
- Backend package manager / virtual environment manager は uv
- 共有 package は必要になるまで作成しない
- Frontend と Backend のコードを直接共有しない
- Generic な shared package を先回りして作らない

TypeScript と Python 間で API 型を直接共有しない。
必要になった場合は FastAPI の OpenAPI Schema から TypeScript Client / Type を生成する方法を優先する。

---

# 6. Domain Model

```text
User
 ├─ Reservation
 │    └─ Ticket
 │
Event
 ├─ Reservation
 └─ Ticket
```

---

# 7. Entity Definitions

## 7.1 User

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| email | string | ログイン用メールアドレス |
| passwordHash | string | ハッシュ化済みパスワード |
| name | string | 表示名 |
| role | enum | USER / ADMIN |
| createdAt | datetime | 作成日時 |
| updatedAt | datetime | 更新日時 |

Constraints:

- email は UNIQUE
- Password の平文保存は禁止

## 7.2 Event

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| title | string | イベント名 |
| description | text | 説明 |
| venue | string | 開催場所 |
| startsAt | datetime | 開始日時 |
| endsAt | datetime | 終了日時 |
| capacity | integer | 最大人数 |
| reservedCount | integer | 現在の予約数 |
| status | enum | DRAFT / PUBLISHED / CLOSED / CANCELLED |
| createdBy | UUID | Admin User |
| createdAt | datetime | 作成日時 |
| updatedAt | datetime | 更新日時 |

Constraints:

- capacity > 0
- reservedCount >= 0
- reservedCount <= capacity
- startsAt < endsAt

## 7.3 Reservation

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| userId | UUID | User |
| eventId | UUID | Event |
| status | enum | RESERVED / CANCELLED |
| reservedAt | datetime | 予約日時 |
| cancelledAt | datetime nullable | キャンセル日時 |
| createdAt | datetime | 作成日時 |
| updatedAt | datetime | 更新日時 |

UNIQUE:

```text
(userId, eventId)
```

## 7.4 Ticket

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| reservationId | UUID | Reservation |
| ticketNumber | string | チケット番号 |
| status | enum | VALID / CANCELLED |
| issuedAt | datetime | 発行日時 |
| createdAt | datetime | 作成日時 |

Constraints:

- reservationId は UNIQUE
- ticketNumber は UNIQUE

---

# 8. Authentication

## Signup

```http
POST /auth/signup
```

```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "Test User"
}
```

処理:

1. Pydantic Validation
2. email 重複確認
3. Password Hash
4. User 作成
5. JWT 発行

## Login

```http
POST /auth/login
```

## Current User

```http
GET /auth/me
```

## JWT

```http
Authorization: Bearer <token>
```

JWT Payload 例:

```json
{
  "sub": "user-id",
  "role": "USER"
}
```

初期実装では Access Token のみ。
Refresh Token は将来拡張とする。

---

# 9. Authorization

Role:

```text
USER
ADMIN
```

ADMIN:

- Event 作成
- Event 更新
- Event 削除
- Event 公開
- Event キャンセル

USER:

- Event 閲覧
- Event 予約
- 自分の予約一覧
- 自分の予約キャンセル

FastAPI の Dependency Injection で実装する。

例:

```python
@router.post("/events")
def create_event(
    current_user: User = Depends(require_admin),
):
    ...
```

主な Dependency:

```text
get_db
get_current_user
require_admin
```

---

# 10. API Specification

## Auth

```text
POST /auth/signup
POST /auth/login
GET  /auth/me
```

## Events

```text
GET    /events
GET    /events/:id
POST   /events
PATCH  /events/:id
DELETE /events/:id
```

POST / PATCH / DELETE は ADMIN のみ。

## Event Search

```http
GET /events?keyword=nestjs&status=PUBLISHED&page=1&limit=20
```

検索条件:

```text
keyword
status
startsFrom
startsTo
page
limit
```

## Reservations

```text
POST   /events/:eventId/reservations
GET    /me/reservations
GET    /me/reservations/:id
DELETE /me/reservations/:id
```

---

# 11. Reservation Transaction

予約処理は Transaction で行う。

```text
BEGIN

1. Event を取得
2. Event.status == PUBLISHED を確認
3. 残席を確認
4. 重複予約を確認
5. Reservation INSERT
6. Ticket INSERT
7. Event.reservedCount UPDATE

COMMIT
```

途中で失敗した場合は ROLLBACK。

SQLAlchemy の `Session.begin()` などを利用する。

例:

```python
with session.begin():
    ...
```

Async SQLAlchemy を採用した場合は `AsyncSession` を利用する。

---

# 12. Concurrency Control

以下を防止する。

```text
capacity = 100
reservedCount = 99

User A reserve
User B reserve

=> reservedCount = 101 になってはいけない
```

初期実装では **Atomic Update** を利用する。

概念:

```sql
UPDATE events
SET reserved_count = reserved_count + 1
WHERE
  id = :id
  AND reserved_count < capacity;
```

更新件数が 0 の場合は `EVENT_SOLD_OUT`。

学習対象:

- Race Condition
- Lost Update
- Transaction Isolation Level
- Optimistic Lock
- Pessimistic Lock
- Atomic Update

---

# 13. Reservation Cancel Transaction

```text
BEGIN

1. Reservation 取得
2. 所有者確認
3. Reservation.status = CANCELLED
4. Ticket.status = CANCELLED
5. Event.reservedCount -= 1

COMMIT
```

---

# 14. Error Handling

共通 Error Response:

```json
{
  "statusCode": 400,
  "code": "EVENT_SOLD_OUT",
  "message": "Event is sold out",
  "timestamp": "2026-01-01T00:00:00.000Z",
  "path": "/events/xxx/reservations"
}
```

Error Code:

```text
INVALID_CREDENTIALS
EMAIL_ALREADY_EXISTS
EVENT_NOT_FOUND
EVENT_NOT_PUBLISHED
EVENT_SOLD_OUT
ALREADY_RESERVED
RESERVATION_NOT_FOUND
RESERVATION_ALREADY_CANCELLED
FORBIDDEN
UNAUTHORIZED
VALIDATION_ERROR
```

FastAPI の以下を利用する。

- `HTTPException`
- Custom Exception
- Global Exception Handler

---

# 15. Validation

Pydantic v2 を利用する。

例:

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)
```

Response Schema も Pydantic で定義する。
SQLModel Model をそのまま API Response に利用しない。

---

# 16. FastAPI Application Structure

```text
apps/api/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   └── models/
│   │       ├── user.py
│   │       ├── event.py
│   │       ├── reservation.py
│   │       └── ticket.py
│   │
│   ├── auth/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── dependencies.py
│   │
│   ├── users/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── events/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── reservations/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   └── tickets/
│       ├── schemas.py
│       ├── service.py
│       └── repository.py
│
├── alembic/
├── tests/
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

Feature / Domain 単位で分割する。

Router に Business Logic を書かない。
Service にユースケースを置く。
Repository は SQLAlchemy Query を分離するために利用する。

ただし、Repository Pattern を過剰に抽象化しない。
`BaseRepository` などの Generic Layer は作らない。

---

# 17. SQLModel / Alembic

SQLModel を開発・本番の両方で ORM / Database Model として利用する。

SQLModel は SQLAlchemy と Pydantic を基盤としているが、本プロジェクトでは ORM 自体を深く学ぶことよりも、
FastAPI を使った一般的な API 開発を一通り経験することを優先する。

構成イメージ:

```text
FastAPI
  ↓
SQLModel Session
  ↓
PostgreSQL
```

以下の Model を SQLModel で定義する。

```text
User
Event
Reservation
Ticket
```

利用する主な機能:

- `SQLModel`
- `Field`
- `Relationship`
- `Session`
- `select()`
- Unique Constraint
- Enum
- Transaction
- Pagination
- Filtering
- Sorting
- Atomic Update

## Table Model と API Schema

DB Table 用 Model と API Request / Response 用 Schema は必要に応じて分離する。

例:

```python
class UserBase(SQLModel):
    email: str
    name: str


class User(UserBase, table=True):
    id: UUID = Field(primary_key=True)
    password_hash: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID
```

DB Model をそのまま API Response として返すことは避ける。

## Alembic

DB Migration は Alembic で管理する。

開発環境:

```text
SQLModel Model 修正
    ↓
alembic revision --autogenerate -m "..."
    ↓
Migration Script
    ↓
alembic upgrade head
    ↓
Local PostgreSQL
```

migration ファイルは Git 管理する。

本番環境:

```text
CI/CD
  ↓
alembic upgrade head
  ↓
RDS PostgreSQL
  ↓
ECS Deploy
```

本番環境では migration を自動生成せず、
開発時に生成・レビュー済みの migration script のみ適用する。

## ORM Learning Policy

ORM の深い内部仕様は本プロジェクトの主目的ではない。

以下を理解できれば十分とする。

- Model 定義
- Relation
- CRUD
- Query
- Transaction
- Migration
- Unique Constraint
- Index
- Pagination
- Filtering
- 同時更新時の競合

SQLAlchemy 固有の高度な機能や複雑な Repository 抽象化は、
必要になった場合のみ追加する。

# 18. SQLAlchemy

SQLAlchemy は **開発時だけではなく本番でも利用する**。

```text
FastAPI
  ↓
SQLModel Session
  ↓
PostgreSQL
```

SQLModel Style を利用する。

利用機能:

- Declarative Model
- `Mapped`
- `mapped_column`
- `relationship`
- `Session`
- `select()`
- Transaction
- Unique Constraint
- Enum
- Pagination
- Filtering
- Sorting
- Atomic Update

Legacy Query API を積極的には利用しない。

---

# 19. Alembic

DB Migration は Alembic を利用する。

## Development

```text
SQLModel Model 修正
  ↓
alembic revision --autogenerate
  ↓
Migration Script を確認・修正
  ↓
alembic upgrade head
  ↓
Local PostgreSQL
```

Migration Script は Git 管理する。

## Production

```text
CI/CD
  ↓
alembic upgrade head
  ↓
RDS PostgreSQL
  ↓
ECS Deploy
```

本番環境で migration を自動生成しない。
開発時に作成・レビュー済みの Migration Script のみ適用する。

---

# 20. Database

PostgreSQL を使用する。

Local:

```text
Docker Compose PostgreSQL
```

AWS:

```text
Amazon RDS for PostgreSQL
```

---

# 21. Frontend

API 学習が目的なので最低限。

```text
/login
/signup
/events
/events/:id
/my/reservations
/admin/events
/admin/events/new
```

デザインには時間をかけない。

---

# 22. Swagger / OpenAPI

FastAPI が生成する OpenAPI を利用する。

```text
/docs
```

Swagger UI。

```text
/redoc
```

ReDoc。

以下を確認できるようにする。

- Request Schema
- Response Schema
- Authentication
- Status Code
- Error Response

---

# 23. Logging

Python `logging` または構造化 Logger を利用する。

最低限記録するもの:

```text
requestId
method
path
statusCode
duration
userId
```

Password / JWT / Secret はログ出力禁止。

---

# 24. Testing

pytest を利用する。

## Unit Test

対象:

```text
auth.service
events.service
reservations.service
```

## Integration Test

```text
SQLAlchemy
+ PostgreSQL
+ Repository / Service
```

## API / E2E Test

FastAPI の TestClient または httpx を利用する。

代表シナリオ:

```text
Admin Create Event
User Signup
User Login
Event List
Reserve Event
Ticket Issued
Reservation List
Cancel Reservation
```

Sold Out:

```text
capacity = 1

User A Reserve -> success
User B Reserve -> EVENT_SOLD_OUT
```

---

# 25. Local Development

```text
┌──────────────┐
│ React / Vite │
│ apps/web     │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│ FastAPI      │
│ apps/api     │
│ Docker       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PostgreSQL   │
│ Docker       │
└──────────────┘
```

Docker Compose Service:

```text
web
api
postgres
```

Frontend は Vite を Host OS で直接実行してもよい。

Backend のローカル起動例:

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload
```

---

# 26. AWS Architecture

```text
                         Internet
                            │
                            ▼
                    ┌──────────────┐
                    │  CloudFront  │
                    └──────┬───────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       ┌──────────┐                ┌───────────┐
       │    S3    │                │    ALB    │
       │ React    │                └─────┬─────┘
       │ Static   │                      │
       └──────────┘                      ▼
                                  ┌──────────────┐
                                  │ ECS Fargate  │
                                  │ FastAPI      │
                                  │ Uvicorn      │
                                  └──────┬───────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │ RDS          │
                                  │ PostgreSQL   │
                                  └──────────────┘
```

---

# 27. Frontend Infrastructure

Vite React の `dist/` を S3 に配置する。

```text
CloudFront
   ↓
S3
   ↓
React
```

- S3 Public Access は無効
- CloudFront Origin Access Control を利用
- SPA Route を `index.html` にフォールバック

---

# 28. Backend Infrastructure

FastAPI を Docker Image にする。

```text
Dockerfile
  ↓
ECR
  ↓
ECS Fargate
```

```text
Client
 ↓
ALB
 ↓
ECS Fargate
```

Application Server は Uvicorn を利用する。

ECS Task は Private Subnet に配置する。

---

# 29. Database Infrastructure

```text
ECS
 ↓
RDS PostgreSQL
```

- RDS は Private Subnet
- Public Access disabled
- Security Group で ECS からのみ PostgreSQL を許可

---

# 30. AWS Network

```text
VPC

├── Public Subnet
│   └── ALB
│
└── Private Subnet
    ├── ECS Fargate
    └── RDS PostgreSQL
```

NAT Gateway は学習環境ではコストに注意する。

本番相当と学習用の簡略構成を分けてもよい。

---

# 31. Secrets

Git に保存しないもの:

```text
DATABASE_URL
JWT_SECRET
```

AWS では以下を利用する。

```text
Secrets Manager
```

または

```text
SSM Parameter Store
```

---

# 32. Monitoring

CloudWatch Logs を利用する。

確認対象:

```text
Application Log
Container Start / Stop
Error
HTTP Request Log
```

---

# 33. Terraform

Terraform で管理する。

```text
infra/terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── modules/
│   ├── network/
│   ├── frontend/
│   ├── ecs/
│   └── database/
└── environments/
    └── dev/
```

最初から過剰な Module 分割は行わない。
可読性を優先する。

---

# 34. Implementation Phases

Codex には以下の順番で実装させる。

## Phase 1

```text
Monorepo Setup
FastAPI Setup
uv Setup
PostgreSQL
SQLAlchemy
Alembic
Docker Compose
User Model
Event Model
```

## Phase 2

```text
Signup
Login
JWT
get_current_user
Authentication Dependency
```

## Phase 3

```text
Event CRUD
Admin Role
Authorization Dependency
Pagination
Search
```

## Phase 4

```text
Reservation
Ticket
DB Transaction
```

## Phase 5

```text
Concurrency Control
Sold Out Handling
Reservation Cancel
```

## Phase 6

```text
Exception Handler
Logging
Middleware
Request ID
OpenAPI / Swagger
```

## Phase 7

```text
Unit Test
Integration Test
API / E2E Test
```

## Phase 8

```text
React UI
```

## Phase 9

```text
Terraform
AWS Deployment
Alembic Production Migration
```

---

# 35. Definition of Done

以下が動けば一旦完成。

- User Signup
- User Login
- JWT Authentication
- Admin Authorization
- Event CRUD
- Event Search
- Pagination
- Event Reservation
- Ticket Issue
- Reservation Transaction
- Concurrent Reservation Protection
- Reservation Cancel
- OpenAPI / Swagger
- Common Error Response
- Logging
- Unit Test
- Integration Test
- API / E2E Test
- React UI
- Docker Compose
- Alembic Migration
- Terraform
- AWS Deployment

---

# 36. Codex Implementation Policy

- 仕様を勝手に変更しない
- FastAPI / SQLModel の標準的で分かりやすい設計を優先する
- Feature / Domain-based directory structure を利用する
- Router に Business Logic を書かない
- Service にユースケースを置く
- SQLAlchemy Query は Repository または Service 層に閉じ込める
- Request / Response に Pydantic Schema を利用する
- Pydantic Validation を省略しない
- Transaction が必要な処理は必ず Transaction を利用する
- Password / Secret / JWT をログ出力しない
- Python の型ヒントを原則付与する
- `Any` を安易に使用しない
- 過剰な抽象化を避ける
- Generic BaseService / BaseRepository は作らない
- SQLModel Style を利用する
- SQLAlchemy Legacy Query API は原則使用しない
- SQLModel は開発・本番の両方で利用する
- Alembic Migration は Git 管理する
- 本番では `alembic upgrade head` で Migration を適用する
- Python の package / environment 管理には uv を利用する
- 実装と同時に必要な Test を追加する
- モノレポ構成は `apps/web` と `apps/api` を基本とする
- 不要な shared package を先に作らない

---

# 37. Future Extensions

```text
Refresh Token
Email Verification
Password Reset
Rate Limit
Redis Cache
SQS
EventBridge
SES
Payment
Seat Reservation
QR Ticket
WebSocket
Audit Log
Soft Delete
OpenTelemetry
CI/CD
GitHub Actions
```

このアプリを他の Backend Framework 学習に利用する場合も、Domain Model と API Specification は可能な限り維持する。

これにより以下を比較しやすくする。

```text
FastAPI
NestJS
Rails
Laravel
Spring Boot
Go
Rust
```
