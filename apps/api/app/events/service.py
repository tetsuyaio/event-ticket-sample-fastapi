from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session

from app.core.exceptions import AppError
from app.db.models.event import Event, EventStatus
from app.db.models.user import User
from app.events.repository import list_events
from app.events.schemas import EventCreate, EventListResponse, EventResponse, EventUpdate


def get_event(session: Session, event_id: UUID) -> Event:
    event = session.get(Event, event_id)
    if event is None:
        raise AppError(404, "EVENT_NOT_FOUND", "Event not found")
    return event


def create_event(session: Session, payload: EventCreate, admin: User) -> EventResponse:
    event = Event(**payload.model_dump(), created_by=admin.id)
    session.add(event)
    session.commit()
    session.refresh(event)
    return EventResponse.model_validate(event)


def update_event(
    session: Session, event_id: UUID, payload: EventUpdate
) -> EventResponse:
    event = get_event(session, event_id)
    updates = payload.model_dump(exclude_unset=True)
    starts_at = updates.get("starts_at", event.starts_at)
    ends_at = updates.get("ends_at", event.ends_at)
    capacity = updates.get("capacity", event.capacity)
    if starts_at >= ends_at:
        raise AppError(422, "VALIDATION_ERROR", "startsAt must be before endsAt")
    if capacity < event.reserved_count:
        raise AppError(422, "VALIDATION_ERROR", "capacity cannot be below reservedCount")
    for name, value in updates.items():
        setattr(event, name, value)
    event.updated_at = datetime.now(UTC)
    session.add(event)
    session.commit()
    session.refresh(event)
    return EventResponse.model_validate(event)


def delete_event(session: Session, event_id: UUID) -> None:
    event = get_event(session, event_id)
    if event.reserved_count > 0:
        raise AppError(409, "FORBIDDEN", "Event with reservations cannot be deleted")
    session.delete(event)
    session.commit()


def search_events(
    session: Session,
    *,
    keyword: str | None,
    status: EventStatus | None,
    starts_from: datetime | None,
    starts_to: datetime | None,
    page: int,
    limit: int,
) -> EventListResponse:
    events, total = list_events(
        session,
        keyword=keyword,
        status=status,
        starts_from=starts_from,
        starts_to=starts_to,
        page=page,
        limit=limit,
    )
    return EventListResponse(
        items=[EventResponse.model_validate(event) for event in events],
        page=page,
        limit=limit,
        total=total,
    )
