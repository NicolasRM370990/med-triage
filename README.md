# Med-Triage

API de classificação de abstracts médicos em inglês utilizando técnicas de **NLP e Machine Learning**, disponibilizada como serviço REST com FastAPI e estruturada seguindo práticas de **MLOps**.

O projeto contempla treinamento e avaliação do modelo, API de inferência, testes automatizados, CI com GitHub Actions, containerização com Docker, monitoramento com Prometheus e Grafana e orquestração de retreinamento utilizando Apache Airflow.

> **Aviso:** este projeto possui finalidade acadêmica e experimental. A classificação produzida pelo modelo não substitui avaliação, diagnóstico ou decisão clínica realizada por profissionais de saúde.

---

## 1. Objetivo

O objetivo do projeto é disponibilizar um modelo leve de NLP capaz de classificar textos médicos em uma das cinco categorias presentes no dataset utilizado.

A solução foi construída considerando um cenário de produção no qual o modelo precisa ser:

- treinado e avaliado de forma reproduzível;
- disponibilizado por meio de uma API REST;
- testado automaticamente;
- executado em containers;
- monitorado;
- submetido a um processo de retreinamento orquestrado;
- integrado a um pipeline de CI.

### Categorias

O modelo utiliza os cinco grupos clínicos do dataset:

| Label | Condition |
|---:|---|
| 1 | `neoplasms` |
| 2 | `digestive system diseases` |
| 3 | `nervous system diseases` |
| 4 | `cardiovascular diseases` |
| 5 | `general pathological conditions` |

Essas categorias representam as classes utilizadas para classificação dos abstracts. **Não devem ser interpretadas como níveis de urgência ou prioridade clínica.**

---

# 2. Arquitetura

A solução é composta pelos seguintes componentes:

```text
                         ┌─────────────────────┐
                         │      Dataset        │
                         │   Medical Abstracts │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Training Pipeline │
                         │ TF-IDF + Logistic   │
                         │     Regression      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    models.joblib    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │                     │
                         │ /                   │
                         │ /predict            │
                         │ /health             │
                         │ /metrics            │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
        ┌──────────────────┐                ┌──────────────────┐
        │   Prometheus     │                │      Client      │
        │    :9090         │                │                  │
        └────────┬─────────┘                └──────────────────┘
                 │
                 ▼
        ┌──────────────────┐
        │     Grafana      │
        │      :3000       │
        └──────────────────┘


        ┌───────────────────────────────────────────┐
        │                 Airflow                   │
        │                                           │
        │ train_model → evaluate_model             │
        │                                           │
        └──────────────────┬────────────────────────┘
                           │
                           ▼
                  models/baseline/models.joblib
```

---

# 3. Stack tecnológica

| Tecnologia | Finalidade |
|---|---|
| Python 3.12 | Linguagem principal |
| uv | Gerenciamento de ambiente e dependências |
| pandas | Manipulação dos datasets |
| scikit-learn | Pipeline de Machine Learning |
| TF-IDF | Representação dos textos |
| Logistic Regression | Classificador |
| joblib | Persistência do modelo |
| FastAPI | API REST |
| Uvicorn | Servidor ASGI |
| pytest | Testes automatizados |
| Ruff | Lint e qualidade de código |
| Docker | Containerização |
| Docker Compose | Orquestração local dos serviços |
| Prometheus | Coleta de métricas |
| Grafana | Visualização das métricas |
| Apache Airflow | Orquestração do treinamento/retreinamento |
| PostgreSQL | Banco de metadados do Airflow |
| GitHub Actions | Integração contínua |

---

# 4. Dataset

O projeto utiliza os arquivos CSV disponibilizados para o desafio:

```text
data/raw/
├── medical_tc_train.csv
├── medical_tc_test.csv
└── medical_tc_labels.csv
```

O dataset de treinamento possui as colunas:

```text
condition_label
medical_abstract
```

O `condition_label` representa a classe utilizada durante o treinamento.

A aplicação utiliza o arquivo de labels para apresentar os nomes das categorias de forma legível na API.

---

# 5. Pipeline de Machine Learning

O modelo utilizado é um pipeline tradicional e leve de classificação de texto:

```text
Texto médico
     │
     ▼
TF-IDF
     │
     ▼
Logistic Regression
     │
     ▼
Classe prevista
     │
     ▼
Condition name
```

## TF-IDF

A representação textual é criada por `src/features/tfidf.create_vectorizer()` e reutilizada no treino:

- conversão para lowercase;
- remoção de stop words em inglês;
- unigramas e bigramas;
- `min_df=2`;
- `max_df=0.95`;
- `sublinear_tf=True`.

Configuração:

```python
TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
)
```

## Classificador

O classificador utilizado é:

```python
LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42,
)
```

O modelo completo é persistido como:

```text
models/baseline/models.joblib
models/baseline/metrics.json
```

---

# 6. Treinamento

O treinamento pode ser executado localmente com:

```bash
uv run python -m src.training.train
```

O pipeline:

