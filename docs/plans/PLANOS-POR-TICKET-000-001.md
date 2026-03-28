# Planos por ticket (000–001)

Resumo executável; planos detalhados em `docs/plans/TICKET-000-*` e `TICKET-001-*`.

---

## TICKET-000 — Scaffold monorepo + Compose + health

**Objetivo:** Monorepo (`apps/*`, `packages/*`, `infra/`), Compose local, health API, build web.

**Saída:** `docker compose up` reprodutível; sem segredos no Git.

**Dependências:** Nenhuma.

---

## TICKET-001 — Auth core

**Objetivo:** Login email/senha, tokens access+refresh, rate limit, hash seguro.

**Saída:** Rotas `/auth/login`, `/auth/refresh`; testes mínimos; base para 002–003.

**Dependências:** TICKET-000.

---

## Ordem

000 → 001 → (002, 003, 004 conforme `EXECUCAO-MESTRE.md`).
