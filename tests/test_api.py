from fastapi.testclient import TestClient

from src.api.main import app

VALID_CONDITIONS = {
    "neoplasms",
    "digestive system diseases",
    "nervous system diseases",
    "cardiovascular diseases",
    "general pathological conditions",
}

client = TestClient(app)


def test_health():
    """Verifica se a API está funcionando."""

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_predict():
    payload = {
        "text": (
            "The patient presented with persistent chest pain "
            "and shortness of breath."
        )
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "condition_name" in data
    assert "confidence" in data

    assert data["condition_name"] in VALID_CONDITIONS
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_empty_text():
    """Verifica a validação de texto vazio."""

    payload = {
        "text": "",
    }

    response = client.post(
        "/predict",
        json=payload,
    )

    assert response.status_code == 422


def test_predict_missing_text():
    """Verifica a validação quando o campo text não é enviado."""

    response = client.post(
        "/predict",
        json={},
    )

    assert response.status_code == 422


def test_metrics():
    """Verifica se o endpoint de métricas está disponível."""

    response = client.get("/metrics")

    assert response.status_code == 200

    assert "http_requests_total" in response.text
