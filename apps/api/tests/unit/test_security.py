from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.models.user import UserRole


def test_password_is_hashed_and_can_be_verified() -> None:
    plain = "correct-horse-battery-staple"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_contains_subject_and_role() -> None:
    user_id = uuid4()
    token = create_access_token(user_id, UserRole.ADMIN)

    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "ADMIN"
    assert "exp" in payload
