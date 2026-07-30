# Database Design & Schema - AutoDS

## Overview
AutoDS utilizes PostgreSQL with SQLAlchemy 2 ORM and Alembic for versioned schema migrations.

## Core Models

### `Dataset`
- `id` (UUID, PK)
- `name` (String)
- `file_path` (String)
- `file_size` (BigInteger)
- `file_format` (String)
- `created_at` (DateTime UTC)
- `updated_at` (DateTime UTC)

### `Profile`
- `id` (UUID, PK)
- `dataset_id` (UUID, FK -> `Dataset.id`)
- `summary_json` (JSONB)
- `created_at` (DateTime UTC)

### `Job`
- `id` (UUID, PK)
- `job_type` (String)
- `status` (Enum: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`)
- `error_message` (Text, Nullable)
- `created_at` (DateTime UTC)
- `completed_at` (DateTime UTC, Nullable)
