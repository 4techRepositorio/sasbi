# Diagrama de contexto do sistema

## O que faz

Mostra actores externos e blocos principais da plataforma 4Pro_BI.

```mermaid
flowchart TB
  subgraph actors [Actores]
    Admin[Administrador do tenant]
    Analyst[Analista]
    Viewer[Utilizador autenticado]
  end

  subgraph product [4Pro_BI]
    Web[Web App Angular]
    Desktop[Desktop Authoring planeado]
    API[API FastAPI]
    Worker[Worker Celery]
  end

  subgraph data [Dados e mensagens]
    PG[(PostgreSQL)]
    RD[(Redis)]
    OBJ[(Object storage MinIO)]
  end

  Admin --> Web
  Analyst --> Web
  Viewer --> Web
  Desktop -.->|futuro| API
  Web --> API
  API --> PG
  API --> OBJ
  API --> RD
  Worker --> RD
  Worker --> PG
  Worker --> OBJ
```

## Como funciona

Pedidos autenticados passam pela API; jobs pesados (parsing) vão para o Worker via Redis; ficheiros ficam em object storage / disco configurado; metadados e isolamento por `tenant_id` no PostgreSQL.

## Como instalar / configurar / testar / evoluir

Ver [INSTALLATION.md](../INSTALLATION.md), [DEPLOYMENT.md](../DEPLOYMENT.md) e [ARCHITECTURE.md](../ARCHITECTURE.md). Evolução Desktop/conectores: ADR-001 e tickets 015–017.
