# Plano detalhado — TICKET-003 MFA por email

**Papéis:** Backend Core · Security Reviewer · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-003-mfa-email.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-003

## 1. Objetivo

Segundo fator por código enviado por email após autenticação de senha válida, com expiração, limite de tentativas e integração com o fluxo de login existente.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| Estado `mfa_pending` no login quando aplicável | TOTP app / WebAuthn |
| `POST /auth/mfa/verify` | Política “obrigatório para admin” fina até TICKET-005 |

### 2.2 Decisões

1. Tabela `mfa_challenges`: `user_id`, `code_hash`, `expires_at`, `attempts` ou contagem externa.
2. Código com `secrets` criptograficamente seguro; hash no armazenamento.
3. Resposta de login pode incluir `mfa_required: true` + `challenge_id` opaco (sem código).
4. Rate limit por IP + utilizador no verify.

## 3. Modelo de dados (rascunho)

```text
mfa_challenges
  id UUID PK
  user_id FK → users
  code_hash VARCHAR NOT NULL
  expires_at TIMESTAMPTZ NOT NULL
  consumed_at TIMESTAMPTZ NULL
  created_at TIMESTAMPTZ
```

## 4. Subtarefas

1. Migration + serviço MFA.
2. Ajustar `AuthService`/login para ramo MFA.
3. Router verify + invalidação após sucesso.
4. Envio de email (reutilizar canal TICKET-002 quando possível).
5. Testes: código correto/incorreto, expirado, brute-force limitado.

## 5. QA — critérios de aceite

- [ ] Login com MFA ativo não emite access token até verify bem-sucedido.
- [ ] Código errado N vezes bloqueia o challenge.
- [ ] Contrato documentado para o Angular (campos opcionais no login).

## 6. Security

- [ ] Código não logado; hash forte.
- [ ] TTL curto (ex.: 10–15 min).

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Email atrasado | UX clara; opcional reenvio com rate limit |

## 8. Dependências

TICKET-001; email/SMTP alinhado a TICKET-002.

## 9. Próximo ticket

TICKET-005 para políticas por papel (admin obrigatório MFA).
