from pathlib import Path

import joblib

ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    ROOT_DIR
    / "models"
    / "baseline"
    / "models.joblib"
)


def load_model():
    """Carrega o pipeline de classificação treinado."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)
