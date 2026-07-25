# Changelog

## [Unreleased]

- **TICKET-015 Conectores:** `packages/connectors` (SPI + 6 plugins); vault Fernet; data-sources + sync worker; quota `plans.max_data_sources`.
- **TICKET-016 / 011:** modelo semântico, `/query` agregada, dashboards Web (canvas + publish), UI Fontes/Modelos/Dashboards.
- **TICKET-017 Desktop:** Electron + Vite; auth `safeStorage`; wizard fontes; publish dataset (sync) e dashboard.
- **Plataforma BI (planeamento + agentes):** ADR-001/002; tickets 015–017; `.cursor/agents/` para paralelismo.

## [0.1.0] — 2026-03-27

- Scaffold do monorepo: `apps/api` (FastAPI + Alembic + TICKET-001 login/refresh), `apps/worker` (Celery stub), `apps/web` (Angular 19), `packages/contracts`, `packages/shared`.
- Infra: `infra/compose/docker-compose.yml` (Postgres, Redis, MinIO).
- **Portainer:** `infra/portainer/stack-4pro-bi.yml` (stack única) e `stack-4pro-data-only.yml`; Dockerfiles com entrypoint Alembic + seed opcional.
- **Esteira base (tickets 000–010):** TICKET-004 tenant+JWT, 002 reset, 003 MFA (código nos logs), 005 RBAC em rotas, 006–009 upload/ingestão/worker/catálogo, 010 quotas por plano.
- Planos: `docs/plans/EXECUCAO-MESTRE.md`, `PLANOS-POR-TICKET-002-010.md`, índice em `docs/plans/README.md`.
- Script: `scripts/run-ticket-pipeline.sh` (Compose local, migrate, seed, pytest).
- Testes: pytest (health + auth + tenant) com SQLite em memória.

**Validar:** `docker compose -f infra/compose/docker-compose.yml up -d postgres`, migrações e `pytest` conforme `apps/api/README.md`.
