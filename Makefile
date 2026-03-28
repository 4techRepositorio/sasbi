# Atalhos para desenvolvimento local (4Pro_BI).
# Requer: bash, opcionalmente Docker para alvo alembic-pg-local / e2e-one-shot / qa-optional (parcial).
.PHONY: help qa qa-alembic qa-optional qa-optional-full migrate alembic-pg-local e2e-api-local e2e-one-shot e2e-dispatch lint-actions wireframes-export stack-up stack-down stack-ps stack-logs

help:
	@echo "Alvos make (raiz do monorepo):"
	@echo "  make qa               — Ruff + pytest API + typecheck/build web + smoke API Playwright (./scripts/run-qa-gates.sh)"
	@echo "  make qa-alembic       — como qa + Postgres Docker + Alembic (RUN_ALEMBIC_PG_LOCAL=1)"
	@echo "  make qa-optional      — Alembic Postgres smoke + E2E browser se e2e/.env.e2e existir"
	@echo "  make qa-optional-full — como qa-optional + E2E one-shot (Docker stack + Playwright completo)"
	@echo "  make migrate          — alembic upgrade head (DATABASE_URL no .env)"
	@echo "  make alembic-pg-local — só job equivalente ao CI alembic-postgres (Docker)"
	@echo "  make e2e-api-local    — só uvicorn SQLite + smoke-api Playwright (sem qa completo)"
	@echo "  make e2e-one-shot     — Docker Postgres + API + ng + Playwright (stack completa; demora)"
	@echo "  make e2e-dispatch     — dispara GitHub Actions E2E (manual); precisa gh auth"
	@echo "  make lint-actions     — actionlint nos workflows (PATH ou Docker rhysd/actionlint)"
	@echo "  make wireframes-export — PDF raiz → PNG em docs/assets/wireframes/exports/ (poppler-utils)"
	@echo "  make stack-up         — Docker: infra/portainer (build + up -d); requer infra/portainer/.env"
	@echo "  make stack-down       — Docker: para a stack (sem -v; STACK_DOWN_VOLUMES=1 apaga volumes)"
	@echo "  make stack-ps         — docker compose ps da stack Portainer"
	@echo "  make stack-logs       — docker compose logs -f (passar serviços: make stack-logs SVC='api web')"
	@echo "  make help             — esta lista"

qa:
	@chmod +x scripts/run-qa-gates.sh 2>/dev/null; ./scripts/run-qa-gates.sh

qa-alembic:
	@chmod +x scripts/run-qa-gates.sh 2>/dev/null; RUN_ALEMBIC_PG_LOCAL=1 ./scripts/run-qa-gates.sh

migrate:
	@chmod +x scripts/run-db-migrate.sh 2>/dev/null; ./scripts/run-db-migrate.sh

alembic-pg-local:
	@chmod +x scripts/run-alembic-postgres-local.sh 2>/dev/null; ./scripts/run-alembic-postgres-local.sh

qa-optional:
	@chmod +x scripts/run-qa-optional.sh 2>/dev/null; ./scripts/run-qa-optional.sh

qa-optional-full:
	@chmod +x scripts/run-qa-optional.sh 2>/dev/null; QA_OPTIONAL_E2E_ONE_SHOT=1 ./scripts/run-qa-optional.sh

e2e-api-local:
	@chmod +x scripts/run-e2e-api-smoke-local.sh 2>/dev/null; ./scripts/run-e2e-api-smoke-local.sh

e2e-one-shot:
	@chmod +x scripts/run-e2e-one-shot-stack.sh 2>/dev/null; ./scripts/run-e2e-one-shot-stack.sh

e2e-dispatch:
	@chmod +x scripts/gh-e2e-dispatch.sh 2>/dev/null; ./scripts/gh-e2e-dispatch.sh

lint-actions:
	@chmod +x scripts/lint-github-actions.sh 2>/dev/null; ./scripts/lint-github-actions.sh

wireframes-export:
	@chmod +x scripts/export-wireframes-from-pdf.sh 2>/dev/null; ./scripts/export-wireframes-from-pdf.sh

stack-up:
	@chmod +x scripts/stack-up.sh 2>/dev/null; ./scripts/stack-up.sh

stack-down:
	@chmod +x scripts/stack-down.sh 2>/dev/null; ./scripts/stack-down.sh

stack-ps:
	@chmod +x scripts/stack-ps.sh 2>/dev/null; ./scripts/stack-ps.sh

stack-logs:
	@chmod +x scripts/stack-logs.sh 2>/dev/null; ./scripts/stack-logs.sh $(SVC)