1. carrega o dataset de treinamento;
2. separa texto e labels;
3. constrói o pipeline TF-IDF + Logistic Regression;
4. treina o modelo;
5. carrega o conjunto de teste;
6. realiza as previsões;
7. calcula as métricas, o classification report e a matriz de confusão;
8. salva o modelo treinado e as métricas.

Artefatos:

```text
models/baseline/models.joblib
models/baseline/metrics.json
```

---

# 7. Avaliação

O modelo é avaliado utilizando o conjunto de teste oficial.

As métricas utilizadas são:

- Accuracy;
- Precision Macro;
- Recall Macro;
- F1 Macro;
- Classification Report;
- Matriz de Confusão.

### Resultado do baseline

Hold-out oficial (`medical_tc_test.csv`), registrado em `models/baseline/metrics.json`:

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.5873 |
| Precision Macro | 0.5724 |
| Recall Macro | 0.6286 |
| F1 Macro | 0.5884 |

Os resultados devem ser interpretados como métricas experimentais do modelo acadêmico e não como indicadores de desempenho clínico.

---

# 8. API

A API foi desenvolvida utilizando **FastAPI**.

Inicialização local:

```bash
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Após iniciar:

```text
http://localhost:8000
```

A documentação interativa fica disponível em:

```text
http://localhost:8000/docs
```

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/` | Redirect para `/docs` |
| GET | `/health` | Verifica a saúde da aplicação |
| POST | `/predict` | Classifica um texto médico |
| GET | `/metrics` | Expõe métricas para Prometheus |
| GET | `/docs` | Documentação OpenAPI |

---

# 9. Endpoint `/predict`

### Request

```http
POST /predict
```

Body:

```json
{
  "text": "The patient presented with persistent chest pain and shortness of breath."
}
```

### Response

```json
{
  "condition_label": 5,
  "condition_name": "general pathological conditions",
  "confidence": 0.3013,
  "low_confidence": true
}
```

- `condition_label`: classe numérica prevista pelo modelo (1 a 5).
- `condition_name`: nome legível lido de `data/raw/medical_tc_labels.csv`.
- `confidence`: maior probabilidade estimada pelo classificador (entre 0 e 1).
- `low_confidence`: `true` quando `confidence` é menor que 0,5.

### Mapeamento das classes

```text
1 → neoplasms
2 → digestive system diseases
3 → nervous system diseases
4 → cardiovascular diseases
5 → general pathological conditions
```

---

# 10. Health Check

Endpoint:

```http
GET /health
```

Exemplo de resposta:

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

Esse endpoint permite verificar se a aplicação está disponível e se o modelo foi carregado corretamente.

---

# 11. Monitoramento

A aplicação expõe métricas utilizando `prometheus-client`.

Endpoint:

```text
GET /metrics
```

Entre as métricas instrumentadas estão:

```text
http_requests_total
http_request_duration_seconds
http_errors_total
```

Essas métricas são coletadas pelo Prometheus.

---

# 12. Prometheus

O Prometheus é executado como serviço Docker.

Configuração:

```text
monitoring/prometheus/prometheus.yml
```

O Prometheus coleta métricas da API através de:

```text
http://api:8000/metrics
```

O intervalo de coleta configurado é de 5 segundos.

A interface do Prometheus fica disponível em:

```text
http://localhost:9090
```

---

# 13. Grafana

O Grafana é utilizado para visualização das métricas coletadas pelo Prometheus.

Interface:

```text
http://localhost:3000
```

Credenciais configuradas para o ambiente local:

```text
Username: admin
Password: admin
```

O dashboard contempla métricas de observabilidade da API, incluindo pelo menos:

### Total de requisições

```promql
sum(http_requests_total)
```

### Latência média

```promql
rate(http_request_duration_seconds_sum[5m])
/
rate(http_request_duration_seconds_count[5m])
```

### Taxa de erros

```promql
sum(rate(http_errors_total[5m]))
```

A arquitetura de observabilidade é:

```text
FastAPI
   │
   │ /metrics
   ▼
Prometheus
   │
   │ PromQL
   ▼
Grafana
```

---

# 14. Docker

A aplicação pode ser executada utilizando Docker Compose:

```bash
docker compose up --build
```

O ambiente reúne os principais componentes da solução:

```text
API
Prometheus
Grafana
PostgreSQL
Airflow Webserver
Airflow Scheduler
```

Para encerrar:

```bash
docker compose down
```

Para verificar os serviços:

```bash
docker compose ps
```

---

# 15. Airflow

O Apache Airflow é utilizado para orquestrar o processo de treinamento e retreinamento do modelo.

A interface está disponível em:

```text
http://localhost:8080
```

Credenciais do ambiente local:

```text
Username: admin
Password: admin
```

O Airflow utiliza PostgreSQL como banco de metadados.

---

# 16. DAG de treinamento

A DAG está localizada em:

```text
dags/train_model.py
```

Nome:

```text
medical_model_retraining
```

O fluxo é:

```text
train_model
     │
     ▼
save_model
     │
     ▼
evaluate_model
```

A DAG reutiliza as funções existentes no módulo de treinamento, evitando duplicação da lógica de Machine Learning.

As principais funções utilizadas são:

```python
train_model()
save_model()
load_model()
evaluate_model()
```

