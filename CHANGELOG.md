# Changelog

## [Unreleased]

- **QA Automation Engineer:** skill Cursor, markers pytest, cobertura API ≥90% (`pytest-cov`, `.coveragerc`, `make qa-coverage`), novos testes (quota-groups, JWT/MFA negativos, parse failures, rate limit, concurrency/perf smoke, rollback), E2E API 401, relatório `docs/CHECKLISTS/qa-automation-report.md`.
- **Onda BI (execução 011–013, 015–017):** correlation ID + `/metrics` + logs JSON (013); camadas bronze/silver/gold + promote (012, ADR-004); dashboards canvas Angular + APIs (011, ADR-003); SPI conectores `packages/connectors` + fontes/sync (015); modelo semântico + `POST /query` (016); scaffold Desktop Electron + publish API (017). Briefing em `docs/product/onda-bi-marcos-bce.md`.
- **Arquitectura (Architect):** blueprint canónico em `docs/architecture/BLUEPRINT.md` (bounded contexts, portas, eventos/filas, APIs, versionamento, trade-offs); ADR modular monolith + Clean Architecture + Celery em `docs/adr/002-modular-monolith-clean-architecture.md`; checklist `docs/CHECKLISTS/architecture-checklist.md`.
- **Frontend Architect:** skill `frontend-architect` + `create-next-screen`; `docs/FRONTEND_ARCHITECTURE.md`; ADR React/Next proposto em `docs/adr/002-frontend-react-next.md`; TICKET-018 + plano detalhado; checklist e rule `03-frontend` actualizados. `apps/web` permanece Angular até aceite do ADR.
- **Plataforma BI (planeamento):** ADR-001 (conectores + Web + Desktop); plano mestre `docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`; tickets **015–017** com planos detalhados; actualização de `VISION`, `ROADMAP`, `ARCHITECTURE`, `INGESTION`, índices.

## [0.1.0] — 2026-03-27

- Scaffold do monorepo: `apps/api` (FastAPI + Alembic + TICKET-001 login/refresh), `apps/worker` (Celery stub), `apps/web` (Angular 19), `packages/contracts`, `packages/shared`.
- Infra: `infra/compose/docker-compose.yml` (Postgres, Redis, MinIO).
- **Portainer:** `infra/portainer/stack-4pro-bi.yml` (stack única) e `stack-4pro-data-only.yml`; Dockerfiles com entrypoint Alembic + seed opcional.
- **Esteira base (tickets 000–010):** TICKET-004 tenant+JWT, 002 reset, 003 MFA (código nos logs), 005 RBAC em rotas, 006–009 upload/ingestão/worker/catálogo, 010 quotas por plano.
- Planos: `docs/plans/EXECUCAO-MESTRE.md`, `PLANOS-POR-TICKET-002-010.md`, índice em `docs/plans/README.md`.
- Script: `scripts/run-ticket-pipeline.sh` (Compose local, migrate, seed, pytest).
- Testes: pytest (health + auth + tenant) com SQLite em memória.

**Validar:** `docker compose -f infra/compose/docker-compose.yml up -d postgres`, migrações e `pytest` conforme `apps/api/README.md`.
