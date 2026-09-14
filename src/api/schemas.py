from pydantic import BaseModel, Field

LOW_CONFIDENCE_THRESHOLD = 0.5


class PredictionRequest(BaseModel):
    """Modelo de dados para a requisição de classificação."""

    text: str = Field(
        ...,
        min_length=1,
        description="Texto médico que será classificado.",
        examples=[
            "The patient presents with symptoms related to the condition."
        ],
    )


class PredictionResponse(BaseModel):
    """Resposta da API contendo a classificação e a confiança do modelo."""

    condition_label: int
    condition_name: str
    confidence: float
    low_confidence: bool
