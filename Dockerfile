FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copia somente os arquivos de dependências
COPY pyproject.toml uv.lock ./

# Instala as dependências travadas
RUN uv sync --frozen --no-dev --no-install-project

# Código da aplicação
COPY src ./src

# Modelo treinado
COPY models ./models

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]