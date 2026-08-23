from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from app.db.models.event import Event, EventStatus
from app.db.models.user import User
from app.events.repository import list_events


def test_event_repository_filters_and_paginates(db_engine) -> None:
    now = datetime.now(UTC)
    with Session(db_engine) as session:
        admin = User(
            email="repository-admin@example.com",
            password_hash="not-used-in-this-test",
            name="Repository Admin",
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        session.add_all(
            [
                Event(
                    title="FastAPI Workshop",
                    description="Python API",
                    venue="Tokyo",
                    starts_at=now + timedelta(days=1),
                    ends_at=now + timedelta(days=1, hours=2),
                    capacity=10,
                    status=EventStatus.PUBLISHED,
                    created_by=admin.id,
                ),
                Event(
                    title="Private Draft",
                    description="Not published",
                    venue="Osaka",
                    starts_at=now + timedelta(days=2),
                    ends_at=now + timedelta(days=2, hours=2),
                    capacity=10,
                    status=EventStatus.DRAFT,
                    created_by=admin.id,
                ),
            ]
        )
        session.commit()

        items, total = list_events(
            session,
            keyword="fastapi",
            status=EventStatus.PUBLISHED,
            starts_from=now,
            starts_to=now + timedelta(days=3),
            page=1,
            limit=1,
        )

    assert total == 1
    assert [event.title for event in items] == ["FastAPI Workshop"]
