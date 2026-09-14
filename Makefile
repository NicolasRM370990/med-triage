.PHONY: sync train api test lint

sync:
	uv sync --dev

train:
	uv run python src/training/train.py

api:
	uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

test:
	uv run pytest -v

lint:
	uv run ruff check .
