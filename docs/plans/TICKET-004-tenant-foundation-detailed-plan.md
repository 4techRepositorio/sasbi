# Plano detalhado — TICKET-004 Tenant foundation

**Papéis:** Architect · Backend Core · Security Reviewer · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-004-tenant-foundation.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-004

## 1. Objetivo

Introduzir `tenants`, vínculo `user_tenants` (ou equivalente), e contexto de tenant na request autenticada derivado **apenas** do token/sessão validada — nunca do body/query não confiável.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| Migrations tenant + associação user↔tenant | Matriz de permissões fina (TICKET-005) |
| Dependency `get_current_tenant` / contexto request | Billing (TICKET-010) |

### 2.2 Decisões

1. JWT (ou sessão) inclui `tenant_id` escolhido após login ou tenant default por utilizador.
2. Repositórios de dados de cliente **sempre** filtram por `tenant_id` do contexto.
3. Seed dev: 2+ tenants e utilizadores cruzados para testes de isolamento.

## 3. Modelo de dados (rascunho)

```text
tenants
  id UUID PK
  slug VARCHAR UNIQUE
  name VARCHAR
  created_at TIMESTAMPTZ

user_tenants
  user_id FK → users
  tenant_id FK → tenants
  PK (user_id, tenant_id)
  role VARCHAR  -- ou FK roles após 005; documentar evolução
```

## 4. Subtarefas

1. Migrations + models.
2. Resolver tenant no middleware/dependency após validar JWT.
3. Aplicar filtro em repositórios existentes (ingestões, datasets quando existirem).
4. Endpoint `GET /me/context` (ou equivalente) para o frontend.
5. Testes: tenant A não lê/escreve dados de tenant B.

## 5. QA — critérios de aceite

- [ ] Todas as rotas de negócio após este ticket exigem contexto de tenant válido.
- [ ] Testes de isolamento automatizados verdes.
- [ ] `docs/ARCHITECTURE.md` atualizado sobre multitenancy.

## 6. Security

- [ ] Rejeitar `tenant_id` vindo do cliente sem validação de membership.
- [ ] Audit log para troca de tenant se aplicável.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Esquecer filtro numa query nova | Code review + padrão base repository |

## 8. Dependências

TICKET-001 (identidade).

## 9. Próximo ticket

TICKET-005 (RBAC) e depois pipeline de dados (006+).
