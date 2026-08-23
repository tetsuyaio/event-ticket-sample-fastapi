from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.auth.schemas import AuthResponse, LoginRequest, SignupRequest, UserResponse
from app.core.exceptions import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User


def signup(session: Session, payload: SignupRequest) -> AuthResponse:
    existing = session.exec(select(User).where(User.email == payload.email.lower())).first()
    if existing:
        raise AppError(409, "EMAIL_ALREADY_EXISTS", "Email already exists")
    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        name=payload.name,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise AppError(409, "EMAIL_ALREADY_EXISTS", "Email already exists") from exc
    session.refresh(user)
    return AuthResponse(
        access_token=create_access_token(user.id, user.role),
        user=UserResponse.model_validate(user),
    )


def login(session: Session, payload: LoginRequest) -> AuthResponse:
    user = session.exec(select(User).where(User.email == payload.email.lower())).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AppError(401, "INVALID_CREDENTIALS", "Invalid email or password")
    return AuthResponse(
        access_token=create_access_token(user.id, user.role),
        user=UserResponse.model_validate(user),
    )
