import importlib

import pytest
from fastapi.testclient import TestClient


app_module = importlib.import_module("src.app")


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        },
        "Empty Club": {
            "description": "Try a new activity",
            "schedule": "Mondays",
            "max_participants": 10,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_chess_participants = ["existing@mergington.edu"]

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    assert activities["Chess Club"]["participants"] == expected_chess_participants
    assert activities["Empty Club"]["participants"] == []


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Empty Club"
    activity_path = "Empty%20Club"
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert activities[activity_name]["participants"] == [email]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    activity_path = "Chess%20Club"
    email = "existing@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities[activity_name]["participants"] == [email]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    activity_path = "Unknown%20Club"
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    activity_path = "Chess%20Club"
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert activities[activity_name]["participants"] == []


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    activity_name = "Empty Club"
    activity_path = "Empty%20Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    activity_path = "Unknown%20Club"
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
