from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
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

# Diretórios
ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT_DIR / "models" / "baseline"


def build_pipeline() -> Pipeline:
    """Cria o pipeline de TF-IDF + Logistic Regression."""
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate_model(
    pipeline: Pipeline,
    X_test,
    y_test,
) -> None:
    """Avalia o modelo utilizando o conjunto de teste."""

    predictions = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )
    recall = recall_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )
    f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    print("\n===== MÉTRICAS DO MODELO =====")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Macro : {f1:.4f}")

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


def main() -> None:
    # Carregar os dados de treinamento
    train_df = load_train()

    # Separar features e rótulos
    X_train = train_df["medical_abstract"]
    y_train = train_df["condition_label"]

    # Criar o pipeline
    pipeline = build_pipeline()

    # Treinar o modelo
    print("Treinando modelo...")
    pipeline.fit(X_train, y_train)

    # Carregar os dados de teste
    test_df = load_test()

    X_test = test_df["medical_abstract"]
    y_test = test_df["condition_label"]

    # Avaliar o modelo
    evaluate_model(
        pipeline,
        X_test,
        y_test,
    )

    # Criar diretório do modelo
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Caminho para salvar o modelo
    model_path = MODEL_DIR / "models.joblib"

    # Salvar o pipeline completo
    joblib.dump(
        pipeline,
        model_path,
    )

    print(f"\nModelo salvo em: {model_path}")


if __name__ == "__main__":
    main()

