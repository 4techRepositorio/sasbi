# UML — classes de domínio (Core / Data)

## O que faz

Vista simplificada das entidades persistidas relevantes ao multitenancy, auth e ingestão.

```mermaid
classDiagram
    class Tenant {
        +UUID id
        +str slug
        +str name
    }
    class User {
        +UUID id
        +str email
        +str password_hash
        +bool mfa_enabled
    }
    class TenantMembership {
        +UUID user_id
        +UUID tenant_id
        +str role
        +int max_storage_mb
        +UUID quota_group_id
    }
    class TenantQuotaGroup {
        +UUID id
        +UUID tenant_id
        +str name
        +int max_storage_mb
    }
    class Plan {
        +str code
        +int max_uploads_per_month
        +int max_storage_mb
    }
    class TenantSubscription {
        +UUID tenant_id
        +str plan_code
    }
    class FileIngestion {
        +UUID id
        +UUID tenant_id
        +str status
        +int size_bytes
        +UUID uploaded_by_user_id
        +str friendly_error
    }
    class AuditLog {
        +UUID id
        +UUID tenant_id
        +str action
        +datetime created_at
    }

    Tenant "1" --> "*" TenantMembership
    User "1" --> "*" TenantMembership
    Tenant "1" --> "*" TenantQuotaGroup
    TenantQuotaGroup "1" --> "*" TenantMembership : opcional
    Tenant "1" --> "1" TenantSubscription
    Plan "1" --> "*" TenantSubscription
    Tenant "1" --> "*" FileIngestion
    User "1" --> "*" FileIngestion : uploaded_by
    Tenant "1" --> "*" AuditLog
```

## Como funciona

Toda entidade de dados de cliente leva `tenant_id` (excepto tabelas só de plataforma). Papel inicial em `TenantMembership.role`; quotas em plano + membership + grupo.

## Como instalar / configurar

Schema via Alembic (`apps/api/alembic/`). Prefixo `core__` / `data__` nas revisões.

## Como testar

Testes de isolamento multi-tenant na API; seed `fourpro_api.dev_seed`.

## Como evoluir

Novas tabelas tenant-scoped → `tenant_id` + índices + testes de isolamento + nota em `ARCHITECTURE.md` / ADR se mudar o modelo.
