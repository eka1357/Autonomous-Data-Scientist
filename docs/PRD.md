# Product Requirements Document (PRD)

# Project Name

AutoDS — Autonomous Data Scientist

---

# Vision

AutoDS is an AI-powered platform that transforms raw datasets into actionable insights with minimal user input.

A user uploads a CSV or Excel dataset, and the platform automatically performs data cleaning (with optional user approval), exploratory data analysis (EDA), machine learning, business insight generation, visualization, and report generation.

The goal is to make advanced data science accessible to analysts, students, researchers, and businesses without requiring programming knowledge.

---

# Problem Statement

Performing data analysis requires multiple tools, technical expertise, and significant time.

Users often need to:

- clean datasets
- explore data
- build machine learning models
- compare algorithms
- create dashboards
- generate reports

These tasks are repetitive and require expertise.

AutoDS automates this workflow using AI agents while providing human-in-the-loop controls.

---

# Objectives

The application should:

- Accept datasets from users.
- Automatically understand dataset structure.
- Clean the data and present a cleaning proposal for user review/approval.
- Perform EDA.
- Detect the machine learning problem (with support for an optional user-specified target prediction column).
- Train multiple ML models.
- Compare model performance.
- Generate business insights.
- Allow users to chat with their dataset using vector-backed RAG.
- Produce downloadable reports.

---

# Core Features (MVP)

## Authentication & Authorization
- Register
- Login
- Refresh Token & Session Management
- Multi-tenant data isolation (IDOR protection)

---

## Project Management
Users can create multiple projects.
Each project stores datasets, analyses, reports, and chat sessions.

---

## Dataset Upload & Sanitization
Supported formats:
- CSV
- XLSX

Validation:
- Maximum file size (100MB)
- Supported encoding & MIME magic header verification
- Formula injection protection & Excel macro stripping
- Duplicate detection

---

## Dataset Profiling
Automatically detect:
- rows, columns, data types
- missing values, duplicate rows, unique values, summary statistics

---

## Data Cleaning & Human-in-the-Loop Approval
Automatically detect missing values, duplicates, datatypes, and outliers.

- **Cleaning Proposal**: Generate a structured diff report showing intended imputation, row dropping, or outlier handling.
- **User Approval**: Allow users to review, approve, or override proposed cleaning actions before proceeding to EDA & ML training.
- Every cleaning action is audited and logged.

---

## Exploratory Data Analysis
Generate summary statistics, histograms, box plots, scatter plots, correlation matrices, and missing value visualizations.

---

## Machine Learning
Automatically determine whether the dataset requires:
- regression
- classification
- clustering
- forecasting

Support an optional user-provided `target_column`.

Train multiple models, compare evaluation metrics, compute SHAP feature importance, and recommend the best model.

---

## Business Insights & Dataset Chat
- Generate executive summary, key findings, recommendations, risks, and opportunities.
- **Dataset Chat**: Vector-indexed RAG assistant (`pgvector` + OpenAI embeddings) allowing users to ask natural language questions about findings and query stats safely via DuckDB.

---

## Report Generation
Generate downloadable PDF reports containing EDA, ML performance benchmarks, charts, and business recommendations.

---

# Non Functional Requirements

The application must be:
- scalable (DuckDB out-of-core data processing, Celery task queue, S3 object storage)
- modular (Clean Architecture, LangGraph single-responsibility agents)
- secure (IDOR protection, file sanitization, JWT authentication)
- responsive (Real-time WebSockets / SSE progress streaming)
- production ready