from conftest import signup
from fastapi.testclient import TestClient


def assert_error(response, *, status: int, code: str, path: str) -> None:
    assert response.status_code == status, response.text
    body = response.json()
    assert body["statusCode"] == status
    assert body["code"] == code
    assert isinstance(body["message"], str) and body["message"]
    assert body["path"] == path
    assert body["timestamp"]


def test_signup_login_and_current_user(client: TestClient) -> None:
    signup_body, headers = signup(
        client, email="alice@example.com", name="Alice Example"
    )
    assert signup_body["tokenType"].lower() == "bearer"

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"
    assert me.json()["name"] == "Alice Example"
    assert me.json()["role"] == "USER"
    assert "password" not in me.json()
    assert "passwordHash" not in me.json()

    login = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json().get("accessToken") or login.json().get("access_token")


def test_duplicate_email_and_invalid_credentials(client: TestClient) -> None:
    signup(client, email="duplicate@example.com")
    duplicate = client.post(
        "/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "name": "Duplicate",
        },
    )
    assert_error(
        duplicate,
        status=409,
        code="EMAIL_ALREADY_EXISTS",
        path="/auth/signup",
    )

    invalid = client.post(
        "/auth/login",
        json={"email": "duplicate@example.com", "password": "wrong-password"},
    )
    assert_error(
        invalid,
        status=401,
        code="INVALID_CREDENTIALS",
        path="/auth/login",
    )


def test_authentication_is_required(client: TestClient) -> None:
    assert_error(
        client.get("/auth/me"), status=401, code="UNAUTHORIZED", path="/auth/me"
    )
    assert_error(
        client.get("/auth/me", headers={"Authorization": "Bearer broken.jwt"}),
        status=401,
        code="UNAUTHORIZED",
        path="/auth/me",
    )


def test_signup_validation_rejects_invalid_and_extra_fields(client: TestClient) -> None:
    for payload in (
        {"email": "not-an-email", "password": "password123", "name": "Alice"},
        {"email": "a@example.com", "password": "short", "name": "Alice"},
        {"email": "a@example.com", "password": "password123", "name": ""},
        {
            "email": "a@example.com",
            "password": "password123",
            "name": "Alice",
            "role": "ADMIN",
        },
    ):
        response = client.post("/auth/signup", json=payload)
        assert_error(
            response,
            status=422,
            code="VALIDATION_ERROR",
            path="/auth/signup",
        )
