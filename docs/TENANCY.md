# Tenancy

## O que faz

Define o modelo multitenant: organizações (`tenants`), vínculo utilizador↔tenant e isolamento obrigatório de dados.

## Como funciona

- Tabelas de dados de cliente incluem `tenant_id`.
- O tenant activo vem do JWT / `Principal` após autenticação — não de parâmetros não confiáveis do cliente.
- Membership com `role` (RBAC fino em TICKET-005).
- Detalhe e sequência: [ARCHITECTURE.md](./ARCHITECTURE.md) § Multitenancy · [diagrams/auth-sequence.md](./diagrams/auth-sequence.md).

## Como instalar

Parte do schema Alembic da API — ver [INSTALLATION.md](./INSTALLATION.md).

## Como configurar

Seed cria tenant(s) de demo. Em produção, provisionar tenants sem reutilizar `RUN_SEED` após bootstrap.

## Como testar

Testes de isolamento multi-tenant na API; checklist QA (`CHECKLISTS/qa-checklist.md`).

## Como evoluir

Troca de tenant, IdP federado ou org hierárquica → ADR + impacto em contratos auth/me.
