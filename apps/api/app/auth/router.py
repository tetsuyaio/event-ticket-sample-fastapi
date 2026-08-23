from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.schemas import AuthResponse, LoginRequest, SignupRequest, UserResponse
from app.auth.service import login, signup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup_route(payload: SignupRequest, session: DbSession) -> AuthResponse:
    return signup(session, payload)


@router.post("/login", response_model=AuthResponse)
def login_route(payload: LoginRequest, session: DbSession) -> AuthResponse:
    return login(session, payload)


@router.get("/me", response_model=UserResponse)
def me_route(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
