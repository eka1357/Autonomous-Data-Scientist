# AutoDS — Autonomous Data Scientist Platform

![AutoDS Platform](https://img.shields.io/badge/Production-Ready-brightgreen.svg)
![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![Next.js](https://img.shields.io/badge/Next.js-15.5-black.svg)
![React](https://img.shields.io/badge/React-19.1-61DAFB.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-1.1-FFF000.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17%20%2B%20pgvector-336791.svg)

AutoDS is a production-grade, autonomous AI-powered Data Science platform. It transforms raw, messy tabular datasets into clean, preprocessed ML models, visual EDA reports, competitive AutoML leaderboards, SHAP explainability insights, single/batch prediction APIs, and interactive RAG chat assistants without requiring manual code.

---

## 🚀 Key Features Across All 14 Phases

1. **Authentication & Workspaces (Phases 1–3)**: JWT token-based authentication, user registration, project workspaces, and IDOR-protected resource ownership.
2. **Dataset Management (Phase 4)**: CSV/XLSX file upload validation, magic-byte checking, formula injection sanitization, file size limits (100MB), and PostgreSQL tracking.
3. **Data Profiling Engine (Phase 5)**: Out-of-core streaming statistics powered by DuckDB (row counts, column data types, missing value percentages, and duplicate row detection).
4. **AI Executive Analysis (Phase 6)**: Executive data summaries, automated ML task classification (Classification, Regression, Clustering), and candidate target column detection.
5. **Human-in-the-Loop Data Cleaning (Phase 7)**: Automated cleaning plans (whitespace trimming, missing value imputation, duplicate removal), human diff approvals, and Jinja2 HTML report generation.
6. **Feature Engineering & Preprocessing (Phase 8)**: Categorical encodings (Label, One-Hot, Ordinal), numeric scalings (Standard, MinMax, Robust, Normalize), VarianceThreshold feature selection, saving `ml_ready.csv`, `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`.
7. **Automated Machine Learning (Phase 9)**: Multi-algorithm competitive training (Logistic Regression, Random Forest, XGBoost, LightGBM, Linear Regression, KMeans, DBSCAN, Agglomerative Clustering), 5-fold cross-validation, and `best_model.joblib` saving.
8. **Model Evaluation & SHAP Explainability (Phase 10)**: Accuracy, Precision, Recall, F1 Score, ROC AUC, Confusion Matrix, MAE, MSE, RMSE, R², MDI feature importances, SHAP values, and downloadable `evaluation_report.html`.
9. **Prediction Inference Service (Phase 11)**: Single-sample JSON inference, batch predictions, CSV upload predictions, downloadable result CSVs, and database history logs.
10. **RAG AI Data Science Assistant (Phase 12)**: Multi-artifact vector context retrieval across all 7 stage outputs, real-time Server-Sent Events (SSE) streaming responses, citations, and chat history management.
11. **Interactive Glassmorphic Dashboard (Phase 13)**: 8-tab Next.js dashboard (Dataset Overview, Cleaning, EDA, Preprocessing, AutoML, Evaluation, Prediction, AI Assistant Chat) built with Tailwind CSS.
12. **Production Hardening (Phase 14)**: Celery task offloading, Redis queueing, structured JSON logging (`loguru`), Prometheus metrics (`/metrics`), Slowapi rate limiting, health probes (`/health`, `/health/liveness`, `/health/readiness`), and Alembic migrations.

---

## 🌟 Recent Enhancements (Phase 15 - UI/UX & ML Core Upgrade)

- **Interactive Recharts Visualizations**: Replaced static Matplotlib charts in the UI with dynamic, interactive `Recharts` for missing values and data distributions.
- **ONNX Model Export**: Added support for exporting best-performing models to standard `ONNX` format via `skl2onnx` alongside traditional `joblib` binaries.
- **Advanced Multivariate Imputation**: Upgraded the data cleaning engine to support `KNNImputer` and `IterativeImputer` for more robust missing value interpolation.
- **High-Cardinality Safeguards**: Added automatic fallback to Label Encoding if One-Hot Encoding encounters >50 unique values, preventing memory explosions.
- **Global Dark Theme Engine**: Overhauled the frontend Next.js architecture with strict CSS variables and custom scrollbars for a cohesive, premium dark-mode glassmorphic aesthetic.

---

## 🛠 Tech Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Lucide React, Axios, TanStack React Query.
- **Backend**: FastAPI, Python 3.12, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic, Celery, Redis, DuckDB, pandas, scikit-learn, XGBoost, LightGBM, SHAP, Jinja2, LangGraph, OpenAI.
- **Database**: PostgreSQL 17 with `pgvector` extension.
- **Infrastructure & Monitoring**: Docker, Docker Compose, Prometheus Instrumentator, Slowapi.

---

## 📁 System Architecture & Directory Structure

```
Autonomous Data Scientist/
├── backend/
│   ├── alembic/              # Database migration scripts (001 -> 011)
│   ├── app/
│   │   ├── api/              # FastAPI v1 endpoints & dependencies (auth, datasets, models, predictions, assistant)
│   │   ├── core/             # Core ML engines (cleaner, profiler, preprocessor, automl, evaluator, RAG)
│   │   ├── db/               # Async SQLAlchemy session & Base declarative models
│   │   ├── models/           # ORM SQLAlchemy database models
│   │   ├── repositories/     # Data access layer repositories
│   │   ├── schemas/          # Pydantic v2 data validation schemas
│   │   ├── services/         # Application business logic services
│   │   ├── worker/           # Celery async tasks & connection pool
│   │   └── main.py           # FastAPI application entry point
│   ├── tests/                # Comprehensive unit & integration pytest suite
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js 15 App Router pages & global layout
│   │   ├── components/       # Glassmorphic 8-tab dashboard components
│   │   ├── lib/              # Axios API client & utility functions
│   │   └── providers/        # React Query providers
│   ├── tailwind.config.ts    # Tailwind CSS configuration
│   └── package.json          # Frontend dependencies
└── docker-compose.yml        # Multi-container orchestration specification
```

---

## ⚡ How To Run

### Option 1: Quickstart via Docker Compose (Recommended)

This spins up all 5 isolated services (**PostgreSQL + pgvector**, **Redis**, **FastAPI Backend**, **Celery Worker**, and **Next.js Frontend**) with automatic healthchecks.

```bash
docker-compose up --build
```

#### Access Points:
- **Interactive UI**: [http://localhost:3000](http://localhost:3000)
- **Dashboard Workspace**: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
- **FastAPI OpenAPI Docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Health Check Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

### Option 2: Manual Local Setup (Development Mode)

#### Prerequisites:
- Python 3.10+
- Node.js 20+ & `npm`
- PostgreSQL 17 (with `pgvector` extension)
- Redis server

#### 1. Backend Setup:
```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Alembic Database Migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Start Celery Worker (Separate Terminal):
```bash
cd backend
.\venv\Scripts\Activate.ps1

# Run Celery async task processor
celery -A app.worker.celery_app.celery_app worker --loglevel=info
```

#### 3. Frontend Setup:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Next.js dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Running Automated Tests

To execute the complete 14-phase automated unit and integration test suite:

```bash
cd backend
pytest
```

---

## 🎯 Technical Interview Questions & Answers

### 1. Architectural Design & Pattern Choices

**Q1: How does AutoDS strictly implement Clean Architecture, and why is this separation critical for an AI platform?**  
**A:** AutoDS separates concerns into four distinct layers:
1. **Domain Entities (`models/`)**: Pure SQLAlchemy database models containing schema definitions and constraints.
2. **Data Access (`repositories/`)**: Encapsulates all query construction, transactional logic, and persistence calls (`select`, `flush`, `commit`).
3. **Core Computation (`core/`)**: Stateless, framework-agnostic Python ML modules (`cleaner.py`, `automl_engine.py`, `evaluator.py`, `profiler.py`).
4. **Application & Delivery (`services/` & `api/`)**: `services/` orchestrates workflows, while `api/` handles HTTP request validation, status codes, and serialization.  
*Why it matters*: Machine learning frameworks (scikit-learn, PyTorch, DuckDB) evolve quickly. By isolating pure ML logic inside `core/`, core algorithms can be updated or swapped without refactoring FastAPI HTTP schemas or SQLAlchemy queries.

---

### 2. High-Performance Data Engineering & Scaling

**Q2: How does the profiling engine handle multi-gigabyte datasets without running into Out-of-Memory (OOM) errors?**  
**A:** AutoDS uses **DuckDB** inside [profiler.py](file:///c:/Users/mahin/OneDrive/Desktop/Projects/Data_projects/Autonomous%20Data%20Scientist/backend/app/core/profiler.py) for out-of-core streaming data processing. Instead of loading the entire CSV into pandas in Python memory, DuckDB streams data chunks directly from disk, executing vectorized C++ SQL queries for row counts, data types, missing value percentages, and duplicate detection within strict container memory limits.

**Q3: How are long-running machine learning training tasks prevented from blocking the main API thread?**  
**A:** When a dataset is uploaded or a training request is issued, FastAPI validates input parameter schemas and enqueues a task payload into **Redis**. A background **Celery worker** picks up the task and executes the CPU/GPU heavy pipeline (`process_uploaded_dataset`) asynchronously. The user receives an immediate `201 Created` HTTP response with a dataset ID and can poll progress or listen to status events without blocking HTTP main looper threads.

---

### 3. Database Connection Management & Celery Pooling

**Q4: How does Celery prevent PostgreSQL connection pool exhaustion during concurrent dataset processing?**  
**A:** In [tasks.py](file:///c:/Users/mahin/OneDrive/Desktop/Projects/Data_projects/Autonomous%20Data%20Scientist/backend/app/worker/tasks.py), AutoDS uses a module-level lazy connection engine initializer (`get_worker_session_maker()`) configured with `pool_size=10`, `max_overflow=20`, and `pool_pre_ping=True`. Instead of opening and closing database engines per task execution, worker threads reuse pooled database connections across task executions, preventing Postgres connection leaks.

---

### 4. RAG AI Assistant Architecture & Server-Sent Events

**Q5: How does the RAG AI Assistant assemble context across 7 different pipeline stages, and how is real-time streaming achieved?**  
**A:** 
1. **Multi-Artifact Aggregation**: `AssistantService._build_dataset_context` fetches records from `DatasetProfile`, `DatasetAnalysis`, `DatasetCleaning`, `DatasetEDA`, `DatasetPreprocessing`, `ModelTraining`, and `ModelEvaluation`.
2. **Context Formatting**: [rag_engine.py](file:///c:/Users/mahin/OneDrive/Desktop/Projects/Data_projects/Autonomous%20Data%20Scientist/backend/app/core/rag_engine.py) formats structured JSON summaries into a prompt context block accompanied by citation source tags (`[Dataset Profile]`, `[EDA Insights]`, `[Model Evaluation]`).
3. **SSE Streaming Resiliency**: In `AssistantService.stream_chat_response`, chunks are yielded over an `AsyncGenerator`. The stream is wrapped in `try/except` blocks so that if an LLM network or token error occurs midway, an explicit `data: [ERROR]` event is emitted before terminating with `data: [DONE]`, preventing front-end UI freezes.

---

### 5. Security & Input Sanitization

**Q6: What security measures protect AutoDS against CSV Formula Injection and IDOR vulnerabilities?**  
**A:**
1. **CSV Formula Injection**: In [dataset_service.py](file:///c:/Users/mahin/OneDrive/Desktop/Projects/Data_projects/Autonomous%20Data%20Scientist/backend/app/services/dataset_service.py), uploaded CSV files are checked for formula prefixes (`=`, `@`, `+`, `-`). If detected on the header line, the byte stream is sanitized with a single quote prefix `'` to prevent formula execution in spreadsheet software like Microsoft Excel.
2. **Magic Byte File Validation**: `.xlsx` files are verified against zip magic bytes (`PK\x03\x04`) to prevent disguised malicious file uploads.
3. **IDOR (Insecure Direct Object Reference) Protection**: All dataset, cleaning, AutoML, and prediction endpoints enforce `get_by_id_and_user` joins in the repository layer, ensuring users can only read or mutate datasets that belong to their authorized projects.

---

### 6. Machine Learning Preprocessing & Leakage Prevention

**Q7: How does AutoDS prevent data leakage during preprocessing and train/test splitting?**  
**A:** In [preprocessor.py](file:///c:/Users/mahin/OneDrive/Desktop/Projects/Data_projects/Autonomous%20Data%20Scientist/backend/app/core/preprocessor.py), the target column is isolated before scaling or encoding feature columns. Categorical encodings (`LabelEncoder`, `OneHotEncoder`, `OrdinalEncoder`) and scalers (`StandardScaler`, `MinMaxScaler`, `RobustScaler`) operate strictly on feature spaces, and `train_test_split` is applied using stratified sampling (for classification) or random sampling prior to model training.
