# System Architecture - AutoDS

## Architectural Overview
AutoDS follows Clean Architecture principles, ensuring clear separation of concerns across presentation, domain logic, data persistence, and background processing layers.

```
+-------------------------------------------------------+
|                    Frontend (Next.js)                 |
+-------------------------------------------------------+
                           | REST / WS
+-------------------------------------------------------+
|                   Backend (FastAPI)                   |
|  +--------------------+  +-------------------------+  |
|  |   API Controllers  |  |  Services & Use Cases   |  |
|  +--------------------+  +-------------------------+  |
|  | Domain Entities    |  |  Repositories (SQLAlchemy)|
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
|                 Database & Task Queue                 |
|  +--------------------+  +-------------------------+  |
|  |  PostgreSQL / DB   |  | Async Task Execution    |  |
|  +--------------------+  +-------------------------+  |
+-------------------------------------------------------+
```

## Tech Stack Guidelines
- **Frontend**: Next.js (App Router), TypeScript, React, Tailwind CSS.
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic.
- **Database**: PostgreSQL / SQLite (for dev).
