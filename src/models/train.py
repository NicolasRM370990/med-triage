from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from src.data.loader import load_train

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT_DIR / "models" / "baseline"

def main() -> None:
    df = load_train()

    X = df["medical_abstract"]
    y = df["condition_label"]

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1,2),
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
    pipeline.fit(X,y)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = MODEL_DIR / "models.joblib"

    joblib.dump(
        pipeline,
        model_path,
    )

    print(f"Modelo salvo em: {model_path}")


if __name__ == "__main__":
    main()

