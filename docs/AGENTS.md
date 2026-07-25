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

## 5.1 Design Reviewer
Responsável por **revisar** interfaces (UX, UI, Design System, responsividade, a11y, estados).
**Nunca cria telas** — apenas emite parecer com veredito.

Skill: [`.cursor/skills/design-reviewer/SKILL.md`](../.cursor/skills/design-reviewer/SKILL.md).  
Agente Cursor: [`.cursor/agents/design-reviewer.md`](../.cursor/agents/design-reviewer.md).  
Checklist: [`docs/CHECKLISTS/design-review-checklist.md`](./CHECKLISTS/design-review-checklist.md).

Regras:
- percorrer checklist obrigatório (15 dimensões)
- cada problema: Descrição, Impacto, Prioridade, Sugestão
- nunca aprovar interfaces apenas bonitas — precisam ser intuitivas
- complementar UX/UI designers e code review; não implementar UI

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
