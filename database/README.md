# Database
PostgreSQL is configured in `compose.yaml`. The current starter creates tables through SQLAlchemy at application startup.
Before a production-style release, add Alembic migrations, backup/restore guidance, and a documented migration test.
