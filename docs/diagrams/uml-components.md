# UML — diagrama de componentes

## O que faz

Mostra componentes deployáveis e pacotes partilhados.

```mermaid
flowchart TB
  subgraph apps [Aplicações]
    WEB["apps/web\nAngular SPA"]
    API["apps/api\nFastAPI"]
    WRK["apps/worker\nCelery"]
    DESK["apps/desktop\nplaneado"]
  end

  subgraph pkgs [Pacotes]
    CTR["packages/contracts\nDTOs Pydantic"]
    SHR["packages/shared"]
    UI["packages/ui\nopcional"]
    CONN["packages/connectors\nplaneado"]
  end

  subgraph infra [Infra]
    PG[(PostgreSQL)]
    RD[(Redis)]
    S3[(MinIO)]
  end

  WEB --> API
  WEB -.-> UI
  DESK -.-> API
  DESK -.-> CTR
  API --> CTR
  API --> SHR
  API --> PG
  API --> S3
  API --> RD
  WRK --> CTR
  WRK --> SHR
  WRK --> RD
  WRK --> PG
  WRK --> S3
  API -.-> CONN
  WRK -.-> CONN
```

## Como funciona

A API agrega routers Core (auth, tenant, billing/me) e Data (uploads, ingestions, datasets). Contratos são a fronteira estável entre apps. Worker partilha modelos/repositórios necessários ao parsing sem expor HTTP.

## Como instalar / configurar / testar / evoluir

Build: Dockerfiles em `apps/*/`. Deploy: [DEPLOYMENT.md](../DEPLOYMENT.md).  
Evolução de boundaries → ADR + actualização deste diagrama e de `ARCHITECTURE.md`.
