from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.exceptions import AppError
from app.db.models.event import Event, EventStatus
from app.db.models.reservation import Reservation, ReservationStatus
from app.db.models.ticket import Ticket, TicketStatus
from app.db.models.user import User
from app.reservations.repository import (
    find_user_event_reservation,
    find_user_reservation,
    list_user_reservations,
    reservation_response,
)
from app.reservations.schemas import ReservationListResponse, ReservationResponse


def reserve_event(session: Session, event_id: UUID, user: User) -> ReservationResponse:
    user_id = user.id
    # Authentication performs a read on this request-scoped session. Close that
    # implicit transaction before starting the reservation unit of work.
    session.commit()
    reservation_id = uuid4()
    try:
        with session.begin():
            event = session.get(Event, event_id)
            if event is None:
                raise AppError(404, "EVENT_NOT_FOUND", "Event not found")
            if event.status != EventStatus.PUBLISHED:
                raise AppError(409, "EVENT_NOT_PUBLISHED", "Event is not published")
            if find_user_event_reservation(session, user_id, event_id):
                raise AppError(409, "ALREADY_RESERVED", "Event is already reserved")

            result = session.execute(
                update(Event)
                .where(
                    Event.id == event_id,
                    Event.status == EventStatus.PUBLISHED,
                    Event.reserved_count < Event.capacity,
                )
                .values(reserved_count=Event.reserved_count + 1, updated_at=datetime.now(UTC))
            )
            if result.rowcount != 1:
                raise AppError(409, "EVENT_SOLD_OUT", "Event is sold out")

            reservation = Reservation(id=reservation_id, user_id=user_id, event_id=event_id)
            ticket = Ticket(
                reservation_id=reservation_id,
                ticket_number=f"TKT-{uuid4().hex.upper()}",
            )
            session.add(reservation)
            session.add(ticket)
    except IntegrityError as exc:
        session.rollback()
        raise AppError(409, "ALREADY_RESERVED", "Event is already reserved") from exc

    reservation = session.get(Reservation, reservation_id)
    if reservation is None:
        raise RuntimeError("Created reservation is missing")
    return reservation_response(session, reservation)


def get_reservation(
    session: Session, reservation_id: UUID, user: User
) -> ReservationResponse:
    reservation = find_user_reservation(session, user.id, reservation_id)
    if reservation is None:
        raise AppError(404, "RESERVATION_NOT_FOUND", "Reservation not found")
    return reservation_response(session, reservation)


def get_reservations(session: Session, user: User) -> ReservationListResponse:
    return ReservationListResponse(
        items=[
            reservation_response(session, reservation)
            for reservation in list_user_reservations(session, user.id)
        ]
    )


def cancel_reservation(session: Session, reservation_id: UUID, user: User) -> None:
    user_id = user.id
    session.commit()
    with session.begin():
        reservation = find_user_reservation(session, user_id, reservation_id)
        if reservation is None:
            raise AppError(404, "RESERVATION_NOT_FOUND", "Reservation not found")
        if reservation.status == ReservationStatus.CANCELLED:
            raise AppError(
                409, "RESERVATION_ALREADY_CANCELLED", "Reservation is already cancelled"
            )
        now = datetime.now(UTC)
        reservation.status = ReservationStatus.CANCELLED
        reservation.cancelled_at = now
        reservation.updated_at = now
        ticket = session.exec(
            select(Ticket).where(Ticket.reservation_id == reservation.id)
        ).one()
        ticket.status = TicketStatus.CANCELLED
        session.execute(
            update(Event)
            .where(Event.id == reservation.event_id, Event.reserved_count > 0)
            .values(reserved_count=Event.reserved_count - 1, updated_at=now)
        )
        session.add(reservation)
        session.add(ticket)
