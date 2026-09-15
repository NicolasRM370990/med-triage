import json
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline

from src.data.loader import load_test, load_train
from src.features.tfidf import create_vectorizer

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT_DIR / "models" / "baseline"
MODEL_PATH = MODEL_DIR / "models.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", create_vectorizer()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def train_model() -> Pipeline:
    train_df = load_train()

    X_train = train_df["medical_abstract"]
    y_train = train_df["condition_label"]

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    return pipeline


def evaluate_model(pipeline: Pipeline) -> dict[str, float]:
    test_df = load_test()

    X_test = test_df["medical_abstract"]
    y_test = test_df["condition_label"]

    predictions = pipeline.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision_macro": float(
            precision_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0,
            )
        ),
        "recall_macro": float(
            recall_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0,
            )
        ),
        "f1_macro": float(
            f1_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0,
            )
        ),
    }

    print("\n===== CLASSIFICATION REPORT =====")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    print("===== MATRIZ DE CONFUSÃO =====")
    print(confusion_matrix(y_test, predictions))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    return metrics


def save_model(pipeline: Pipeline) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)


def load_model() -> Pipeline:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def main() -> None:
    print("Treinando modelo...")

    pipeline = train_model()
    metrics = evaluate_model(pipeline)

    print("\n===== MÉTRICAS DO MODELO =====")

    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")

    save_model(pipeline)

    print(f"\nModelo salvo em: {MODEL_PATH}")
    print(f"Métricas salvas em: {METRICS_PATH}")


if __name__ == "__main__":
    main()
