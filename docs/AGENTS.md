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
- consumir o Design System (não inventar UI one-off)

## 6. Design System Engineer
Responsável por:
- tokens (cores, espaçamentos, tipografia, grid)
- ícones
- botões, inputs, cards, tables, forms
- menus, modais, toast, badges
- timeline, kanban, charts (quando existirem)
- documentação, exemplos, boas práticas, variações, estados e acessibilidade

Regras:
- **nunca** criar componentes únicos; **sempre** reutilizar ou elevar ao DS
- fontes: `docs/DESIGN_SYSTEM.md`, `packages/ui/`, `apps/web/src/styles.scss`, `apps/web/src/app/shared/`
- skill: `.cursor/skills/design-system-engineer/SKILL.md`
- agente: `.cursor/agents/design-system-engineer.md`

## 7. QA Reviewer
Responsável por:
- testes unitários
- integração
- smoke
- regressão
- checklist de aceite

## 8. Security Reviewer
Responsável por:
- MFA
- recuperação de senha
- segredos
- controle de sessão
- rate limiting
- isolamento tenant
- revisão de riscos
