from copy import deepcopy

from fastapi.testclient import TestClient
from test_auth_api import assert_error


def test_admin_can_manage_events_and_public_can_read_them(
    client: TestClient,
    admin_headers: dict[str, str],
    event_payload: dict,
) -> None:
    created = client.post("/events", json=event_payload, headers=admin_headers)
    assert created.status_code == 201, created.text
    event = created.json()
    event_id = event["id"]
    assert event["reservedCount"] == 0
    assert event["status"] == "PUBLISHED"

    detail = client.get(f"/events/{event_id}")
    assert detail.status_code == 200
    assert detail.json()["title"] == event_payload["title"]

    listing = client.get("/events?keyword=fastapi&status=PUBLISHED&page=1&limit=20")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert [item["id"] for item in listing.json()["items"]] == [event_id]

    patched = client.patch(
        f"/events/{event_id}", json={"venue": "Osaka"}, headers=admin_headers
    )
    assert patched.status_code == 200
    assert patched.json()["venue"] == "Osaka"

    deleted = client.delete(f"/events/{event_id}", headers=admin_headers)
    assert deleted.status_code == 204
    assert_error(
        client.get(f"/events/{event_id}"),
        status=404,
        code="EVENT_NOT_FOUND",
        path=f"/events/{event_id}",
    )


def test_event_mutation_requires_admin(
    client: TestClient,
    user_headers: dict[str, str],
    event_payload: dict,
    published_event: dict,
) -> None:
    event_id = published_event["id"]
    requests = (
        client.post("/events", json=event_payload, headers=user_headers),
        client.patch(f"/events/{event_id}", json={"venue": "Kyoto"}, headers=user_headers),
        client.delete(f"/events/{event_id}", headers=user_headers),
    )
    for response in requests:
        assert response.status_code == 403
        assert response.json()["code"] == "FORBIDDEN"


def test_event_validation(
    client: TestClient,
    admin_headers: dict[str, str],
    event_payload: dict,
) -> None:
    invalid_payloads = []

    zero_capacity = deepcopy(event_payload)
    zero_capacity["capacity"] = 0
    invalid_payloads.append(zero_capacity)

    reversed_dates = deepcopy(event_payload)
    reversed_dates["startsAt"], reversed_dates["endsAt"] = (
        reversed_dates["endsAt"],
        reversed_dates["startsAt"],
    )
    invalid_payloads.append(reversed_dates)

    extra_field = deepcopy(event_payload)
    extra_field["reservedCount"] = 10
    invalid_payloads.append(extra_field)

    for payload in invalid_payloads:
        response = client.post("/events", json=payload, headers=admin_headers)
        assert_error(
            response,
            status=422,
            code="VALIDATION_ERROR",
            path="/events",
        )


def test_event_list_pagination_is_bounded(client: TestClient) -> None:
    response = client.get("/events?page=0&limit=101")
    assert_error(
        response,
        status=422,
        code="VALIDATION_ERROR",
        path="/events",
    )
