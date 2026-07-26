---
name: qa-automation-engineer
description: Garante qualidade com testes unitários, integração, E2E, API, performance e segurança; cobertura mínima 90% e relatório QA
---

# Skill: QA Automation Engineer

Nunca aceite código sem testes. Antes de declarar uma entrega pronta:

## Tipos de teste (obrigatórios por feature relevante)

1. **Unitários** — helpers, validação, segurança (hash/JWT), regras puras.
2. **Integração** — `TestClient` + DB (SQLite em memória ou Postgres marcado).
3. **API** — contratos HTTP (status, body, autenticação).
4. **E2E** — Playwright em `e2e/` (smoke / RBAC / fluxos críticos).
5. **Performance** — smoke de latência e concorrência leve (`@pytest.mark.performance` / `concurrency`).
6. **Segurança** — tenant isolation, RBAC, rate limit, tokens, spoofing (`@pytest.mark.security`).

## Cobertura

- Meta: **≥ 90%** em `fourpro_api` (omitir apenas wiring/seed documentados).
- Comando: `./scripts/run-qa-coverage.sh` ou `make qa-coverage`.
- CI deve falhar abaixo do limiar (`--cov-fail-under=90`).

## Checklist por entrega

- [ ] Fluxos felizes
- [ ] Fluxos inválidos
- [ ] Erros (HTTP/mensagem coerente)
- [ ] Timeout (cliente/API onde aplicável)
- [ ] Concorrência (marcado; opt-in CI se pesado)
- [ ] Carga / stress (smoke local ou job opcional)
- [ ] Validação de banco (persistência / isolamento)
- [ ] Rollback (transacção não deixa lixo)
- [ ] Logs (audit / technical_log quando aplicável)
- [ ] Mocks (SMTP, OTP, Celery)
- [ ] Fixtures reutilizáveis

## Markers pytest

Usar: `unit`, `integration`, `api`, `auth`, `tenant_isolation`, `rbac`, `billing`,
`ingestion`, `security`, `audit`, `performance`, `concurrency`, `slow`, `postgres`.

PR: `pytest -m "not slow and not concurrency"` (default suite já é rápida).
Nightly / opcional: `pytest -m "concurrency or performance or postgres"`.

## Relatório final (obrigatório)

Gerar/atualizar `docs/CHECKLISTS/qa-automation-report.md` via
`./scripts/generate-qa-report.sh` contendo:

1. **Cobertura** (total + ficheiros críticos)
2. **Riscos**
3. **Bugs encontrados**
4. **Cenários faltantes**
5. **Prioridade** (P0/P1/P2)

## Resposta ao utilizador

Seguir o formato global: objetivo, plano, arquivos alterados, riscos, próximos passos.
