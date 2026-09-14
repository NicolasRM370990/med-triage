# Roteiro de vídeo — Med-Triage (modelo STAR)

**Duração alvo:** 4 min 50 s (máximo 5 min)  
**Ritmo:** ~140 palavras/minuto, tom técnico e direto  
**Suporte:** slides `Med-Triage_Analise_STAR.pptx`  
**Formato:** falar para a câmera; os slides entram nos cortes indicados.

---

## Antes de gravar

- Abrir o PPT no slide 1.
- Ter um exemplo de `POST /predict` em mente (dor no peito / falta de ar).
- Não vender o modelo como diagnóstico. É **apoio à triagem de texto**.
- Números do último treino (`models/baseline/metrics.json`): accuracy **0,587**, F1 macro **0,588**, recall macro **0,629**.

---

## 0:00–0:20 · Abertura (slide 1)

**Fala**

Olá. Este é o **Med-Triage**: um serviço que lê um abstract médico em inglês e devolve uma de cinco categorias clínicas, com score de confiança e um aviso quando essa confiança fica baixa.

Não é um notebook isolado. O objetivo foi sair do CSV e chegar em uma **API pronta para operação**, com testes, container e esteira de entrega.

---

## 0:20–0:35 · Agenda STAR (slide 2)

**Fala**

Vou contar o projeto no modelo **STAR**: o cenário, a tarefa, o que implementamos de fato, e o resultado — incluindo o que ainda não está maduro.

---

## S — Situation · 0:35–1:40 (slides 3 e 4)

### 0:35–1:15 · O problema (slide 3)

**Fala**

A literatura biomédica cresce mais rápido do que qualquer equipe consegue ler. Abstracts descrevem a condição do paciente, e quem faz triagem precisa de um **primeiro filtro padronizado**.

O corpus trabalha com cinco grupos: neoplasias, doenças do sistema digestivo, do sistema nervoso, cardiovasculares e condições patológicas gerais.

O valor de negócio só aparece se esse classificador **chegar em produção**: contrato de API, saúde do serviço e alguma observabilidade. Um modelo no disco, sozinho, não resolve o fluxo. E isto **não substitui** avaliação clínica.

### 1:15–1:40 · Os dados (slide 4)

**Fala**

Usamos o **Medical Abstracts TC Corpus**: **11.550** textos de treino e **2.888** de teste. Zero nulos, zero duplicados. Colunas simples: rótulo e abstract.

O ponto crítico é o **desbalanceamento**. A classe “general pathological conditions” tem cerca de **um terço** dos exemplos. Digestive system, a menor, fica perto de **dez por cento**. Qualquer métrica só de acurácia mascara isso. Por isso o norte é **F1 macro**.

---

## T — Task · 1:40–2:10 (slide 5)

**Fala**

A tarefa era fechar um **MVP de ponta a ponta**.

Primeiro, explorar o corpus. Depois, treinar um baseline reproduzível de NLP clássico e avaliar no hold-out oficial. Em seguida, **servir** o modelo: texto entra; rótulo, nome da condição e confiança saem. Por último, **operar**: Python 3.12 alinhado, Docker, testes, CI/CD e métricas.

Recorte consciente: não era o melhor paper de embeddings biomédicos. Era um produto mínimo, auditável, que outra pessoa consegue subir.

---

## A — Action · 2:10–4:15 (slides 6 a 9)

### 2:10–2:45 · Arquitetura (slide 6)

**Fala**

O repositório segue um mapa de **MLOps**: `data/raw`, `src`, `models`, `tests`, Docker e workflows no GitHub.

O caminho real está em **`src/`**: loader, vetorizador TF-IDF, treino e API FastAPI. Os testes vivos cobrem o contrato da API. README, Makefile e `.env.example` já descrevem o setup.

Pastas como `monitoring/`, `airflow/` e `notebooks/` ainda são **esqueleto**. Vale ser honesto: a intenção de plataforma está no mapa; a implementação está concentrada no serviço de inferência.

### 2:45–3:20 · Modelo (slide 7)

**Fala**

O baseline é um **pipeline scikit-learn**: TF-IDF com unigramas e bigramas, stopwords em inglês, `sublinear_tf`, e **regressão logística** com `class_weight` balanceado. Vetor e classificador viajam no mesmo `joblib`. Isso simplifica o deploy: a API carrega um arquivo só.

Avaliamos accuracy, precision, recall, F1 macro e matriz de confusão. As métricas também vão para `metrics.json`. Escolhemos esse stack porque é rápido, interpretável e suficiente para validar o fluxo até o endpoint.

