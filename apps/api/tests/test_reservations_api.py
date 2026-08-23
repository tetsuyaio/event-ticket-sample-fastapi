from copy import deepcopy

from fastapi.testclient import TestClient
from test_auth_api import assert_error


def test_reservation_issues_ticket_and_cancel_restores_capacity(
    client: TestClient,
    user_headers: dict[str, str],
    published_event: dict,
) -> None:
    event_id = published_event["id"]
    reserved = client.post(f"/events/{event_id}/reservations", headers=user_headers)
    assert reserved.status_code == 201, reserved.text
    reservation = reserved.json()
    reservation_id = reservation["id"]
    assert reservation["status"] == "RESERVED"
    assert reservation["eventId"] == event_id
    assert reservation["ticket"]["status"] == "VALID"
    assert reservation["ticket"]["ticketNumber"]

    event = client.get(f"/events/{event_id}").json()
    assert event["reservedCount"] == 1

    listing = client.get("/me/reservations", headers=user_headers)
    assert listing.status_code == 200
    assert len(listing.json()["items"]) == 1
    assert listing.json()["items"][0]["id"] == reservation_id

    detail = client.get(f"/me/reservations/{reservation_id}", headers=user_headers)
    assert detail.status_code == 200
    assert detail.json()["ticket"]["ticketNumber"] == reservation["ticket"]["ticketNumber"]

    cancelled = client.delete(
        f"/me/reservations/{reservation_id}", headers=user_headers
    )
    assert cancelled.status_code == 204

    detail = client.get(f"/me/reservations/{reservation_id}", headers=user_headers)
    assert detail.status_code == 200
    assert detail.json()["status"] == "CANCELLED"
    assert detail.json()["cancelledAt"] is not None
    assert detail.json()["ticket"]["status"] == "CANCELLED"
    assert client.get(f"/events/{event_id}").json()["reservedCount"] == 0

    assert_error(
        client.delete(f"/me/reservations/{reservation_id}", headers=user_headers),
        status=409,
        code="RESERVATION_ALREADY_CANCELLED",
        path=f"/me/reservations/{reservation_id}",
    )


def test_duplicate_reservation_is_rejected(
    client: TestClient,
    user_headers: dict[str, str],
    published_event: dict,
) -> None:
    path = f"/events/{published_event['id']}/reservations"
    assert client.post(path, headers=user_headers).status_code == 201
    assert_error(
        client.post(path, headers=user_headers),
        status=409,
        code="ALREADY_RESERVED",
        path=path,
    )


def test_sold_out_event_never_exceeds_capacity(
    client: TestClient,
    admin_headers: dict[str, str],
    user_headers: dict[str, str],
    second_user_headers: dict[str, str],
    event_payload: dict,
) -> None:
    payload = deepcopy(event_payload)
    payload["capacity"] = 1
    event = client.post("/events", json=payload, headers=admin_headers).json()
    path = f"/events/{event['id']}/reservations"

    assert client.post(path, headers=user_headers).status_code == 201
    assert_error(
        client.post(path, headers=second_user_headers),
        status=409,
        code="EVENT_SOLD_OUT",
        path=path,
    )
    assert client.get(f"/events/{event['id']}").json()["reservedCount"] == 1


def test_draft_event_cannot_be_reserved(
    client: TestClient,
    admin_headers: dict[str, str],
    user_headers: dict[str, str],
    event_payload: dict,
) -> None:
    payload = deepcopy(event_payload)
    payload["status"] = "DRAFT"
    event = client.post("/events", json=payload, headers=admin_headers).json()
    path = f"/events/{event['id']}/reservations"
    assert_error(
        client.post(path, headers=user_headers),
        status=409,
        code="EVENT_NOT_PUBLISHED",
        path=path,
    )


def test_user_cannot_read_or_cancel_another_users_reservation(
    client: TestClient,
    user_headers: dict[str, str],
    second_user_headers: dict[str, str],
    published_event: dict,
) -> None:
    reservation = client.post(
        f"/events/{published_event['id']}/reservations", headers=user_headers
    ).json()
    path = f"/me/reservations/{reservation['id']}"

    # 他人の予約の存在自体を漏らさない。
    assert_error(
        client.get(path, headers=second_user_headers),
        status=404,
        code="RESERVATION_NOT_FOUND",
        path=path,
    )
    assert_error(
        client.delete(path, headers=second_user_headers),
        status=404,
        code="RESERVATION_NOT_FOUND",
        path=path,
    )


def test_reservation_endpoints_require_authentication(
    client: TestClient, published_event: dict
) -> None:
    path = f"/events/{published_event['id']}/reservations"
    assert_error(client.post(path), status=401, code="UNAUTHORIZED", path=path)
    assert_error(
        client.get("/me/reservations"),
        status=401,
        code="UNAUTHORIZED",
        path="/me/reservations",
    )
