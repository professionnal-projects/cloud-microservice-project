import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Portfolio Microservice")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_VERSION", "9.9.9")

    flask_app = create_app()
    flask_app.config.update({"TESTING": True})

    with flask_app.test_client() as test_client:
        yield test_client


def test_dashboard_route_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert b"Dashboard" in response.data


def test_health_route(client):
    response = client.get("/health")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert payload["environment"] == "test"


def test_info_route(client):
    response = client.get("/info")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload == {
        "service": "Portfolio Microservice",
        "version": "9.9.9",
        "environment": "test",
        "runtime": "Flask",
    }


def test_metrics_route(client):
    client.get("/health")
    response = client.get("/metrics")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["app_env"] == "test"
    assert payload["request_count"] >= 2
    assert "uptime_seconds" in payload


def test_echo_route_with_json_payload(client):
    test_payload = {"message": "hello", "source": "pytest"}

    response = client.post("/echo", json=test_payload)
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["received"] == test_payload


def test_echo_route_rejects_invalid_json(client):
    response = client.post(
        "/echo",
        data="plain-text-body",
        content_type="text/plain",
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert "valid JSON" in payload["error"]
