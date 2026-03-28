# Plano detalhado — TICKET-010 Billing core

**Papéis:** Architect · Backend Core · Product · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-010-billing-core.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-010

## 1. Objetivo

Modelar `plans`, `tenant_subscriptions` (ou equivalente) e quotas (armazenamento, jobs/ingestões, assentos) com **enforcement** nas operações críticas (upload, enqueue parse), retornando códigos e mensagens claras (ex.: 402/403) sem gateway de pagamento externo no MVP.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| CRUD admin de planos (API interna) | Stripe/Paddle (ADR futuro) |
| Middleware/service de quota antes de upload/job | Faturação por utilização em tempo real |

### 2.2 Decisões

1. Quotas lidas de tabelas configuráveis; default “generoso” em dev.
2. Enforcement centralizado (ex.: `BillingService.can_upload(tenant, size)`).
3. Documentar que billing é **interno** até ADR de PSP.

## 3. Modelo de dados (rascunho)

```text
plans
  id UUID PK
  code VARCHAR UNIQUE
  max_storage_bytes BIGINT NULL
  max_monthly_ingestions INT NULL
  max_seats INT NULL

tenant_subscriptions
  tenant_id FK → tenants
  plan_id FK → plans
  starts_at, ends_at TIMESTAMPTZ NULL
```

## 4. Subtarefas

1. Migrations + seeds plano dev.
2. Serviço de quota + integração em upload e enqueue.
3. Respostas HTTP e mensagens amigáveis.
4. Testes: limite artificial dispara bloqueio.
5. Atualizar `docs/ARCHITECTURE.md` / SECURITY sobre quotas.

## 5. QA — critérios de aceite

- [ ] Ultrapassar quota bloqueia a ação esperada.
- [ ] Tenant sem subscrição tem comportamento definido (default plan ou erro).
- [ ] Sem bypass por manipulação de request.

## 6. Security

- [ ] Apenas admin altera planos de tenant.
- [ ] Auditoria de mudanças de plano.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Complexidade prematura | MVP com 1–2 planos e limites simples |

## 8. Dependências

TICKET-004; integração técnica com 006–008.

## 9. Próximo passo de produto

Marco D (SaaS fechável) após enforcement estável; Marco C (BI) em roadmap separado.
