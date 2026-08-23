from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.auth.dependencies import AdminUser, DbSession
from app.db.models.event import EventStatus
from app.events.schemas import EventCreate, EventListResponse, EventResponse, EventUpdate
from app.events.service import (
    create_event,
    delete_event,
    get_event,
    search_events,
    update_event,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventListResponse)
def list_events_route(
    session: DbSession,
    keyword: str | None = None,
    event_status: Annotated[EventStatus | None, Query(alias="status")] = None,
    starts_from: Annotated[datetime | None, Query(alias="startsFrom")] = None,
    starts_to: Annotated[datetime | None, Query(alias="startsTo")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> EventListResponse:
    return search_events(
        session,
        keyword=keyword,
        status=event_status,
        starts_from=starts_from,
        starts_to=starts_to,
        page=page,
        limit=limit,
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event_route(event_id: UUID, session: DbSession) -> EventResponse:
    return EventResponse.model_validate(get_event(session, event_id))


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event_route(payload: EventCreate, session: DbSession, admin: AdminUser) -> EventResponse:
    return create_event(session, payload, admin)


@router.patch("/{event_id}", response_model=EventResponse)
def update_event_route(
    event_id: UUID, payload: EventUpdate, session: DbSession, _admin: AdminUser
) -> EventResponse:
    return update_event(session, event_id, payload)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_route(event_id: UUID, session: DbSession, _admin: AdminUser) -> None:
    delete_event(session, event_id)
