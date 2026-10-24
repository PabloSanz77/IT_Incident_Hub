# IT Incident Hub — Starter

Sistema de gestión de incidentes TI para el proyecto integrador DevOps.

## Stack
- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy
- Base de datos: PostgreSQL
- Contenedores: Docker Compose
- Calidad: pytest (backend), Vitest (frontend)
- CI: Azure Pipelines y GitHub Actions (plantillas iniciales)

## Requisitos
- Docker Desktop iniciado
- Git
- Node.js LTS y npm (solo si deseas ejecutar el frontend fuera de Docker)

## Ejecutar con Docker
1. Copia `.env.example` a `.env`.
2. Desde la raíz ejecuta:
   ```bash
   docker compose up --build
   ```
3. Frontend: http://localhost:5173
4. API: http://localhost:8000
5. Swagger: http://localhost:8000/docs

La base de datos se crea mediante SQLAlchemy al iniciar el backend. Para un entorno real, añadir migraciones con Alembic antes del release.

## Ejecutar pruebas del backend localmente
Desde `backend/`, instala dependencias de `requirements.txt` y ejecuta:
```bash
python -m pytest -v
```
Las pruebas usan una base SQLite temporal y no requieren PostgreSQL.

## Importante sobre la entrega académica
Este ZIP es una base de trabajo. No crea automáticamente recursos en tu cuenta de Azure DevOps ni en GitHub. Los Boards, PR reales, revisión, agente autohospedado, artefactos publicados, versiones y evidencias deben configurarse y ejecutarse en tus cuentas. No presentes plantillas como si fueran ejecuciones reales.

## Flujo de trabajo con Git

- `main`: rama principal del proyecto.
- `feature/pipeline-fix`: rama de trabajo para ajustes de integración continua.
- Los cambios deben revisarse mediante Pull Requests antes de integrarse en la rama principal.