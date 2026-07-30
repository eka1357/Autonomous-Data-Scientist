# API Specification - AutoDS

## Overview
All REST endpoints are exposed via FastAPI under `/api/v1`.

## Core Resources

### Datasets (`/api/v1/datasets`)
- `POST /api/v1/datasets/upload` - Upload a new dataset (CSV, Parquet, JSON).
- `GET /api/v1/datasets/` - List uploaded datasets.
- `GET /api/v1/datasets/{id}` - Retrieve metadata & summary statistics for a dataset.
- `DELETE /api/v1/datasets/{id}` - Remove dataset and associated artifacts.

### Profiling (`/api/v1/profiles`)
- `POST /api/v1/profiles/{dataset_id}/generate` - Trigger data profiling task.
- `GET /api/v1/profiles/{dataset_id}` - Retrieve profiling summary.

### Health Check
- `GET /health` - System health status.
