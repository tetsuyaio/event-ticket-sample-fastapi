from datetime import datetime
from uuid import UUID

from app.core.schemas import ApiSchema
from app.db.models.reservation import ReservationStatus
from app.db.models.ticket import TicketStatus
from app.events.schemas import EventResponse


class TicketResponse(ApiSchema):
    id: UUID
    reservation_id: UUID
    ticket_number: str
    status: TicketStatus
    issued_at: datetime
    created_at: datetime


class ReservationResponse(ApiSchema):
    id: UUID
    user_id: UUID
    event_id: UUID
    status: ReservationStatus
    reserved_at: datetime
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime
    ticket: TicketResponse
    event: EventResponse


class ReservationListResponse(ApiSchema):
    items: list[ReservationResponse]
