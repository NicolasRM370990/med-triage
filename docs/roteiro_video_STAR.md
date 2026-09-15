# Roteiro de vídeo — Med-Triage (modelo STAR)

**Duração alvo:** 4 min 50 s (máximo 5 min)  
**Ritmo:** ~140 palavras/minuto, tom técnico e direto  
**Suporte:** slides `Med-Triage_Analise_STAR.pptx`  
**Formato:** falar para a câmera; os slides entram nos cortes indicados.

---

## Antes de gravar

- Abrir o PPT no slide 1 (equipe visível).
- Ter um exemplo de `POST /predict` em mente (dor no peito / falta de ar).
- Não vender o modelo como diagnóstico. É **apoio à triagem de texto**.
- Números em `models/baseline/metrics.json`: accuracy **0,587**, precision macro **0,572**, recall macro **0,629**, F1 macro **0,588**.

---

## 0:00–0:25 · Abertura (slide 1)

**Fala**

Olá. Este é o Med-Triage: um serviço que lê um abstract médico em inglês e devolve uma de cinco categorias clínicas, com score de confiança e um aviso quando essa confiança fica baixa. O objetivo foi sair do CSV e chegar em um fluxo de MLOps: API, Docker, Grafana e retreino no Airflow.

---

## 0:25–0:40 · Agenda STAR (slide 2)

**Fala**

Vou contar o projeto no modelo **STAR**: o cenário, a tarefa, o que implementamos, e o resultado — incluindo o limite do modelo.

---

## S — Situation · 0:40–1:40 (slides 3 e 4)

### 0:40–1:15 · O problema (slide 3)

**Fala**

A literatura biomédica cresce mais rápido do que qualquer equipe consegue ler. Abstracts descrevem a condição do paciente, e quem faz triagem precisa de um **primeiro filtro padronizado**.

O corpus trabalha com cinco grupos: neoplasias, doenças do sistema digestivo, do sistema nervoso, cardiovasculares e condições patológicas gerais. Essas classes **não** são níveis de urgência.

O valor só aparece se o classificador **chegar em produção**. E isto **não substitui** avaliação clínica.

### 1:15–1:40 · Os dados (slide 4)

**Fala**

Usamos o **Medical Abstracts TC Corpus**: **11.550** textos de treino e **2.888** de teste. Zero nulos, zero duplicados.

O ponto crítico é o **desbalanceamento**. A classe “general pathological conditions” tem cerca de **um terço** dos exemplos. Digestive system fica perto de **dez por cento**. Por isso o norte é **F1 macro**.

---

## T — Task · 1:40–2:10 (slide 5)

**Fala**

A tarefa era um **MVP de ponta a ponta**: explorar o corpus, treinar um baseline reproduzível, servir o modelo por API e **operar** — Python 3.12, Compose com monitoramento e Airflow, CI/CD.

Não era o melhor paper de embeddings. Era um produto auditável, que outra pessoa consegue subir com `docker compose up`.

---

## A — Action · 2:10–4:15 (slides 6 a 9)

### 2:10–2:45 · Arquitetura (slide 6)

**Fala**

O repositório segue um mapa de **MLOps**. O código vive em **`src/`**. O retreino está em **`dags/`**. O Compose sobe API, Prometheus, Grafana, Postgres e Airflow.

O fluxo é contínuo: o CSV em `data/raw` treina o modelo; a DAG grava `models.joblib` e `metrics.json`; a API responde em `/predict`; o Prometheus coleta `/metrics` e o Grafana mostra o dashboard.

### 2:45–3:20 · Modelo (slide 7)

**Fala**

O baseline é **TF-IDF** via `create_vectorizer()` — unigramas, bigramas e `sublinear_tf` — mais **regressão logística com class_weight balanceado**. Vetor e classificador viajam no mesmo `joblib`. As funções de treino e avaliação são as mesmas do script local e da DAG.

Avaliamos accuracy, precision, recall e F1 macro no hold-out oficial e gravamos o resultado em **metrics.json**.

### 3:20–3:50 · API (slide 8)

**Fala**

A API tem **`/`** redirecionando para o Swagger, **`/health`**, **`/predict`** e **`/metrics`**.

Entra `text`. Sai rótulo, nome da condição, confiança e `low_confidence` abaixo de **0,5**. Texto vazio retorna **422**. Os nomes vêm do CSV de labels. O modelo carrega na subida: se o artefato não existe, o serviço falha cedo. No exemplo de dor no peito do README, a confiança fica perto de **0,30** e o aviso dispara.

### 3:50–4:15 · MLOps (slide 9)

**Fala**

O runtime é **Python 3.12** no projeto, no CI e na imagem. O quality gate roda Ruff. Grafana em **:3000** mostra requisições, latência e erro. Airflow em **:8080** agenda o retreino **semanal**. Push em `main` publica a imagem no GHCR.

---

## R — Result · 4:15–5:00 (slides 10 a 12)

### 4:15–4:40 · O que está no ar (slide 10)

**Fala**

**Resultado.** O fluxo existe: dado, treino, `models.joblib`, `metrics.json`, API, dashboard e orquestração.

Os números do hold-out: accuracy **0,59**, F1 macro **0,59**, recall macro **0,63** — o balanceamento puxou o recall. Para triagem clínica real, **ainda não basta**. Para o desafio, a plataforma está de pé.

O que já funciona é o contrato da API e a plataforma. O que limita o produto é o próprio classificador.

### 4:40–4:55 · Próximos passos (slide 11)

**Fala**

Próximo salto: **melhorar o modelo** — embeddings ou threshold por classe — recarregar a API depois da DAG, alertar no Grafana e manter o disclaimer clínico.

### 4:55–5:00 · Fechamento (slide 12)

**Fala**

Saímos do corpus e chegamos no endpoint, com monitoramento e retreino. O Med-Triage já opera; o próximo capítulo é qualidade do modelo.

Obrigado. Fico à disposição para perguntas.

---

## Mapa de tempo (teleprompter)

| Bloco        | Relógio     | Slide | Segundos |
|--------------|-------------|-------|----------|
| Abertura     | 0:00–0:25   | 1     | 25       |
| Agenda       | 0:25–0:40   | 2     | 15       |
| Situation    | 0:40–1:40   | 3–4   | 60       |
| Task         | 1:40–2:10   | 5     | 30       |
| Action       | 2:10–4:15   | 6–9   | 125      |
| Result       | 4:15–5:00   | 10–12 | 45       |
| **Total**    |             |       | **300**  |

Se ultrapassar 5 minutos, corte detalhes de portas do Compose. Não corte Situation (desbalanceamento) nem Result (F1 e disclaimer).

---

## Cortes se faltar fôlego (versão 3 min 30 s)

1. Abertura com equipe + STAR (25 s)  
2. Situation: problema + 5 classes + desbalanceamento (45 s)  
3. Task: quatro entregas (20 s)  
4. Action: pipeline + API + Compose/Airflow (70 s)  
5. Result: F1 ~0,59, plataforma pronta, próximo passo é o modelo (50 s)

---

## Frases de backup (perguntas)

- **“Por que não BERT?”** — Baseline primeiro: artefato único, treino barato, API simples. Transformer entra quando o F1 macro do clássico saturar.  
- **“Dá para usar em hospital?”** — Não como decisão clínica. Só como filtro de texto, com humano no loop e com o flag de baixa confiança.  
- **“O que fariam amanhã?”** — Subir o modelo (embeddings ou threshold por classe) e fechar o loop: DAG gera artefato, API passa a usar o novo joblib com alerta no Grafana.
