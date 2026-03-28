# Planos por ticket (002–010)

Resumo executável; **planos detalhados** (modelo TICKET-001) em `docs/plans/TICKET-00X-*-detailed-plan.md`. Detalhes de segurança em `docs/SECURITY.md` e regras `.cursor/rules`.

**Execução:** o plano é único para toda a equipa; **vários tickets podem correr em paralelo** conforme gates e trilhos em [`EXECUCAO-MESTRE.md`](./EXECUCAO-MESTRE.md) §0.

---

## TICKET-002 — Recuperação de senha

**Objetivo:** Solicitar reset por email e redefinir com token de uso único e expiração.

**Plano:** Tabela `password_reset_tokens` (hash do token, `user_id`, `expires_at`, `used_at`); `POST /auth/forgot-password` (mensagem genérica); `POST /auth/reset-password`; serviço de email (adapter SMTP ou fila); auditoria de solicitação.

**Arquivos previstos:** `routers/auth.py` (expandir), `services/password_reset_service.py`, `repositories/`, migration, `packages/contracts` DTOs, testes de expiração e uso único.

**Riscos:** Token em URL logado; vazamento de existência de email — manter política de mensagem única.

**Saída:** Teste integração com email mock; critério do ticket atendido.

---

## TICKET-003 — MFA por email

**Objetivo:** Segundo fator com código por email após senha válida.

**Plano:** Estado de login `mfa_pending` + `mfa_challenges` (código hash, expiração); envio assíncrono opcional; `POST /auth/mfa/verify`; política por grupo (ex.: admin obrigatório) após TICKET-005.

**Arquivos previstos:** models, router, service, rate limit por IP+user.

**Riscos:** Código adivinhável — usar `secrets.token_hex`, tentativas limitadas.

**Saída:** Login feliz exige MFA quando flag/papel exige.

---

## TICKET-004 — Tenant foundation

**Objetivo:** `tenants`, vínculo `user_tenants`, contexto de tenant na request autenticada.

**Plano:** Migrations; dependency `get_current_tenant`; guards em repositórios; seed dev multi-tenant; testes de isolamento (tenant A não lê B).

**Arquivos previstos:** `models/tenant.py`, `middleware` ou dependency, `repositories/base.py` scoping.

**Riscos:** `tenant_id` vindo do cliente — **nunca** confiar; apenas do token/sessão server-side.

**Saída:** Testes de isolamento verdes.

---

## TICKET-005 — RBAC

**Objetivo:** Papéis (admin, analyst, consumer) e mapeamento permissão → endpoint.

**Plano:** Tabelas `roles`, `user_roles` (scoped por tenant); matriz em código ou tabela; decorator `requires_permission`; espelho mínimo no Angular (guards).

**Arquivos previstos:** `core/security.py`, `dependencies/rbac.py`, seeds.

**Riscos:** Divergência FE/BE — testes de API como fonte da verdade.

**Saída:** Usuário consumidor bloqueado em rota admin.

---

## TICKET-006 — Upload de arquivos

**Objetivo:** Upload tipos txt, csv, xls, xlsx, json com validação e storage.

**Plano:** Presigned ou multipart → disco/MinIO; limites por tipo/tamanho; metadados mínimos na resposta; auditoria.

**Arquivos previstos:** `routers/uploads.py`, `services/storage_service.py`, config mime/size.

**Riscos:** MIME spoofing — validação mágica bytes + quota.

**Saída:** Arquivo armazenado e registrado (metadata pode completar no 007).

---

## TICKET-007 — Metadata de ingestão

**Objetivo:** Tabela de uploads/jobs com status e vínculo tenant.

**Plano:** Estados `uploaded`, `validating`, `parsing`, `processed`, `failed`; API de detalhe; mensagem amigável + log técnico.

**Arquivos previstos:** `models/ingestion.py`, `services/ingestion_service.py`.

**Riscos:** Status inconsistente — transações e máquina de estados clara.

**Saída:** Todo upload tem registro persistido.

---

## TICKET-008 — Pipeline de parsing

**Objetivo:** Fila (Redis/Celery), worker consome e atualiza status.

**Plano:** Task por `ingestion_id`; parsers por extensão; reprocessamento; dead-letter/retry policy mínima.

**Arquivos previstos:** `apps/worker/tasks/parse.py`, `packages/shared` util formato.

**Riscos:** Falhas silenciosas — sempre `failed` + reason no metadata.

**Saída:** Teste worker com arquivo fixture pequeno.

---

## TICKET-009 — Catálogo de datasets

**Objetivo:** Listagem paginada só do tenant; tela Angular.

**Plano:** API `GET /datasets`; filtros; contrato estável em `packages/contracts`.

**Riscos:** Esquecer filtro tenant — testes obrigatórios.

**Saída:** Dois tenants isolados na listagem.

---

## TICKET-010 — Billing core

**Objetivo:** `plans`, `tenant_subscriptions`, quotas (storage, jobs, assentos).

**Plano:** CRUD admin planos; vínculo tenant; middleware de enforcement em upload/job.

**Riscos:** Billing sem gateway no MVP — documentar que é “interno” até ADR de pagamento.

**Saída:** Limite artificial dispara 402/403 com mensagem clara.

---

## Ordem de leitura para a squad

1. `EXECUCAO-MESTRE.md`  
2. `PLANOS-POR-TICKET-000-001.md` (000–001)  
3. `TICKET-001-auth-core-detailed-plan.md`  
4. Este arquivo, ticket atual  
5. Pós-MVP: `PLANOS-POR-TICKET-011-014.md`  
6. `docs/wireframes/` para UX
