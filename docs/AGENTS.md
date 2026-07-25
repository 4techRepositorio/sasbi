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

## 5. Frontend Architect
Responsável por:
- arquitectura UI (Feature-First, Atomic Design)
- login, admin, workspace, upload UI, dashboards
- UX por tenant e indicação clara do tenant activo
- performance (lazy loading, code splitting, SSR quando necessário)
- componentes reutilizáveis (props tipadas, docs, exemplo, testes)
- design system e fronteira Server/Client (stack alvo React/Next — ver [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) e [ADR-002](./adr/002-frontend-react-next.md))
- implementação actual em `apps/web` (Angular) até aceite da migração

Skills: `.cursor/skills/frontend-architect`, `create-angular-screen` (actual), `create-next-screen` (alvo).

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
