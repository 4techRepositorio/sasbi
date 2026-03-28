# Plano detalhado — TICKET-002 Recuperação de senha

**Papéis:** Backend Core · Security Reviewer · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-002-password-recovery.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-002

## 1. Objetivo

Permitir que um utilizador solicite redefinição de senha por email e conclua o fluxo com token de uso único, expiração curta e mensagens que não revelem existência de conta.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| `POST /auth/forgot-password`, `POST /auth/reset-password` | MFA (TICKET-003) |
| Persistência de token hasheado + auditoria mínima | Magic link login sem senha |

### 2.2 Decisões

1. Tabela `password_reset_tokens`: `user_id`, `token_hash`, `expires_at`, `used_at` (nullable).
2. Resposta genérica em forgot-password (mesmo texto para email existente ou não).
3. Email via adapter SMTP ou fila (Celery) — configurável por env.
4. Um token ativo por utilizador ou invalidação em cadeia — documentar política.

## 3. Modelo de dados (rascunho)

```text
password_reset_tokens
  id UUID PK
  user_id FK → users
  token_hash VARCHAR NOT NULL
  expires_at TIMESTAMPTZ NOT NULL
  used_at TIMESTAMPTZ NULL
  created_at TIMESTAMPTZ
```

## 4. Subtarefas

1. Migration + repositório.
2. `PasswordResetService`: criar token, validar, marcar usado, invalidar anteriores.
3. Rotas com schemas Pydantic e erros HTTP consistentes.
4. Integração email (mock em testes).
5. Testes: token expirado, reuso, email inexistente (resposta idêntica).

## 5. QA — critérios de aceite

- [ ] Reset com token válido altera senha e invalida token.
- [ ] Token usado ou expirado retorna erro claro sem vazar dados.
- [ ] `docs/CHECKLISTS/backend-checklist.md` / security atualizados.

## 6. Security

- [ ] Token só em hash; TTL curto (ex.: 1h).
- [ ] Rate limit em forgot-password (IP + email).
- [ ] Logs sem token em claro.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Enumeration | Mensagem única; timing attacks — evitar diferenças grandes |

## 8. Dependências

TICKET-001 (users, auth base).

## 9. Próximo ticket

Paralelo possível com TICKET-003 e TICKET-004; recomenda-se TICKET-004 antes de fluxos multitenant completos.
