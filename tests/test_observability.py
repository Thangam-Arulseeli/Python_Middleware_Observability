#### Create tests/test_observability.py

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_correlation_id_is_returned():

    response = client.get(
        "/health/live"
    )

    correlation_id = response.headers.get(
        "X-Correlation-ID"
    )

    assert correlation_id is not None
    assert len(correlation_id) > 0


def test_valid_correlation_id_is_reused():

    response = client.get(
        "/health/live",
        headers={
            "X-Correlation-ID": "training-test-001",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["X-Correlation-ID"]
        == "training-test-001"
    )


def test_invalid_correlation_id_is_replaced():

    invalid_id = "invalid id with spaces"

    response = client.get(
        "/health/live",
        headers={
            "X-Correlation-ID": invalid_id,
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["X-Correlation-ID"]
        != invalid_id
    )



