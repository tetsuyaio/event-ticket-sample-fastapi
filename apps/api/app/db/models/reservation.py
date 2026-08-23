from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum, UniqueConstraint
from sqlmodel import Field, SQLModel


class ReservationStatus(StrEnum):
    RESERVED = "RESERVED"
    CANCELLED = "CANCELLED"


class Reservation(SQLModel, table=True):
    __tablename__ = "reservations"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_reservations_user_event"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    event_id: UUID = Field(foreign_key="events.id", index=True)
    status: ReservationStatus = Field(
        default=ReservationStatus.RESERVED,
        sa_column=Column(Enum(ReservationStatus), nullable=False),
    )
    reserved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    cancelled_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
