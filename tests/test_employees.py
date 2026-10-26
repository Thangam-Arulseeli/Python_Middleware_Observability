#### Create tests/test_employees.py

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_employee():

    response = client.post(
        "/api/employees",
        json={
            "name": "Arun Kumar",
            "email": "arun@example.com",
            "department": "Engineering",
            "salary": 55000,
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["name"] == "Arun Kumar"
    assert body["department"] == "Engineering"


def test_employee_not_found():

    response = client.get(
        "/api/employees/999999"
    )

    assert response.status_code == 404
    body = response.json()

    assert body["error"]["code"] == "HTTP_404"
    assert (
        body["error"]["correlation_id"]
    )


def test_validation_error():

    response = client.post(
        "/api/employees",
        json={
            "name": "A",
            "email": "arun@example.com",
            "department": "Engineering",
            "salary": -5000,
        },
    )

    assert response.status_code == 422

    assert (
        response.json()["error"]["code"]
        == "VALIDATION_ERROR"
    )


