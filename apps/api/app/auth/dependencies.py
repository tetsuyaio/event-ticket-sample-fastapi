from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.db.models.user import User, UserRole
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise AppError(401, "UNAUTHORIZED", "Authentication required")
    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        user_id = UUID(str(subject))
    except (jwt.PyJWTError, ValueError, TypeError) as exc:
        raise AppError(401, "UNAUTHORIZED", "Invalid or expired token") from exc
    user = session.get(User, user_id)
    if user is None:
        raise AppError(401, "UNAUTHORIZED", "User no longer exists")
    request.state.user_id = str(user.id)
    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise AppError(403, "FORBIDDEN", "Admin role required")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
DbSession = Annotated[Session, Depends(get_db)]
