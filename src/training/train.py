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


def build_pipeline() -> Pipeline:
    """Cria o pipeline de TF-IDF + Logistic Regression."""
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


def evaluate_model(
    pipeline: Pipeline,
    X_test,
    y_test,
) -> dict[str, float]:
    """Avalia o modelo utilizando o conjunto de teste."""

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

    print("\n===== MÉTRICAS DO MODELO =====")
    print(f"Accuracy : {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision_macro']:.4f}")
    print(f"Recall   : {metrics['recall_macro']:.4f}")
    print(f"F1 Macro : {metrics['f1_macro']:.4f}")

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

    return metrics


def main() -> None:
    train_df = load_train()

    X_train = train_df["medical_abstract"]
    y_train = train_df["condition_label"]

    pipeline = build_pipeline()

    print("Treinando modelo...")
    pipeline.fit(X_train, y_train)

    test_df = load_test()
    X_test = test_df["medical_abstract"]
    y_test = test_df["condition_label"]

    metrics = evaluate_model(
        pipeline,
        X_test,
        y_test,
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = MODEL_DIR / "models.joblib"
    joblib.dump(
        pipeline,
        model_path,
    )

    metrics_path = MODEL_DIR / "metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(f"\nModelo salvo em: {model_path}")
    print(f"Métricas salvas em: {metrics_path}")


if __name__ == "__main__":
    main()
