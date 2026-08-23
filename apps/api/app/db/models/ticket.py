from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum
from sqlmodel import Field, SQLModel


class TicketStatus(StrEnum):
    VALID = "VALID"
    CANCELLED = "CANCELLED"


class Ticket(SQLModel, table=True):
    __tablename__ = "tickets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    reservation_id: UUID = Field(foreign_key="reservations.id", unique=True, index=True)
    ticket_number: str = Field(unique=True, index=True, max_length=64)
    status: TicketStatus = Field(
        default=TicketStatus.VALID,
        sa_column=Column(Enum(TicketStatus), nullable=False),
    )
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
