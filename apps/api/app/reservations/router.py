from uuid import UUID

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser, DbSession
from app.reservations.schemas import ReservationListResponse, ReservationResponse
from app.reservations.service import (
    cancel_reservation,
    get_reservation,
    get_reservations,
    reserve_event,
)

event_router = APIRouter(prefix="/events", tags=["reservations"])
me_router = APIRouter(prefix="/me/reservations", tags=["reservations"])


@event_router.post(
    "/{event_id}/reservations",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def reserve_event_route(
    event_id: UUID, session: DbSession, current_user: CurrentUser
) -> ReservationResponse:
    return reserve_event(session, event_id, current_user)


@me_router.get("", response_model=ReservationListResponse)
def list_reservations_route(
    session: DbSession, current_user: CurrentUser
) -> ReservationListResponse:
    return get_reservations(session, current_user)


@me_router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation_route(
    reservation_id: UUID, session: DbSession, current_user: CurrentUser
) -> ReservationResponse:
    return get_reservation(session, reservation_id, current_user)


@me_router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation_route(
    reservation_id: UUID, session: DbSession, current_user: CurrentUser
) -> None:
    cancel_reservation(session, reservation_id, current_user)
