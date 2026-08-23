from uuid import UUID

from sqlmodel import Session, select

from app.db.models.event import Event
from app.db.models.reservation import Reservation
from app.db.models.ticket import Ticket
from app.events.schemas import EventResponse
from app.reservations.schemas import ReservationResponse, TicketResponse


def find_user_event_reservation(
    session: Session, user_id: UUID, event_id: UUID
) -> Reservation | None:
    return session.exec(
        select(Reservation).where(
            Reservation.user_id == user_id,
            Reservation.event_id == event_id,
        )
    ).first()


def find_user_reservation(
    session: Session, user_id: UUID, reservation_id: UUID
) -> Reservation | None:
    return session.exec(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.user_id == user_id,
        )
    ).first()


def list_user_reservations(session: Session, user_id: UUID) -> list[Reservation]:
    return list(
        session.exec(
            select(Reservation)
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.reserved_at.desc())
        ).all()
    )


def reservation_response(session: Session, reservation: Reservation) -> ReservationResponse:
    ticket = session.exec(
        select(Ticket).where(Ticket.reservation_id == reservation.id)
    ).one()
    event = session.get(Event, reservation.event_id)
    if event is None:  # DB foreign key should make this unreachable.
        raise RuntimeError("Reservation event is missing")
    return ReservationResponse(
        **reservation.model_dump(),
        ticket=TicketResponse.model_validate(ticket),
        event=EventResponse.model_validate(event),
    )
