from datetime import datetime
from uuid import UUID

from pydantic import Field, model_validator

from app.core.schemas import ApiSchema
from app.db.models.event import EventStatus


class EventCreate(ApiSchema):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=10000)
    venue: str = Field(min_length=1, max_length=200)
    starts_at: datetime
    ends_at: datetime
    capacity: int = Field(gt=0)
    status: EventStatus = EventStatus.DRAFT

    @model_validator(mode="after")
    def validate_period(self) -> "EventCreate":
        if self.starts_at >= self.ends_at:
            raise ValueError("startsAt must be before endsAt")
        return self


class EventUpdate(ApiSchema):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    venue: str | None = Field(default=None, min_length=1, max_length=200)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    capacity: int | None = Field(default=None, gt=0)
    status: EventStatus | None = None


class EventResponse(ApiSchema):
    id: UUID
    title: str
    description: str
    venue: str
    starts_at: datetime
    ends_at: datetime
    capacity: int
    reserved_count: int
    status: EventStatus
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class EventListResponse(ApiSchema):
    items: list[EventResponse]
    page: int
    limit: int
    total: int
