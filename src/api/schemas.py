from pydantic import BaseModel, Field


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
    condition_name: str # Nome da condição médica prevista pelo modelo.
    confidence: float # Confiança do modelo na previsão, variando de 0 a 1.