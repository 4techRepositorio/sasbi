# Plano detalhado — TICKET-005 RBAC

**Papéis:** Architect · Backend Core · Frontend (guards) · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-005-rbac.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-005

## 1. Objetivo

Papéis por tenant (ex.: `admin`, `analyst`, `consumer`) com mapeamento explícito permissão → endpoint no backend e espelho mínimo no Angular (guards), evitando divergência não testada.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| Papéis scoped por tenant | ABAC granular / custom roles UI |
| Decorator/dependency `requires_role` | Feature flags comerciais (010) |

### 2.2 Decisões

1. Fonte da verdade: API; frontend apenas UX (ocultar rotas).
2. Matriz em código versionado (`core/security.py` ou módulo dedicado) ou tabela `roles` + `user_roles` — documentar escolha.
3. Upload e admin apenas `admin`/`analyst` conforme wireframes.

## 3. Modelo de dados (rascunho)

```text
roles
  id UUID PK
  code VARCHAR UNIQUE  -- admin, analyst, consumer

user_tenant_roles
  user_id, tenant_id, role_id
  UNIQUE (user_id, tenant_id)
```

(Alternativa: coluna `role` em `user_tenants` no MVP — ADR se simplificar.)

## 4. Subtarefas

1. Migration + seed roles.
2. Dependency RBAC reutilizável nas rotas FastAPI.
3. Incluir `role` no contexto `/me/context`.
4. Angular: `roleGuard` nas rotas sensíveis (upload, futuro admin).
5. Testes: consumer bloqueado em `POST /uploads`; admin permitido.

## 5. QA — critérios de aceite

- [ ] Matriz documentada (tabela README ou SECURITY).
- [ ] Pelo menos um teste por papel crítico.
- [ ] Wireframes admin/upload alinhados.

## 6. Security

- [ ] Nunca confiar só no hide de botão no UI.
- [ ] Auditoria opcional para ações admin.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| FE/BE dessincronizados | Testes de API como contrato |

## 8. Dependências

TICKET-004.

## 9. Próximo ticket

TICKET-006 (upload com enforcement de papel).
