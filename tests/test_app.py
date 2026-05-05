import copy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_200(client):
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_get_activities_contains_required_fields(client):
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    for activity_data in data.values():
        assert required_fields.issubset(activity_data.keys())


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count + 1
    assert f"Signed up {email} for {activity_name}" in response.json()["message"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_remove_participant_success(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant_email}"
    )

    # Assert
    assert response.status_code == 200
    assert participant_email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1
    assert f"Removed {participant_email} from {activity_name}" in response.json()["message"]


def test_remove_participant_not_found_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = "missing@student.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant_email}"
    )

    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]
