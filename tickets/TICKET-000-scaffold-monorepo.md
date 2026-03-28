# Scaffold monorepo + Compose + health

**ID:** TICKET-000  
**Plano detalhado:** [`docs/plans/TICKET-000-scaffold-monorepo-detailed-plan.md`](../docs/plans/TICKET-000-scaffold-monorepo-detailed-plan.md)

## Objetivo

Estrutura inicial do monorepo (`apps/api`, `apps/web`, `apps/worker`, `packages/*`, `infra`), Compose para desenvolvimento e healthchecks mínimos — base para todos os tickets seguintes.

## Escopo

Layout de pastas alinhado a `.cursor/rules/01-architecture.mdc`; Docker Compose; variáveis em `.env.example`; endpoints ou páginas de health; scripts de arranque documentados.

## Fora de escopo

Regras de negócio de auth, tenant e ingestão (tickets 001+).

## Impacto técnico

Infra, DX, CI futuro.

## Subtarefas

- Monorepo: `apps/api`, `apps/web`, `worker` placeholder, `packages/contracts`, `packages/shared`
- `infra/compose` + stack Portainer opcional
- Health API (`/health` ou equivalente) e build Angular
- Documentação: `apps/api/README.md`, `infra/portainer/README.md` conforme existente

## Critérios de aceite

`docker compose up` sobe API + DB + dependências necessárias; health responde; web compila.

## Riscos

Segredos commitados — usar apenas `.env.example`.

## Dependências

Nenhuma (ticket zero).
