# Plano detalhado — TICKET-014 CI e quality gates

**Papéis:** DevOps · QA · Toda a squad  
**Status:** planejado  
**Ticket:** `tickets/TICKET-014-ci-quality-gates.md`  
**Alinhamento:** `EXECUCAO-MESTRE.md` §4 (workflow GitHub/GitLab); Definition of Done global.

## 1. Objetivo

Garantir que cada PR valida automaticamente **lint**, **testes backend** (`pytest apps/api`) e **build frontend** (`ng build`), com possível extensão a worker e contratos — antes de merge para `main`.

## 2. Escopo

| Incluído | Excluído |
|----------|----------|
| Workflow CI no fornecedor Git usado pelo repositório remoto | Deploy automático produção (CD separado) |
| Job: instalar deps, rodar pytest com DB de teste (service container ou sqlite se aplicável) | Testes e2e Playwright completos (podem ser estágio 2) |
| Job: `npm ci` + `npm run build` em `apps/web` | Análise SAST enterprise paga |

## 3. Pré-requisitos

- Repositório versionado em GitHub ou GitLab com runners disponíveis.
- `pytest` passando localmente; variáveis de teste documentadas em `apps/api/README.md` ou `.env.test.example`.

## 4. Subtarefas

1. Escolher ficheiro: `.github/workflows/ci.yml` ou `.gitlab-ci.yml`.
2. Definir imagem base (Python + Node ou jobs paralelos).
3. Serviço PostgreSQL efémero para testes de integração (ou marcar testes que precisam de DB com `pytest -m integration`).
4. Cache de pip/npm para duração aceitável.
5. Badge opcional no README raiz; branch protection exigindo CI verde.

## 5. QA — critérios de aceite

- [ ] PR de exemplo falha se teste propositalmente quebrado.
- [ ] Build Angular falha com erro de TypeScript.
- [ ] Documentação em `docs/plans/` ou README como reproduzir CI localmente.

## 6. Riscos

| Risco | Mitigação |
|-------|-----------|
| Flaky tests | Isolamento de DB; seeds determinísticos |
| CI lento | Jobs paralelos API vs web |

## 7. Dependências

Nenhuma funcional; recomendado após TICKET-001 para ter suíte mínima estável.

## 8. Próximo passo

Estágio 2: cobertura mínima obrigatória, `ruff`/`eslint` strict, smoke e2e.
