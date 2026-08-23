from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, Text
from sqlmodel import Field, SQLModel


class EventStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Event(SQLModel, table=True):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_events_capacity_positive"),
        CheckConstraint("reserved_count >= 0", name="ck_events_reserved_count_nonnegative"),
        CheckConstraint("reserved_count <= capacity", name="ck_events_reserved_within_capacity"),
        CheckConstraint("starts_at < ends_at", name="ck_events_valid_period"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: str = Field(sa_column=Column(Text, nullable=False))
    venue: str = Field(max_length=200)
    starts_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True)
    )
    ends_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    capacity: int
    reserved_count: int = Field(default=0)
    status: EventStatus = Field(
        default=EventStatus.DRAFT,
        sa_column=Column(Enum(EventStatus), nullable=False, index=True),
    )
    created_by: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
