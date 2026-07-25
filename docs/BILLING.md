# Billing

## O que faz

Aplica limites do plano (uploads/mês, armazenamento) e quotas opcionais por utilizador/grupo no upload.

## Como funciona

- Plano activo via `tenant_subscriptions` → `plans`.
- Verificação em `POST /uploads` (`BillingService.ensure_storage_for_new_upload` + contagem mensal).
- Resposta **HTTP 402** quando a quota é excedida.
- Contexto em `GET /me/context` (`plan`, `storage`) — `fourpro_contracts.billing`.
- Detalhe: [ARCHITECTURE.md](./ARCHITECTURE.md) § Cotas de armazenamento.

## Como instalar

Migrações Core (`core__*`) + seed de planos — [INSTALLATION.md](./INSTALLATION.md).

## Como configurar

Limites no plano; admin configura `max_storage_mb` / `quota_group_id` via rotas `/tenant/...`.

## Como testar

Testes de quota na API; exemplo de contexto em `docs/examples/01-auth.sh`.

## Como evoluir

Cobrança externa, seats Desktop (pós-017), novos métricas → ADR + contratos + OpenAPI.
