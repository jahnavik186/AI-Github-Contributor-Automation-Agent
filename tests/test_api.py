from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_use_cases_endpoint():
    response = client.get("/use-cases")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert "customer_support" in payload["use_cases"]


def test_agent_run_endpoint():
    response = client.post(
        "/agent/run",
        json={
            "user_id": "test-user",
            "session_id": "test-session",
            "message": "I need a refund for a duplicate charge.",
            "use_case": "customer_support",
            "use_retrieval": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["use_case"] == "customer_support"
    assert payload["intent"] in {
        "billing_issue",
        "refund_request",
        "access_issue",
        "scheduling",
        "general_support",
    }
    assert "trace" in payload

