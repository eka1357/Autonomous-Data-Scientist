# AutoDS Development Roadmap

## Vision

Build AutoDS incrementally.

Each milestone should produce a working application.

Never break previous functionality.

---

# Phase 1 — Foundation

## Milestone 1

Project Initialization

Goal

Create the complete project structure.

Tasks

- Configure backend
- Configure frontend
- Docker setup
- Environment variables
- Logging
- Configuration system
- GitHub Actions
- Health endpoint

Deliverable

Application starts successfully.

---

## Milestone 2

Authentication

Tasks

- User registration
- Login
- JWT authentication
- Password hashing
- Protected routes

Deliverable

Users can create accounts and login.

---

## Milestone 3

Project Management

Tasks

- Create project
- Edit project
- Delete project
- List projects

Deliverable

Users can manage workspaces.

---

## Milestone 4

Dataset Upload

Tasks

- Upload CSV
- Upload XLSX
- File validation
- Metadata extraction
- Storage

Deliverable

Datasets are uploaded successfully.

---

## Milestone 5

Schema Detection

Tasks

Automatically detect

- column names
- datatypes
- missing values
- duplicates
- statistics

Deliverable

Dataset profile generated.

---

# Phase 2 — AI Pipeline

## Milestone 6

Pipeline Engine

Tasks

Implement event-driven workflow.

Dataset Uploaded

↓

Schema Detected

↓

Cleaning

↓

EDA

↓

ML

↓

Insights

↓

Report

Deliverable

Pipeline executes automatically.

---

## Milestone 7

Cleaning Agent

Tasks

- Missing values
- Duplicate removal
- Datatype fixes
- Cleaning log

---

## Milestone 8

EDA Agent

Tasks

Generate

- charts
- correlations
- statistics
- distributions

---

## Milestone 9

Machine Learning Agent

Tasks

Automatically detect

- Regression
- Classification
- Clustering
- Forecasting

Train multiple models.

Compare performance.

---

## Milestone 10

Business Insight Agent

Tasks

Generate

- executive summary
- recommendations
- opportunities
- risks

---

## Milestone 11

Report Generation

Generate

- PDF
- Charts
- Tables
- Recommendations

---

# Phase 3 — Intelligence

## Milestone 12

Dataset Chat

Users ask questions.

Agent answers using

- dataset
- reports
- ML results

---

## Milestone 13

Analysis History

Store every execution.

Allow comparison.

Version analyses.

---

## Milestone 14

Experiment Tracking

Track

- preprocessing
- models
- metrics
- feature engineering

---

# Phase 4 — Production

## Milestone 15

Optimization

Improve

- performance
- caching
- background workers

---

## Milestone 16

Deployment

Docker

CI/CD

Production configuration

Monitoring

---

# Future Ideas

- Real-time collaboration
- AutoML tuning
- Time-series forecasting
- RAG over datasets
- Power BI export
- Explainable AI
- Scheduled analyses
- Team workspaces
- Notifications
- Plugin system