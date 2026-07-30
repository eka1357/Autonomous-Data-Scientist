# Architecture Decision Records (ADR) - AutoDS

## ADR-001: Project Directory Layout Standard
- **Status**: Approved
- **Context**: Need a clear, predictable workspace layout for AI agents and human developers.
- **Decision**: Adopt `.agents/rules/agents.md` for AI rules, `docs/` for specs, `frontend/`, `backend/`, and `docker/` for code separation.
- **Consequences**: Standardized structure across frontend, backend, and documentation components.

## ADR-002: Technology Stack Selection
- **Status**: Approved
- **Context**: Need high performance, type safety, and modern standard tooling.
- **Decision**: Use Python 3.12 + FastAPI + SQLAlchemy 2 for backend, and Next.js + React + Tailwind + TypeScript for frontend.
