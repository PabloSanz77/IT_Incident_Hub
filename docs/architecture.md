# Architecture — IT Incident Hub
Browser → React/TypeScript/Vite → FastAPI REST API → SQLAlchemy → PostgreSQL.
Docker Compose provides a repeatable local development environment.
The API currently exposes incident CRUD-style creation/read/update, filtering, comments, health, and dashboard endpoints.
## Known limitations
- Authentication and role-based authorization are not implemented.
- Schema creation currently uses SQLAlchemy `create_all`; Alembic migrations are still needed.
- The starter pipelines need to be run and adjusted in the actual accounts.
