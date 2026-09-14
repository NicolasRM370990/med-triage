import os
from pathlib import Path

import joblib

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "baseline" / "models.joblib"


def resolve_model_path() -> Path:
    env_path = os.getenv("MODEL_PATH")
    if not env_path:
        return DEFAULT_MODEL_PATH

    path = Path(env_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path


def load_model():
    """Carrega o pipeline de classificação treinado."""

    model_path = resolve_model_path()
    if not model_path.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em: {model_path}"
        )

    return joblib.load(model_path)
