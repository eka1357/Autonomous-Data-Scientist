# API Specification

## Overview

The AutoDS backend exposes RESTful APIs under `/api/v1`.

All APIs return standardized JSON responses.

Authentication uses JWT Bearer tokens passed via the `Authorization: Bearer <token>` header.

### Security & IDOR Prevention Notice
All endpoints scoped to projects, datasets, jobs, reports, or chats validate ownership before returning data or performing actions:
`WHERE project.user_id == current_user.id`. Requests targeting unauthorized resources return `403 Forbidden` or `404 Not Found`.

---

# Authentication & Session Management

## Register
`POST /auth/register`

Request Body:
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "SecurePassword123!"
}
```

Response (`201 Created`):
```json
{
  "success": true,
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "Account created successfully"
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```

## Login
`POST /auth/login`

Request Body:
```json
{
  "email": "jane@example.com",
  "password": "SecurePassword123!"
}
```

Response (`200 OK`):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "dGhpcy1pcy...",
    "expires_in": 3600
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```

## Refresh Token
`POST /auth/refresh`

Request Body:
```json
{
  "refresh_token": "dGhpcy1pcy..."
}
```

## Logout
`POST /auth/logout` (Requires Auth)

## Current User Profile
`GET /auth/me` (Requires Auth)

---

# Projects

## List Projects
`GET /projects`

## Create Project
`POST /projects`

Request Body:
```json
{
  "name": "E-Commerce Churn Analysis",
  "description": "Customer retention and churn prediction workspace"
}
```

## Get Project Details
`GET /projects/{project_id}`

## Delete Project
`DELETE /projects/{project_id}`

---

# Dataset Management

## Upload Dataset
`POST /datasets/upload` (Multipart Form)

Form Fields:
- `file`: Binary CSV or XLSX file (Max size: 100MB).
- `project_id`: Target project UUID.

Validation Rules:
- MIME-type magic binary verification.
- Rejection of CSV formula injection prefixes (`=`, `@`, `+`, `-`).
- Excel macro-free verification.

Response (`201 Created`):
```json
{
  "success": true,
  "data": {
    "dataset_id": "987e6543-e89b-12d3-a456-426614174000",
    "filename": "churn_data.csv",
    "file_size_bytes": 10485760,
    "status": "uploaded"
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```

## Get Dataset Details & Metadata
`GET /datasets/{dataset_id}`

## Delete Dataset
`DELETE /datasets/{dataset_id}`

---

# Analysis Pipeline

## Start Analysis
`POST /analysis/start`

Request Body:
```json
{
  "dataset_id": "987e6543-e89b-12d3-a456-426614174000",
  "target_column": "churn_label", // Optional target prediction column
  "auto_approve_cleaning": false // Optional boolean flag
}
```

Response (`202 Accepted`):
```json
{
  "success": true,
  "data": {
    "job_id": "456e7890-e89b-12d3-a456-426614174000",
    "status": "queued"
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```

## Get Analysis Status
`GET /analysis/{job_id}`

Response (`200 OK`):
```json
{
  "success": true,
  "data": {
    "job_id": "456e7890-e89b-12d3-a456-426614174000",
    "status": "awaiting_approval", // queued | running | awaiting_approval | completed | failed
    "current_stage": "data_cleaning",
    "cleaning_status": "proposed",
    "progress_percent": 30,
    "elapsed_time_seconds": 12.4
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```

## Get Cleaning Preview & Proposed Diff
`GET /analysis/{job_id}/cleaning-preview`

Response (`200 OK`):
```json
{
  "success": true,
  "data": {
    "job_id": "456e7890-e89b-12d3-a456-426614174000",
    "missing_values_handled": { "age": "imputed_median", "income": "imputed_mean" },
    "outliers_detected": 42,
    "proposed_action": "remove_outliers_and_impute",
    "affected_rows_count": 42
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```

## Approve / Override Cleaning Proposal
`POST /analysis/{job_id}/approve-cleaning`

Request Body:
```json
{
  "approve": true,
  "custom_overrides": {
    "outlier_strategy": "clip" // Optional override
  }
}
```

## Stream Live Pipeline Events (WebSocket / SSE)
`GET /analysis/{job_id}/stream` (Server-Sent Events)

## Cancel Analysis Job
`POST /analysis/{job_id}/cancel`

---

# Reports & ML Results

## List Project Reports
`GET /reports?project_id={project_id}`

## Download Report PDF
`GET /reports/{report_id}/download`

## Get Trained ML Models & Metrics
`GET /analysis/{job_id}/models`

Response includes algorithms trained, cross-validation metrics, and SHAP feature importances.

## Get Rendered EDA Charts
`GET /analysis/{job_id}/charts`

---

# Dataset Chat (RAG Assistant)

`POST /chat`

Request Body:
```json
{
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Which feature contributed most to customer churn?"
}
```

Response (`200 OK`):
```json
{
  "success": true,
  "data": {
    "answer": "Based on the trained XGBoost model, 'tenure' and 'monthly_charges' had the highest SHAP feature importance scores.",
    "sources": [
      { "type": "model_metric", "id": "shap_importance_table" }
    ]
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```

---

# Error Response Format

Standard Error Payload:
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to access this resource."
  },
  "timestamp": "2026-07-30T22:00:00Z"
}
```