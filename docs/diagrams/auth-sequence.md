# Fluxo de autenticação (sequência)

## O que faz

Documenta login, MFA opcional, refresh e recuperação de senha.

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as API /auth
    participant S as AuthService
    participant DB as PostgreSQL
    participant M as Email ou logs

    C->>A: POST /auth/login
    A->>S: verificar credenciais
    S->>DB: user + membership
    alt MFA activo
        S->>M: OTP 6 dígitos
        A-->>C: mfa_required + mfa_token
        C->>A: POST /auth/mfa/verify
        A->>S: validar OTP
        A-->>C: access + refresh
    else sem MFA
        A-->>C: access + refresh + tenant_id role
    end

    C->>A: POST /auth/refresh
    A->>S: rotacionar refresh
    A-->>C: novos tokens

    C->>A: POST /auth/forgot-password
    A->>S: token reset 1h
    S->>M: link ou token
    C->>A: POST /auth/reset-password
    A->>S: nova senha + revogar refresh
```

Pedido autenticado subsequente:

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Router
    participant P as get_current_principal
    participant Svc as Service
    participant Repo as Repository

    C->>R: Bearer access_token
    R->>P: decode JWT
    P-->>R: Principal user_id tenant_id role
    R->>Svc: operação com tenant do Principal
    Svc->>Repo: queries filtradas por tenant_id
```

## Como funciona

O `tenant_id` efectivo vem do JWT/membership validada — nunca só do body do cliente. Rate limits em login/refresh/forgot (slowapi).

## Como instalar / configurar

Variáveis `JWT_*`, `LOGIN_RATE_LIMIT`, `REFRESH_RATE_LIMIT`, `SMTP_*` — ver `.env.example` e [INSTALLATION.md](../INSTALLATION.md).

## Como testar

- `pytest` em `apps/api/tests` (auth + tenant).
- Exemplos: [`docs/examples/01-auth.sh`](../examples/01-auth.sh).

## Como evoluir

Novos factores MFA ou IdP federado → ADR + contratos `fourpro_contracts.auth` + regenerar OpenAPI.
