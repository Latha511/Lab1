import copy

import pytest
from fastapi.testclient import TestClient


from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    email = "test@example.com"

    response = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]

    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    email = "daniel@mergington.edu"

    response = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success():
    email = "john@mergington.edu"

    response = client.delete(
        f"/activities/Gym%20Class/participants?email={email}"
    )
    assert response.status_code == 200
    assert email not in activities["Gym Class"]["participants"]


def test_remove_participant_not_found():
    response = client.delete(
        "/activities/Gym%20Class/participants?email=notfound@abc.com"
    )
    assert response.status_code == 404


def test_remove_activity_not_found():
    response = client.delete(
        "/activities/DoesNotExist/participants?email=foo@bar.com"
    )
    assert response.status_code == 404
