# Database Design & Schema Specification

## Overview

AutoDS utilizes PostgreSQL 17 with the `pgvector` extension for relational storage, execution audit logging, and semantic search over dataset metadata.

Large artifacts (raw files, cleaned datasets, serialized ML models, PDF reports, rendered images) reside in Object Storage (S3). The database maintains structural references, metadata, and embeddings.

---

# Core Entities & Data Types

## User (`users`)
- `id` (UUID, Primary Key, default `gen_random_uuid()`)
- `name` (VARCHAR(255), NOT NULL)
- `email` (VARCHAR(255), UNIQUE, NOT NULL)
- `password_hash` (VARCHAR(255), NOT NULL)
- `created_at` (TIMESTAMPTZ, default `NOW()`)
- `updated_at` (TIMESTAMPTZ, default `NOW()`)

## Project (`projects`)
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key -> `users.id` ON DELETE CASCADE, NOT NULL)
- `name` (VARCHAR(255), NOT NULL)
- `description` (TEXT)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

## Dataset (`datasets`)
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key -> `projects.id` ON DELETE CASCADE, NOT NULL)
- `filename` (VARCHAR(255), NOT NULL)
- `raw_storage_path` (VARCHAR(1024), NOT NULL)
- `cleaned_storage_path` (VARCHAR(1024), NULLABLE)
- `file_size_bytes` (BIGINT, NOT NULL)
- `file_type` (VARCHAR(50), NOT NULL)
- `row_count` (BIGINT, NULLABLE)
- `column_count` (INTEGER, NULLABLE)
- `uploaded_at` (TIMESTAMPTZ, default `NOW()`)

## Analysis Job (`analysis_jobs`)
- `id` (UUID, Primary Key)
- `dataset_id` (UUID, Foreign Key -> `datasets.id` ON DELETE CASCADE, NOT NULL)
- `target_column` (VARCHAR(255), NULLABLE)
- `status` (VARCHAR(50), NOT NULL) -- `queued`, `running`, `awaiting_approval`, `completed`, `failed`, `cancelled`
- `cleaning_status` (VARCHAR(50), default `pending`) -- `pending`, `proposed`, `approved`, `completed`, `skipped`
- `eda_status` (VARCHAR(50), default `pending`)
- `ml_status` (VARCHAR(50), default `pending`)
- `cleaning_proposal` (JSONB, NULLABLE) -- Stores suggested cleaning diff & stats
- `progress_percent` (INTEGER, default 0)
- `current_stage` (VARCHAR(100))
- `error_message` (TEXT, NULLABLE)
- `started_at` (TIMESTAMPTZ, NULLABLE)
- `completed_at` (TIMESTAMPTZ, NULLABLE)

## Dataset Embedding (`dataset_embeddings`)
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key -> `projects.id` ON DELETE CASCADE, NOT NULL)
- `dataset_id` (UUID, Foreign Key -> `datasets.id` ON DELETE CASCADE, NOT NULL)
- `chunk_type` (VARCHAR(50), NOT NULL) -- `column_summary`, `eda_insight`, `report_summary`
- `content` (TEXT, NOT NULL)
- `embedding` (vector(1536), NOT NULL) -- pgvector 1536-dim embedding vector
- `metadata_json` (JSONB, NULLABLE)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

## Pipeline Event (`pipeline_events`)
- `id` (UUID, Primary Key)
- `job_id` (UUID, Foreign Key -> `analysis_jobs.id` ON DELETE CASCADE, NOT NULL)
- `event_name` (VARCHAR(100), NOT NULL)
- `payload` (JSONB, NOT NULL)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

## Agent Run (`agent_runs`)
- `id` (UUID, Primary Key)
- `job_id` (UUID, Foreign Key -> `analysis_jobs.id` ON DELETE CASCADE, NOT NULL)
- `agent_name` (VARCHAR(100), NOT NULL)
- `status` (VARCHAR(50), NOT NULL)
- `input_json` (JSONB, NULLABLE)
- `output_json` (JSONB, NULLABLE)
- `duration_ms` (BIGINT, NULLABLE)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

## ML Model (`ml_models`)
- `id` (UUID, Primary Key)
- `job_id` (UUID, Foreign Key -> `analysis_jobs.id` ON DELETE CASCADE, NOT NULL)
- `algorithm_name` (VARCHAR(100), NOT NULL)
- `task_type` (VARCHAR(50), NOT NULL) -- `regression`, `classification`, `clustering`, `forecasting`
- `metrics_json` (JSONB, NOT NULL)
- `feature_importance_json` (JSONB, NULLABLE)
- `model_storage_path` (VARCHAR(1024), NOT NULL)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

## Report (`reports`)
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key -> `projects.id` ON DELETE CASCADE, NOT NULL)
- `job_id` (UUID, Foreign Key -> `analysis_jobs.id` ON DELETE CASCADE, NOT NULL)
- `report_type` (VARCHAR(50), default `pdf`)
- `storage_path` (VARCHAR(1024), NOT NULL)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

## Chat Session (`chat_sessions`)
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key -> `projects.id` ON DELETE CASCADE, NOT NULL)
- `title` (VARCHAR(255), NOT NULL)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

## Chat Message (`chat_messages`)
- `id` (UUID, Primary Key)
- `session_id` (UUID, Foreign Key -> `chat_sessions.id` ON DELETE CASCADE, NOT NULL)
- `role` (VARCHAR(20), NOT NULL) -- `user`, `assistant`, `system`
- `content` (TEXT, NOT NULL)
- `sources_json` (JSONB, NULLABLE)
- `created_at` (TIMESTAMPTZ, default `NOW()`)

---

# Indexes & Performance Tuning

- `CREATE INDEX idx_projects_user_id ON projects(user_id);`
- `CREATE INDEX idx_datasets_project_id ON datasets(project_id);`
- `CREATE INDEX idx_jobs_dataset_status ON analysis_jobs(dataset_id, status);`
- `CREATE INDEX idx_events_job_id_created ON pipeline_events(job_id, created_at DESC);`
- `CREATE INDEX idx_embeddings_vector ON dataset_embeddings USING hnsw (embedding vector_cosine_ops);`
- `CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at ASC);`