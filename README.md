# AutoDS — Autonomous Data Scientist Platform

AutoDS is an end-to-end autonomous AI-powered Data Science platform designed to automate data profiling, executive AI analysis, human-in-the-loop data cleaning, exploratory data analysis (EDA), machine learning preprocessing, automated machine learning (AutoML), model evaluation, prediction inference, RAG chat assistance, and interactive dashboard reporting.

---

## 🚀 Features & Capabilities Across All 14 Phases

1. **Authentication & Workspaces (Phase 1-3)**: JWT authentication, user registration, project workspaces, role-based access control.
2. **Dataset Management (Phase 4)**: CSV/XLSX file upload validation, size limit checks, metadata extraction, PostgreSQL storage tracking.
3. **Data Profiling Engine (Phase 5)**: Out-of-core streaming statistics powered by DuckDB (row counts, missing value %, column data types, duplicate counts).
4. **AI Executive Analysis (Phase 6)**: Executive summaries, recommended ML tasks (Classification/Regression/Clustering), target column candidates.
5. **Human-in-the-Loop Data Cleaning (Phase 7)**: Automated cleaning plans, whitespace trimming, column dropping, duplicate removal, human diff approval, saving `cleaned.csv` and Jinja2 HTML EDA report generation.
6. **Feature Engineering & Preprocessing (Phase 8)**: Categorical encodings (Label, One-Hot, Ordinal), Numeric scalings (Standard, MinMax, Robust, Normalize), feature selection, saving `ml_ready.csv`, `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`.
7. **Automated Machine Learning (Phase 9)**: Problem type auto-detection, multi-algorithm competitive training (Logistic Regression, Random Forest, XGBoost, LightGBM, Linear Regression, KMeans, DBSCAN, Agglomerative Clustering), leaderboard comparison, saving `best_model.joblib`.
8. **Model Evaluation & Explainability (Phase 10)**: Accuracy, Precision, Recall, F1 Score, ROC AUC, Confusion Matrix, MAE, MSE, RMSE, R², 5-Fold Cross Validation, Feature Importances, SHAP value summary, saving HTML evaluation report `evaluation_report.html`.
9. **Prediction Service (Phase 11)**: Single feature JSON inference, batch predictions, CSV file upload predictions, result CSV downloads, prediction history log in DB.
10. **AI Data Science Assistant (Phase 12)**: RAG assistant querying context across all 7 project artifacts, real-time Server-Sent Events (SSE) streaming responses, report citations, persistent chat history.
11. **Interactive React Dashboard (Phase 13)**: 8-tab Next.js dashboard (Overview, Cleaning, EDA, Preprocessing, AutoML, Evaluation, Prediction, AI Assistant Chat) with dataset upload modal and report downloads.
12. **Production Readiness (Phase 14)**: Structured JSON logging, Prometheus `/metrics` endpoint, health checks (`/health`, `/health/liveness`, `/health/readiness`), Slowapi rate limiting, Docker Compose healthchecks.

---

## 🛠 Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, Lucide React, Axios, TanStack React Query.
- **Backend**: FastAPI, Python 3.12, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic, Celery, Redis, DuckDB, pandas, scikit-learn, XGBoost, LightGBM, SHAP, Jinja2, LangGraph, OpenAI.
- **Database**: PostgreSQL 17 + pgvector.
- **Deployment**: Docker, Docker Compose, Prometheus Instrumentator, Slowapi.

---

## ⚡ Quickstart & Local Deployment

### Using Docker Compose

```bash
docker-compose up --build
```

- **Frontend**: `http://localhost:3000`
- **Interactive Dashboard**: `http://localhost:3000/dashboard`
- **Backend API**: `http://localhost:8000/api/v1`
- **OpenAPI Docs**: `http://localhost:8000/api/v1/docs`
- **Prometheus Metrics**: `http://localhost:8000/metrics`
- **Health Checks**: `http://localhost:8000/api/v1/health`

---

## 🧪 Running Automated Tests

```bash
cd backend
pytest
```
