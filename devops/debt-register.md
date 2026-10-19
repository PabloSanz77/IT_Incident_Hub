# Initial technical debt register (validate and update during development)
| ID | Debt to verify | Risk | Proposed action |
|---|---|---|---|
| TD-01 | No Alembic migrations yet | Schema changes may be unsafe | Add migration scripts and migration test |
| TD-02 | No authentication/authorization | Any caller may change tickets | Define roles and add authentication |
| TD-03 | No pagination | Large incident lists may be slow | Add pagination and tests |
| TD-04 | Minimal API error logging | Diagnosis may be difficult | Add structured logs and request IDs |
| TD-05 | No dependency lock/security gate policy | Builds can drift; vulnerable packages may pass | Pin/lock dependencies and document scan decisions |
