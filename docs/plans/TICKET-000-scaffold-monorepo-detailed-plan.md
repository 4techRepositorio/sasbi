# Plano detalhado — TICKET-000 Scaffold monorepo + Compose + health

**Papéis:** Architect · DevOps · Backend (API mínima) · Frontend (build)  
**Status:** referência (geralmente pré-001)  
**Ticket:** `tickets/TICKET-000-scaffold-monorepo.md`

## 1. Objetivo

Garantir que o repositório reflete a arquitetura alvo (`.cursor/rules/01-architecture.mdc`), com ambiente local reprodutível e verificação mínima de saúde dos serviços, antes de implementar auth e domínio.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| Estrutura `apps/*`, `packages/*`, `infra/` | Lógica TICKET-001+ |
| Compose + Postgres (+ Redis se já previsto) | Dados de produção |
| Healthcheck HTTP na API | Autenticação obrigatória no health |

### 2.2 Decisões

1. **Compose:** `infra/compose/docker-compose.yml` como fonte de verdade para dev local; stack Portainer em `infra/portainer/` para ambientes geridos.
2. **Segredos:** apenas `.env.example` no Git; nunca valores reais.
3. **Worker:** pasta `apps/worker` pode existir como stub até TICKET-008.

## 3. Subtarefas

1. Validar árvore do monorepo vs regras de arquitetura.
2. Subir stack local e documentar comandos em README raiz ou `infra/`.
3. Endpoint de health na API (200, eventualmente DB ping).
4. `npm run build` / `pytest` smoke conforme existente no repo.
5. Atualizar `docs/ARCHITECTURE.md` se a estrutura mudar.

## 4. QA — critérios de aceite

- [ ] Compose sobe sem erros em máquina limpa (após `cp .env.example`).
- [ ] Health da API acessível.
- [ ] Checklist infra preenchido quando aplicável.

## 5. Riscos

| Risco | Mitigação |
|-------|-----------|
| Drift entre Compose e Portainer | Documentar diferenças; preferir variáveis comuns |

## 6. Próximo ticket

`TICKET-001` — Auth core.
