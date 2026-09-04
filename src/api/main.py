import time

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app

from src.api.model import load_model
from src.api.schemas import (
    PredictionRequest,
    PredictionResponse,
)

CONDITION_NAMES = {
    1: "neoplasms",
    2: "digestive system diseases",
    3: "nervous system diseases",
    4: "cardiovascular diseases",
    5: "general pathological conditions",
}

app = FastAPI(
    title="Medical Triage API",
    description=(
        "API para classificação de textos médicos "
        "utilizando um modelo NLP."
    ),
    version="1.0.0",
)


# -------------------------------------------------------------------
# Métricas Prometheus
# -------------------------------------------------------------------

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de requisições HTTP.",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Tempo de processamento das requisições HTTP.",
    ["endpoint"],
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total de erros da API.",
    ["endpoint"],
)


# -------------------------------------------------------------------
# Carregamento do modelo
# -------------------------------------------------------------------

model = load_model()


# -------------------------------------------------------------------
# Endpoints
# health => Verifica se a API está funcionando.
# predict => Classifica o texto recebido.
# metrics => Exibe as métricas Prometheus.
# -------------------------------------------------------------------

@app.get("/health")
def health():
    """
        Endpoint de saúde da API.
        Retorna o status da API e se o modelo foi carregado com sucesso.
    """

    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
        Endpoint de previsão de classificação.
        Recebe um texto médico e retorna a classificação prevista
        e a confiança do modelo.
    """
    start_time = time.perf_counter()

    try:
        prediction = int(model.predict([request.text])[0])
        probabilities = model.predict_proba([request.text])[0]
        confidence = float(max(probabilities))

        condition_name = CONDITION_NAMES.get(
            prediction,
            "unknown condition",
        )

        REQUEST_COUNT.labels(
            method="POST",
            endpoint="/predict",
            status="200",
        ).inc()

        return PredictionResponse(
            condition_name=condition_name,
            confidence=confidence,
        )

    except Exception as exc:
        ERROR_COUNT.labels(endpoint="/predict").inc()
        REQUEST_COUNT.labels(
            method="POST",
            endpoint="/predict",
            status="500",
        ).inc()

        raise HTTPException(
            status_code=500,
            detail="Erro durante a classificação.",
        ) from exc

    finally:
        elapsed = time.perf_counter() - start_time
        REQUEST_LATENCY.labels(
            endpoint="/predict",
        ).observe(elapsed)


# -------------------------------------------------------------------
# Endpoint de métricas
# -------------------------------------------------------------------

metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)