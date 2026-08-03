# AutoDS — Autonomous Data Scientist Platform

AutoDS is an end-to-end autonomous AI-powered Data Science platform designed to automate data profiling, executive AI analysis, human-in-the-loop data cleaning, exploratory data analysis (EDA), machine learning preprocessing, automated machine learning (AutoML), model evaluation, prediction inference, RAG chat assistance, and interactive dashboard reporting.

---

## 🚀 How to Run

### Method 1: Using Docker Compose (Recommended)

Make sure Docker Desktop is installed and running, then execute:

```bash
docker-compose up --build
```

Once running, access the services:
- **Interactive Workspace Dashboard**: `http://localhost:3000/dashboard`
- **Landing Page**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/api/v1`
- **OpenAPI Swagger Docs**: `http://localhost:8000/api/v1/docs`

---

### Method 2: Running Locally (Development Mode)

#### 1. Start the Backend API (FastAPI)
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Start the Frontend (Next.js)
Open a second terminal window:
```bash
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start Next.js development server
npm run dev
```

Open your browser at `http://localhost:3000/dashboard`.

---

## 🛠 Tech Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS, Lucide React, Axios.
- **Backend**: FastAPI, Python 3.12, SQLAlchemy (Async), Alembic, Celery, Redis, DuckDB, pandas, scikit-learn, XGBoost, LightGBM, SHAP, OpenAI.
- **Database**: PostgreSQL + pgvector.
