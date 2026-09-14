import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from prometheus_client import Counter, Histogram, make_asgi_app

from src.api.model import load_model
from src.api.schemas import (
    LOW_CONFIDENCE_THRESHOLD,
    PredictionRequest,
    PredictionResponse,
)
from src.data.loader import load_condition_names

app = FastAPI(
    title="Medical Triage API",
    description=(
        "API para classificação de textos médicos "
        "utilizando um modelo NLP. Apoio à triagem; "
        "não substitui avaliação clínica."
    ),
    version="1.0.0",
)


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

model = load_model()
condition_names = load_condition_names()


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    """Retorna o status da API e se o modelo foi carregado."""

    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Classifica um texto médico e devolve rótulo, nome e confiança."""
    start_time = time.perf_counter()

    try:
        prediction = int(model.predict([request.text])[0])
        probabilities = model.predict_proba([request.text])[0]
        confidence = float(max(probabilities))
        condition_name = condition_names.get(
            prediction,
            "unknown condition",
        )

        REQUEST_COUNT.labels(
            method="POST",
            endpoint="/predict",
            status="200",
        ).inc()

        return PredictionResponse(
            condition_label=prediction,
            condition_name=condition_name,
            confidence=confidence,
            low_confidence=confidence < LOW_CONFIDENCE_THRESHOLD,
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


metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)
