# System Architecture

## Overview

AutoDS follows a modular client-server architecture with AI agent orchestration, asynchronous task processing, and vector-backed knowledge retrieval.

The system consists of:

- Frontend (Next.js 15, React 19, Tailwind CSS v4, TypeScript)
- Backend API (FastAPI, Python 3.12, Pydantic v2)
- Task Execution & Event Broker (Celery, Redis)
- AI Agent Layer (LangGraph, OpenAI)
- Machine Learning & Data Engine (DuckDB, scikit-learn, XGBoost, SHAP)
- Database & Vector Storage (PostgreSQL 17, pgvector, SQLAlchemy 2.x, Alembic)
- File Storage (S3-compatible object storage / local storage for dev)

Each layer maintains strict boundary separation.

---

# High Level Architecture & Event Flow

```
Frontend (Next.js)
  │
  ├── REST API / WebSockets
  ▼
FastAPI Backend ──(Enqueue Job)──► Redis Queue ──► Celery Workers
  │                                                     │
  ├── (Persist Metadata & Status)                        ├── (Agent Execution & ML Engine)
  ▼                                                     ▼
PostgreSQL + pgvector ◄──(Update Status / Logs)─────────┴──► S3 File Storage
  ▲
  │ (Pub/Sub Stream)
FastAPI WS/SSE ◄─────── Redis Pub/Sub
```

### Detailed Event Execution Flow

1. **Job Enqueue**: Client triggers analysis via REST API (`POST /analysis/start`). FastAPI creates a record in PostgreSQL with status `queued` and enqueues a task payload in Redis.
2. **Celery Worker Execution**: Celery worker pulls the job from Redis, updates PostgreSQL job status to `running`, and publishes a progress event to Redis Pub/Sub.
3. **Real-time Event Streaming**: FastAPI WebSocket/SSE endpoint subscribes to the job's Redis Pub/Sub channel and broadcasts real-time progress updates to the Frontend.
4. **Data Cleaning & Approval Pause**: Data Cleaning Agent analyzes dataset quality and produces a cleaning proposal. Job status transitions to `awaiting_approval`.
5. **Approval Resume**: Upon receiving user approval (`POST /analysis/{job_id}/approve-cleaning`), Celery resumes execution for EDA, ML, Insights, and Report Generation.
6. **Completion**: Celery worker uploads generated charts, models, and PDF reports to S3, writes embeddings to `pgvector`, updates PostgreSQL status to `completed`, and emits a final completion event.

---

# Frontend

- **Technology**: Next.js 15, React 19, TypeScript, Tailwind CSS v4, Zustand, TanStack Query, Plotly.js.
- **Responsibilities**: User authentication, dataset upload, real-time progress dashboard, interactive cleaning approval interface, charts, reports, and Chat UI.
- The frontend never performs data analysis directly; all communication is via REST APIs and WebSockets.

---

# Backend & Security

- **Technology**: FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, JWT, Loguru.
- **Responsibilities**: API routing, payload validation, authentication, project authorization, file upload sanitization, task enqueuing, and event subscription.

### IDOR Prevention & Security Policies
- **Tenant Isolation**: Every database query on user-owned entities (Projects, Datasets, Jobs, Reports, Chats) strictly enforces ownership scope:
  `WHERE project.id = :project_id AND project.user_id = :current_user_id`.
- **File Upload Validation**:
  - Max File Size: Enforced 100MB limit.
  - MIME-Type Verification: Magic-number binary header checks (not just file extension).
  - Sanitization: Strip CSV formula injection prefixes (`=`, `@`, `+`, `-`), disable Excel macro execution.

---

# AI Agent Layer & Workflow

The AI system is managed by **LangGraph** with single-responsibility agents:

1. **Coordinator Agent**: Manages pipeline state transitions and coordinates output handoffs between agents.
2. **Data Cleaning Agent**: Detects missing values, duplicates, and outliers. Generates a structured cleaning log and diff proposal for user approval.
3. **EDA Agent**: Generates summary statistics, correlation matrices, and chart specifications executed via DuckDB.
4. **Machine Learning Agent**: Identifies task type (or respects optional `target_column`), trains baseline models, performs cross-validation, and computes SHAP feature importance.
5. **Business Insight Agent**: Synthesizes executive summaries, key findings, and recommendations.
6. **Chat Agent**: Answers user questions against dataset metadata and RAG embeddings using safe DuckDB SQL generation.

---

# Embeddings & Vector Storage Design (RAG)

- **Vector Storage**: PostgreSQL 17 with `pgvector` extension storing 1536-dimensional embeddings (OpenAI `text-embedding-3-small`).
- **Indexed Contents**: Dataset column profiles, statistical summaries, EDA findings, executive summary chunks, and model performance metrics.
- **Query Strategy**: When a user asks a question in "Dataset Chat", the Chat Agent performs semantic similarity search over `dataset_embeddings` to construct RAG prompt context, and executes sanitized DuckDB SQL queries for exact calculations.

---

# Machine Learning & Data Engine

- **Technology**: DuckDB, Pandas, NumPy, scikit-learn, XGBoost, SHAP.
- **Data Engine**: DuckDB handles dataset profiling, filtering, cleaning, and aggregation out-of-core without loading entire files into memory.
- **ML Engine**: Operates on sampled/cleaned memory-bounded arrays for model training and SHAP explainability.

---

# Error Handling & Resilience

- Every API error returns structured JSON (`success`, `error` object with `code` and `message`, and `timestamp`).
- Pipeline tracks stage-level status (`cleaning_status`, `eda_status`, `ml_status`). Failure in ML does not discard completed EDA or profiling artifacts.