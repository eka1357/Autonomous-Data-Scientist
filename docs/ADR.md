# Engineering Decision Records (ADR)

---

## Decision 001: FastAPI Framework Selection
- **Status**: Accepted
- **Context**: Need high-performance, type-safe REST APIs with automatic OpenAPI schema generation.
- **Decision**: Use FastAPI with Python 3.12 and Pydantic v2.

---

## Decision 002: Celery + Redis + PostgreSQL Event-Driven Architecture
- **Status**: Accepted
- **Context**: Long-running data processing, ML training, and report generation require decoupled background execution and real-time frontend updates.
- **Decision**: Celery workers consume tasks from Redis queues, publish real-time progress events via Redis Pub/Sub to FastAPI WebSockets/SSE endpoints, and write persistent state/audit records to PostgreSQL.

---

## Decision 003: PostgreSQL 17 + pgvector for Relational Data & RAG Embeddings
- **Status**: Accepted
- **Context**: Need relational data integrity for user workspaces alongside vector search capabilities for "Dataset Chat".
- **Decision**: Use PostgreSQL 17 with `pgvector` HNSW indexes for 1536-dim embeddings instead of maintaining a separate standalone vector database.

---

## Decision 004: Single-Responsibility LangGraph Agents & Human-in-the-Loop Cleaning Approval
- **Status**: Accepted
- **Context**: Automated data cleaning must not corrupt raw dataset records without user consent.
- **Decision**: Use LangGraph for single-responsibility agents. The Data Cleaning Agent emits a cleaning proposal, pausing the pipeline (`awaiting_approval`) until the user approves or overrides the proposal.

---

## Decision 005: Out-of-Core Data Processing with DuckDB
- **Status**: Accepted
- **Context**: Pandas loads datasets entirely into memory, leading to RAM exhaustion (OOM) under concurrent background processing.
- **Decision**: Perform all data profiling, cleaning, filtering, and EDA aggregation using DuckDB. Reserve Pandas/NumPy array slicing strictly for final ML model fit steps.

---

## Decision 006: Direct File Storage Separation & IDOR Security Controls
- **Status**: Accepted
- **Context**: Large raw datasets, transformed files, models, and PDF reports must not be stored in SQL BLOBs.
- **Decision**: Store metadata in PostgreSQL and raw/cleaned artifacts in Object Storage (S3). Enforce tenant ownership validation (`WHERE project.user_id == current_user.id`) across all API routes.