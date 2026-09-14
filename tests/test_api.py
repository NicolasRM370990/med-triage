from fastapi.testclient import TestClient

from src.api.main import app, condition_names
from src.data.loader import load_condition_names

VALID_CONDITIONS = set(load_condition_names().values())

client = TestClient(app)


def test_root_redirects_to_docs():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert "/docs" in response.headers["location"]


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

    assert data["condition_name"] in VALID_CONDITIONS
    assert data["condition_label"] in condition_names
    assert condition_names[data["condition_label"]] == data["condition_name"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["low_confidence"] == (data["confidence"] < 0.5)


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


def test_labels_come_from_csv():
    assert condition_names == load_condition_names()
    assert len(condition_names) == 5
