import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        "Art Club": {
            "description": "Explore visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["artist@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities):
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_activity_page(client):
    # Arrange: the client fixture provides the app with isolated data.

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client, activities):
    # Arrange: the activities fixture supplies one known activity.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client, activities):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in activities["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    email = "artist@mergington.edu"
    original_participants = activities["Art Club"]["participants"].copy()

    # Act
    response = client.post("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Art Club"]["participants"] == original_participants


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, activities):
    # Arrange
    email = "artist@mergington.edu"

    # Act
    response = client.delete("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Art Club"}
    assert email not in activities["Art Club"]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    email = "artist@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"