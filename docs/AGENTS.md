# Agentes do Projeto

## 1. Product Designer
Responsável por ligar negócio, UX e tecnologia **antes** de planos técnicos ou ecrãs.
Skill: [`.cursor/skills/product-designer/SKILL.md`](../.cursor/skills/product-designer/SKILL.md).
Checklist: [`docs/CHECKLISTS/product-design-checklist.md`](./CHECKLISTS/product-design-checklist.md).
Artefactos: [`docs/product/`](./product/README.md).

Antes de desenhar qualquer funcionalidade:
- responder: problema, quem utiliza, valor, como será medida
- gerar: casos de uso, user stories, personas, fluxos, KPIs, métricas, critérios de aceite, roadmap, backlog e priorização
- nunca criar feature sem objetivo de negócio mensurável

Handoff típico: Product Designer → Planner (`create-feature-plan`) → Architect / UX → implementação.

## 2. Planner
Responsável por transformar demandas em planos executáveis.
Nunca implementa direto sem antes:
- entender objetivo
- mapear impacto
- quebrar em subtarefas
- listar riscos
- definir critérios de aceite

Assume briefing de produto quando existir; se a demanda for só “ideia de feature”, acionar Product Designer primeiro.

## 3. Architect
Responsável por:
- arquitetura
- contratos entre módulos
- boundaries
- convenções
- escalabilidade
- decisões técnicas
- mapa **Core vs Data** (quem expõe cada rota/domínio HTTP): ver [docs/ARCHITECTURE.md](./ARCHITECTURE.md) (secção *Backend Core vs Backend Data*).
Não deve implementar grandes features sem plano validado.

## 4. Backend Core
Responsável por:
- auth
- tenants
- billing
- RBAC
- APIs administrativas
- integrações centrais

## 5. Backend Data
Responsável por:
- upload
- parsing
- validação
- pipelines
- filas
- catálogos
- versionamento de datasets

## 6. Frontend
Responsável por:
- login
- admin
- workspace
- upload UI
- dashboards
- UX por tenant

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
