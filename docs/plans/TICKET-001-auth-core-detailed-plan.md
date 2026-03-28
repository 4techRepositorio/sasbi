# Plano detalhado — TICKET-001 Auth Core

**Papéis:** Planner · Architect · Backend Core · Security Reviewer · QA Reviewer  
**Status:** planejado (pré-implementação)  
**Ticket:** `tickets/TICKET-001-auth-core.md`

**Nota de alinhamento:** os planos em `docs_planos_antigos/` previam **Keycloak** (P0-04, P1-01, P1-02) e portal OIDC. Este repositório segue **FastAPI + auth em `apps/api`** (`.cursor/rules/02-backend.mdc`). Se no futuro a identidade migrar para Keycloak, trate como **ADR** e ajuste este plano; até lá, o escopo do TICKET-001 permanece login/API próprios. Ver também `docs/wireframes/REFERENCIAS-MATERIAIS-LEGADOS.md`.

## 1. Objetivo

Entregar autenticação inicial com email e senha: modelo de usuário seguro, login validado, emissão de credenciais de sessão (access + refresh), base para MFA e recuperação de senha em tickets subsequentes.

## 2. Validação arquitetural (Architect)

### 2.1 Escopo confirmado

| Incluído | Excluído (outros tickets) |
|----------|---------------------------|
| Tabela `users`, hash de senha | MFA (`TICKET-003`) |
| POST login, validação | Recursos de reset (`TICKET-002`) |
| JWT ou sessão opaca + refresh | `tenant_id` em todas as rotas de negócio (`TICKET-004`) |
| Rate limiting em login | RBAC detalhado (`TICKET-005`) |

### 2.2 Decisões propostas

1. **Credenciais:** access token JWT (curta duração) + refresh token opaco persistido (tabela `refresh_tokens` ou coluna hasheada em `users` + rotação), revogação possível.
2. **Senha:** Argon2id ou bcrypt (preferir Argon2id via `argon2-cffi` se disponível no stack).
3. **Camadas:** `routers/auth.py` → `services/auth_service.py` → `repositories/user_repository.py`; schemas em `packages/contracts` ou `apps/api/schemas` alinhado ao monorepo.
4. **Estado inicial do usuário:** campos mínimos: `id`, `email` (único global), `password_hash`, `is_active`, `created_at`, `updated_at`. **Sem `tenant_id` na tabela `users` até TICKET-004** — vínculo user↔tenant virá em associação; login retorna apenas identidade até o tenant ser injetado no contexto.
5. **Segurança:** rate limit por IP + email no login; não revelar se email existe (mensagem genérica em falha); audit log mínimo para login sucesso/falha (pode ser log estruturado na Fase 1, tabela `audit_events` na Fase 2 se ainda não existir).

### 2.3 Contratos API (rascunho — impacto a documentar antes de publicar v1)

- `POST /api/v1/auth/login` — body: `email`, `password` → `access_token`, `refresh_token`, `token_type`, `expires_in`.
- `POST /api/v1/auth/refresh` — body: `refresh_token` → novo par.
- `POST /api/v1/auth/logout` — invalida refresh (opcional no escopo mínimo; recomendado).

**Impacto em contratos futuros:** `TICKET-002` e `TICKET-003` acrescentam endpoints e estados (`mfa_pending`); clientes devem aceitar extensão do payload de login sem breaking change (versionamento ou campos opcionais).

## 3. Modelo de dados

```text
users
  id UUID PK
  email VARCHAR UNIQUE NOT NULL
  password_hash VARCHAR NOT NULL
  is_active BOOLEAN DEFAULT true
  created_at, updated_at TIMESTAMPTZ

refresh_tokens (se rotação)
  id UUID PK
  user_id FK → users
  token_hash VARCHAR NOT NULL  -- nunca armazenar token em claro
  expires_at TIMESTAMPTZ
  revoked_at TIMESTAMPTZ NULL
  created_at TIMESTAMPTZ
```

Índices: `users(email)`, `refresh_tokens(user_id)`, `refresh_tokens(expires_at)` para limpeza.

## 4. Subtarefas de implementação (Backend Core)

1. Scaffold `apps/api`: FastAPI, settings via variáveis de ambiente, logging estruturado.
2. SQLAlchemy + Alembic: migration inicial `users` (+ `refresh_tokens` se aplicável).
3. `UserRepository`: create (seed/dev), get_by_email.
4. `AuthService`: verificar senha, emitir tokens, refresh, logout.
5. Router `/auth` com validação Pydantic e tratamento de erros HTTP consistente.
6. Middleware futuro: placeholder para `tenant_id` (no-op até TICKET-004).
7. **Testes mínimos:** login sucesso com senha correta; falha senha incorreta; falha usuário inexistente (mesma mensagem); refresh válido/inválido; rate limit (se testável com dependency override).

## 5. QA — critérios de aceite mensuráveis

- [ ] Usuário ativo com senha válida recebe 200 e tokens.
- [ ] Senha errada ou email inexistente retorna 401 com mensagem genérica.
- [ ] Tokens assinados com segredo vindo de env; clock skew documentado.
- [ ] Refresh com token revogado/expirado retorna 401.
- [ ] Checklist: `docs/CHECKLISTS/backend-checklist.md` atualizado após merge.

## 6. Security Reviewer — checklist

- [ ] Segredos apenas em env / secret manager.
- [ ] Hash forte; nenhum log de senha ou token em claro.
- [ ] Rate limiting ativo no login.
- [ ] CORS e headers segurança revisados antes de expor à web.

## 7. Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| Credenciais fracas | Política mínima de senha na Fase 2; por ora apenas hash seguro |
| Enumeration de emails | Resposta genérica no login |
| Refresh hijacking | HttpOnly cookie (decisão frontend) ou armazenamento seguro no cliente; rotação de refresh |
| Scope creep MFA/recovery | Rejeitar PRs que misturem TICKET-002/003 |

## 8. Dependências de infraestrutura

- PostgreSQL e Redis (Redis pode ser opcional para rate limit na v0; preferir Redis conforme regras).
- Docker Compose em `infra/` para desenvolvimento local.

## 9. Ordem de execução sugerida (este ticket)

1. Infra local (compose + env sample).  
2. App API + healthcheck.  
3. Migrations + seed dev user.  
4. Auth service + rotas.  
5. Testes + documentação de env em `apps/api/README.md`.

## 10. Próximo ticket

Após aceite: `TICKET-004-tenant-foundation.md` em paralelo conceitual com `TICKET-002` — recomenda-se **Tenant Foundation logo após Auth Core** para que todas as rotas subsequentes já filtrem por tenant; **Password Recovery** pode ser paralelo ao tenant se equipe dividir, mas login “completo” para produto multitenant exige 004 antes de upload/RBAC.
