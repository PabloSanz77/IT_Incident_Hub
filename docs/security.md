# Security plan
- Never commit `.env`, access tokens, passwords, or real credentials.
- Use protected secret variables in Azure Pipelines/GitHub Actions.
- Use least-privilege permissions for service connections and self-hosted agents.
- Scan dependencies and document package, version, severity, remediation/acceptance decision, and date.
- Add authentication, authorization, validation, logging, and secret scanning before a production release.
