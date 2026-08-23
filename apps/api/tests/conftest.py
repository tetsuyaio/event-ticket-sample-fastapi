from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.models.user import User
from app.db.session import get_db
from app.main import app


@pytest.fixture
def db_engine():
    """各テストを、同じ接続を共有する空のインメモリ DB で実行する。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    try:
        yield engine
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(db_engine) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _token(body: dict[str, Any]) -> str:
    token = body.get("accessToken") or body.get("access_token")
    assert isinstance(token, str) and token
    return token


def signup(
    client: TestClient,
    *,
    email: str,
    name: str = "Test User",
    password: str = "password123",
) -> tuple[dict[str, Any], dict[str, str]]:
    response = client.post(
        "/auth/signup",
        json={"email": email, "password": password, "name": name},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    return body, {"Authorization": f"Bearer {_token(body)}"}


@pytest.fixture
def user_headers(client: TestClient) -> dict[str, str]:
    _, headers = signup(client, email="user@example.com")
    return headers


@pytest.fixture
def second_user_headers(client: TestClient) -> dict[str, str]:
    _, headers = signup(client, email="other@example.com", name="Other User")
    return headers


@pytest.fixture
def admin_headers(client: TestClient, db_engine) -> dict[str, str]:
    # 公開 API に role 昇格エンドポイントはないため、signup 後に fixture 内で昇格する。
    signup(client, email="admin@example.com", name="Admin")
    with Session(db_engine) as session:
        admin = session.exec(select(User).where(User.email == "admin@example.com")).one()
        role_type = type(admin.role)
        admin.role = getattr(role_type, "ADMIN", "ADMIN")
        session.add(admin)
        session.commit()

    response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {_token(response.json())}"}


@pytest.fixture
def event_payload() -> dict[str, Any]:
    return {
        "title": "FastAPI Conference",
        "description": "FastAPI を学ぶイベント",
        "venue": "Tokyo",
        "startsAt": "2030-06-01T10:00:00Z",
        "endsAt": "2030-06-01T12:00:00Z",
        "capacity": 2,
        "status": "PUBLISHED",
    }


@pytest.fixture
def published_event(
    client: TestClient,
    admin_headers: dict[str, str],
    event_payload: dict[str, Any],
) -> dict[str, Any]:
    response = client.post("/events", json=event_payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    return response.json()