O módulo `src/features/tfidf.py` **é** o que o treino usa. Sem atalho duplicado no script.

### 3:20–3:50 · API (slide 8)

**Fala**

A API tem **`/`** redirecionando para o Swagger, **`/health`**, **`/predict`** e **`/metrics`**.

O contrato é simples. Entra `text`. Sai o rótulo numérico, o nome da condição, a confiança entre 0 e 1, e `low_confidence` quando o score fica abaixo de **0,5**. Texto vazio ou payload incompleto retorna **422**. A latência de `/predict` vai para o Prometheus.

Os nomes vêm do CSV de labels, não de um dicionário hardcoded. O modelo carrega na subida: se o artefato não existe, o serviço falha cedo.

Num teste com dor no peito e falta de ar, o ponto a observar é se a confiança dispara o aviso — a classe genérica ainda absorve casos ambíguos.

### 3:50–4:15 · MLOps (slide 9)

**Fala**

Do lado de engenharia: **sete testes** de contrato passam; o CI roda Ruff e pytest em **Python 3.12**, a mesma versão do `pyproject` e da imagem Docker. A imagem usa **uv**, copia código, modelo e labels. O Compose sobe a API na porta 8000 com healthcheck. No push para `main`, o CD publica no **GitHub Container Registry** com a tag do commit.

A esteira básica existe. O que ainda não sobe no Compose é Grafana. O treino continua sendo um script local, não um job orquestrado.

---

## R — Result · 4:15–5:00 (slides 10 a 12)

### 4:15–4:40 · O que está no ar (slide 10)

**Fala**

**Resultado.** Temos um fluxo completo: dado, treino, artefato, API, teste e imagem.

Os números do modelo, no hold-out oficial, são modestos: accuracy **0,59** e F1 macro **0,59**, com recall macro um pouco acima, **0,63**. Para triagem clínica real, isso **não basta**. Para um desafio de produto, prova que o caminho existe e que o balanceamento já puxou o recall.

O que já funciona bem é o contrato da API, o fail-fast do modelo e a base de observabilidade. O que ainda é placeholder é dashboard, orquestração e testes do pipeline de treino.

### 4:40–4:55 · Próximos passos (slide 11)

**Fala**

Próximo salto, nesta ordem: **melhorar o modelo** — embeddings biomédicos ou threshold por classe; ligar Prometheus e Grafana de verdade; travar métricas no CI; e deixar explícito, sempre, que isto **apoia triagem, não substitui o clínico**.

### 4:55–5:00 · Fechamento (slide 12)

**Fala**

Em uma frase: saímos do corpus e chegamos no endpoint. O Med-Triage já classifica, devolve confiança e nasce com testes e CD. O próximo capítulo é qualidade do modelo e observabilidade visual.

Obrigado. Fico à disposição para perguntas.

---

## Mapa de tempo (teleprompter)

| Bloco        | Relógio     | Slide | Segundos |
|--------------|-------------|-------|----------|
| Abertura     | 0:00–0:20   | 1     | 20       |
| Agenda       | 0:20–0:35   | 2     | 15       |
| Situation    | 0:35–1:40   | 3–4   | 65       |
| Task         | 1:40–2:10   | 5     | 30       |
| Action       | 2:10–4:15   | 6–9   | 125      |
| Result       | 4:15–5:00   | 10–12 | 45       |
| **Total**    |             |       | **300**  |

Se ultrapassar 5 minutos, corte nesta ordem: detalhes do Compose, lista de pastas vazias, e o exemplo numérico da predição. Não corte Situation (desbalanceamento) nem Result (F1 e disclaimer clínico).

---

## Cortes se faltar fôlego (versão 3 min 30 s)

1. Abertura + STAR (20 s)  
2. Situation: problema + 5 classes + desbalanceamento (50 s)  
3. Task: quatro entregas (20 s)  
4. Action: pipeline + endpoints + CI/CD 3.12 (70 s)  
5. Result: F1 ~0,59, 7 testes, próximo passo modelo + Grafana (50 s)

---

## Frases de backup (perguntas)

- **“Por que não BERT?”** — Baseline primeiro: artefato único, treino barato, API simples. Transformer entra quando o F1 macro do clássico saturar.  
- **“Dá para usar em hospital?”** — Não como decisão clínica. Só como filtro de texto, com humano no loop e com o flag de baixa confiança.  
- **“O que eu faria amanhã?”** — Subir o modelo (embeddings ou threshold por classe) e um dashboard Prometheus/Grafana. A esteira 3.12 já está alinhada.
