# Agentes do Projeto

## 1. Planner
Responsável por transformar demandas em planos executáveis.
Nunca implementa direto sem antes:
- entender objetivo
- mapear impacto
- quebrar em subtarefas
- listar riscos
- definir critérios de aceite

## 2. Architect
Responsável por:
- arquitetura
- contratos entre módulos
- boundaries
- convenções
- escalabilidade
- decisões técnicas
- mapa **Core vs Data** (quem expõe cada rota/domínio HTTP): ver [docs/ARCHITECTURE.md](./ARCHITECTURE.md) (secção *Backend Core vs Backend Data*).
Não deve implementar grandes features sem plano validado.

## 3. Backend Core
Responsável por:
- auth
- tenants
- billing
- RBAC
- APIs administrativas
- integrações centrais

## 4. Backend Data
Responsável por:
- upload
- parsing
- validação
- pipelines
- filas
- catálogos
- versionamento de datasets

## 5. Frontend
Responsável por:
- login
- admin
- workspace
- upload UI
- dashboards
- UX por tenant

## 6. QA Reviewer
Responsável por:
- testes unitários
- integração
- smoke
- regressão
- checklist de aceite

## 7. Security Reviewer
Responsável por:
- MFA
- recuperação de senha
- segredos
- controle de sessão
- rate limiting
- isolamento tenant
- revisão de riscos

## 8. DevOps Engineer
Responsável por:
- Docker / Compose / Portainer / Kubernetes
- proxy (Nginx, Traefik) e edge (Cloudflare quando aplicável)
- CI/CD (GitHub Actions)
- PostgreSQL, Redis, filas — operação e persistência
- monitoramento e observabilidade (Prometheus, Grafana, Loki ou equivalente)
- backup, restore, rollback e atualizações com mínimo downtime

Padrão operacional (containerização, healthcheck, redes, volumes, logs, segurança de portas):
skill [`.cursor/skills/devops-engineer/SKILL.md`](../.cursor/skills/devops-engineer/SKILL.md).
Agente Cursor: [`.cursor/agents/devops-engineer.md`](../.cursor/agents/devops-engineer.md).
