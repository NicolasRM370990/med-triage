# Med-Triage

API FastAPI que classifica abstracts médicos em inglês em cinco grupos clínicos, com score de confiança. É **apoio à triagem de texto**, não substitui avaliação clínica.

## Requisitos

- Python **3.12**
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync --dev
```

## Treino

```bash
uv run python src/training/train.py
```

O pipeline TF-IDF + regressão logística (com `class_weight="balanced"`) grava:

- `models/baseline/models.joblib`
- `models/baseline/metrics.json`

Métricas no hold-out oficial (`medical_tc_test.csv`), após o último treino:

| Métrica          | Valor  |
|------------------|--------|
| Accuracy         | 0.5873 |
| Precision macro  | 0.5724 |
| Recall macro     | 0.6286 |
| F1 macro         | 0.5884 |

## API

```bash
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Ou `uv run med-triage` / `make api`.

| Método | Rota        | Descrição                                      |
|--------|-------------|------------------------------------------------|
| GET    | `/`         | Redirect para `/docs`                          |
| GET    | `/health`   | Saúde do serviço e se o modelo carregou        |
| POST   | `/predict`  | Classifica `{"text": "..."}`                   |
| GET    | `/metrics`  | Métricas Prometheus                            |
| GET    | `/docs`     | OpenAPI                                        |

Resposta de `/predict`: `condition_label`, `condition_name`, `confidence`, `low_confidence` (true se confiança < 0,5). Os nomes vêm de `data/raw/medical_tc_labels.csv`.

Variáveis opcionais (veja `.env.example`): `HOST`, `PORT`, `MODEL_PATH`.

## Testes e lint

```bash
uv run pytest -v
uv run ruff check .
```

## Docker

```bash
docker compose up --build
```

A imagem usa Python 3.12, instala o projeto com `uv` e inclui o modelo e o CSV de rótulos.

## Layout

O código da aplicação está em `src/` (`api`, `data`, `features`, `training`). Pastas como `monitoring/` ficam como reserva de observabilidade visual (Prometheus/Grafana ainda não sobem no Compose).
