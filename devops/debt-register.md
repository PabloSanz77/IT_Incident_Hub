# Registro de deudas técnicas — IT Incident Hub

| ID | Deuda técnica | Riesgo | Acción propuesta | Estado | Evidencia |
|---|---|---|---|---|---|
| TD-01 | No existen migraciones de Alembic | Los cambios en el esquema pueden ser inseguros o difíciles de reproducir. | Incorporar Alembic y scripts de migración. | Pendiente | Revisión de la arquitectura de persistencia. |
| TD-02 | No existe autenticación ni autorización | Los usuarios podrían acceder o modificar incidentes sin controles de identidad. | Diseñar autenticación y permisos por rol. | Pendiente | Revisión de los endpoints de la API. |
| TD-03 | No existe paginación | Las consultas podrían tardar más cuando aumente la cantidad de incidentes. | Incorporar paginación y pruebas. | Pendiente | Revisión del endpoint de consulta. |
| TD-04 | Logging y diagnóstico de errores insuficientes | Los errores pueden ser difíciles de investigar. | Incorporar logging estructurado en operaciones importantes y errores del backend. | Implementada parcialmente; pendiente de validar evidencia adicional. | `backend/app/main.py`; commit `264ac1f`. |
| TD-05 | Falta de bloqueo de dependencias y controles de seguridad | Las instalaciones pueden variar y las dependencias vulnerables podrían pasar inadvertidas. | Revisar dependencias, actualizar pytest y documentar los resultados de pip-audit. | Corrección iniciada; pendiente de completar y validar el bloqueo de dependencias | `backend/requirements.txt`; documentación de seguridad; PR #3 abierta. |

## Criterios de seguimiento

- Mantener identificadores únicos para las deudas técnicas.
- Registrar el riesgo, la acción propuesta y el estado de cada deuda.
- Vincular los cambios con commits, pruebas o solicitudes de extracción cuando exista evidencia.
- No marcar una deuda como resuelta hasta comprobar que la corrección está implementada y validada.