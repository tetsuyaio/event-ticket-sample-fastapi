from datetime import datetime

from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.db.models.event import Event, EventStatus


def list_events(
    session: Session,
    *,
    keyword: str | None,
    status: EventStatus | None,
    starts_from: datetime | None,
    starts_to: datetime | None,
    page: int,
    limit: int,
) -> tuple[list[Event], int]:
    filters = []
    if keyword:
        pattern = f"%{keyword}%"
        filters.append(or_(Event.title.ilike(pattern), Event.description.ilike(pattern)))
    if status:
        filters.append(Event.status == status)
    if starts_from:
        filters.append(Event.starts_at >= starts_from)
    if starts_to:
        filters.append(Event.starts_at <= starts_to)
    statement = select(Event).where(*filters)
    count_statement = select(func.count()).select_from(Event).where(*filters)
    total = session.exec(count_statement).one()
    items = list(
        session.exec(
            statement.order_by(Event.starts_at).offset((page - 1) * limit).limit(limit)
        ).all()
    )
    return items, total
