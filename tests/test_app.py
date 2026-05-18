import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    """Arrange: save a deep copy of the in-memory activities and restore after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "new_student@example.com"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")
    assert email in activities[activity]["participants"]


def test_signup_already_registered():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "repeat@example.com"

    # Act (first signup)
    resp1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp1.status_code == 200

    # Act (second signup)
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp2.status_code == 400


def test_signup_nonexistent_activity():
    # Arrange
    client = TestClient(app)

    # Act
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "x@y.com"})

    # Assert
    assert resp.status_code == 404


def test_unregister_success():
    # Arrange
    client = TestClient(app)
    activity = "Programming Class"
    email = "temp@example.com"

    # Act (signup then unregister)
    resp_signup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp_signup.status_code == 200
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered():
    # Arrange
    client = TestClient(app)
    activity = "Programming Class"
    email = "notregistered@example.com"

    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 404


def test_unregister_nonexistent_activity():
    # Arrange
    client = TestClient(app)

    # Act
    resp = client.delete("/activities/NoSuchActivity/participants", params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404
