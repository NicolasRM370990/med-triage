from datetime import UTC, datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.training.train import (
    evaluate_model,
    load_model,
    save_model,
    train_model,
)


def train_task():
    model = train_model()
    save_model(model)

    print("Modelo treinado e salvo com sucesso.")


def evaluate_task():
    model = load_model()
    metrics = evaluate_model(model)

    print("===== MÉTRICAS DO MODELO =====")

    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")


with DAG(
    dag_id="medical_model_retraining",
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    schedule="@weekly",
    catchup=False,
    tags=["mlops", "training", "medical"],
) as dag:

    train_model_task = PythonOperator(
        task_id="train_model",
        python_callable=train_task,
    )

    evaluate_model_task = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_task,
    )

    train_model_task >> evaluate_model_task