Essa separação mantém a responsabilidade bem definida:

```text
src/training/
    → lógica de Machine Learning

dags/
    → orquestração do processo
```

A DAG está configurada para execução periódica:

```text
@weekly
```

Além disso, pode ser executada manualmente pela interface do Airflow.

---

# 17. Retreinamento

Quando a DAG é executada:

```text
Airflow
   │
   ▼
Carrega dataset
   │
   ▼
Treina modelo
   │
   ▼
Salva models.joblib
   │
   ▼
Avalia modelo
```

O artefato produzido é:

```text
models/baseline/models.joblib
```

Esse mesmo artefato é utilizado pela API para realizar inferências.

Assim, temos o fluxo:

```text
Airflow
   │
   ▼
Novo treinamento
   │
   ▼
Novo modelo
   │
   ▼
FastAPI
   │
   ▼
Predições
```

---

# 18. Testes

Os testes automatizados estão em:

```text
tests/
└── test_api.py
```

A suíte cobre:

- health check;
- predição;
- validação de texto vazio;
- validação de campo obrigatório;
- endpoint de métricas.

Execução:

```bash
uv run pytest -v
```

Resultado esperado:

```text
5 passed
```

---

# 19. Lint e qualidade de código

O projeto utiliza Ruff.

Execução:

```bash
uv run ruff check .
```

O objetivo é detectar problemas de estilo, imports e qualidade antes da integração das alterações.

---

# 20. CI com GitHub Actions

O projeto possui pipeline de integração contínua em:

```text
.github/workflows/ci.yml
```

O workflow é executado em pushes e pull requests e realiza:

```text
Checkout
   ↓
Configuração do Python
   ↓
Instalação do uv
   ↓
Instalação das dependências
   ↓
Ruff
   ↓
Pytest
```

Dessa forma, alterações no código passam por validações automatizadas antes de serem consideradas prontas.

---

# 21. Gerenciamento de dependências

O projeto utiliza `uv`.

Instalação/sincronização:

```bash
uv sync --dev
```

As dependências de produção são declaradas no:

```text
pyproject.toml
```

O lockfile utilizado para garantir versões reprodutíveis é:

```text
uv.lock
```

---

# 22. Estrutura do projeto

Estrutura principal:

```text
med-triage/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── dags/
│   └── train_model.py
│
├── data/
│   └── raw/
│       ├── medical_tc_train.csv
│       ├── medical_tc_test.csv
│       └── medical_tc_labels.csv
│
├── models/
│   └── baseline/
│       └── models.joblib
│
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml
│   │
│   └── grafana/
│       ├── dashboards/
│       └── provisioning/
│
├── src/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── model.py
│   │   └── schemas.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py
│   │
│   └── training/
│       ├── __init__.py
│       └── train.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── .gitignore
├── Dockerfile
├── Dockerfile.airflow
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── uv.lock
```

Arquivos gerados automaticamente, como `__pycache__`, arquivos `.pyc`, ambientes virtuais e artefatos temporários, não devem ser versionados.

---

# 23. Execução local

## Instalar dependências

```bash
uv sync --dev
```

## Treinar o modelo

```bash
uv run python -m src.training.train
```

## Executar a API

```bash
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## Executar testes

```bash
uv run pytest -v
```

## Executar lint

```bash
uv run ruff check .
```

---

# 24. Execução completa com Docker

Para executar a infraestrutura completa:

```bash
docker compose up --build
```

Serviços principais:

| Serviço | Porta | Função |
|---|---:|---|
| FastAPI | 8000 | API de inferência |
| Prometheus | 9090 | Coleta de métricas |
| Grafana | 3000 | Dashboard |
| Airflow | 8080 | Orquestração de treinamento |
| PostgreSQL | interna | Metadados do Airflow |

Endpoints úteis:

```text
API:
http://localhost:8000/docs

Prometheus:
http://localhost:9090

Grafana:
http://localhost:3000

Airflow:
http://localhost:8080
```

---

# 25. Fluxo MLOps completo

O projeto implementa um fluxo simplificado de Machine Learning em produção:

```text
                    ┌──────────────┐
                    │    Dataset   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Airflow    │
                    │  Scheduling  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Training   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Evaluation  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Model Artifact│
                    │ models.joblib │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Prediction  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Prometheus   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Grafana    │
                    └──────────────┘
```

Paralelamente, o código é validado continuamente:

```text
Git Push / Pull Request
          │
          ▼
   GitHub Actions
          │
     ┌────┴────┐
     ▼         ▼
   Ruff     Pytest
```

---

# 26. Conclusão

O Med-Triage demonstra uma arquitetura compacta de MLOps aplicada à classificação de textos médicos, combinando:

```text
Machine Learning
       +
FastAPI
       +
Docker
       +
GitHub Actions
       +
Prometheus
       +
Grafana
       +
Airflow
```

O projeto busca demonstrar não apenas a criação de um modelo de Machine Learning, mas também os componentes necessários para disponibilizá-lo como serviço, testar sua qualidade, acompanhar seu comportamento operacional e automatizar seu processo de treinamento.

> **Projeto acadêmico — Tech Challenge Fase 03**