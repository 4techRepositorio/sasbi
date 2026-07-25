---
name: senior-backend-engineer
description: Implementa backend pronto para produção (Repository, DI, config por env, resiliência, authz, auditoria, métricas e testes). Usar ao criar/alterar endpoints, services, workers, filas ou integrações.
---

# Skill: Senior Backend Engineer

Engenharia backend orientada a produção na plataforma SaaS multitenant 4Pro_BI.

## Stack relevante

- Node / TypeScript (quando o módulo for JS/TS)
- Python / FastAPI (stack principal do `apps/api` e `apps/worker`)
- PostgreSQL, Redis, RabbitMQ / Kafka (ou Celery + Redis conforme o módulo)
- Docker

Respeitar a arquitetura do repo: routers → services → repositories → schemas/DTOs; worker separado para processamento pesado; `tenant_id` em toda tabela/operação sensível.

## Proibições

1. Nunca gerar código duplicado — extrair utilitário/shared/service comum antes de copiar.
2. Nunca acessar o banco no controller/router quando houver regra de negócio.
3. Nunca confiar em `tenant_id` ou papéis vindos só do cliente sem validação de sessão.
4. Nunca embutir segredos no código — config exclusivamente por environment.
5. Nunca criar endpoint sem o checklist de segurança/observabilidade abaixo.

## Padrões obrigatórios

Sempre aplicar:

| Concern | Expectativa |
| --- | --- |
| Estrutura | DTO/schema → repository → service → router/handler |
| DI | Dependências injetadas (FastAPI `Depends`, container equivalente em Node) |
| Config | Variáveis de ambiente tipadas/validadas no boot |
| Validação | Entrada e saída via schema/DTO; rejeitar payload inválido cedo |
| Logs | Estruturados (JSON ou campos chave), com `tenant_id`, `request_id`/correlation, sem PII sensível |
| Erros | Tipados/mapeados para HTTP; mensagem amigável + detalhe técnico só em log |
| Retry | Em I/O transitório (DB, cache, fila, HTTP externo), com backoff e jitter |
| Timeout | Em toda chamada externa / fila / DB crítico |
| Circuit breaker | Em dependências externas instáveis ou caras |
| Testes | Unitário mínimo do service + isolamento de tenant quando aplicável |

## Checklist antes de criar qualquer endpoint

1. **Autenticação** — rota protegida (exceto endpoints públicos explícitos e documentados).
2. **Autorização** — RBAC/perfil; escopo por tenant; negar por default.
3. **Auditoria** — ações críticas registradas (quem, tenant, recurso, resultado).
4. **Métricas** — latência/erro/contador do fluxo (ou hook equivalente já usado no projeto).
5. **Contrato** — schema request/response em `packages/contracts` ou schemas locais alinhados; documentar impacto se mudar contrato.
6. **Tenant isolation** — queries e writes sempre filtrados pelo tenant da sessão.
7. **Idempotência** — quando o verbo/efeito for sensível a retry (upload, cobrança, publish).

## Fluxo de implementação

1. Confirmar plano da feature (não implementar feature grande sem plano).
2. Definir DTOs/schemas de request e response.
3. Implementar repository (apenas acesso a dados; sem regra de negócio).
4. Implementar service (regras, orquestração, resiliência, auditoria).
5. Expor router/handler fino (authz + validação + chamada ao service).
6. Configurar timeouts/retries/circuit breaker nas dependências externas.
7. Adicionar logs estruturados nos pontos de entrada, falha e conclusão.
8. Escrever testes mínimos (feliz, erro, tenant isolation, permissão).
9. Atualizar docs/checklist se impactar contrato, billing ou segurança.

## Resiliência (mínimo)

- Retry só em erros transitórios; não retry em 4xx de validação/auth.
- Timeout menor que o SLA do caller; cancelar trabalho quando estourar.
- Circuit breaker abre após limiar de falhas; fallback seguro ou erro claro.
- Filas: dead-letter / reprocessamento previsto; status de job observável.

## Alinhamento com o repo

- Backend Core: auth, tenants, billing, RBAC, admin — ver `docs/AGENTS.md`.
- Backend Data: upload, parsing, pipelines, filas, catálogo — ver `docs/AGENTS.md`.
- Endpoint FastAPI pontual: complementar com a skill `create-fastapi-endpoint`.
- Testes: complementar com a skill `create-tests`.
- Regras always-on: `.cursor/rules/02-backend.mdc`, `06-security.mdc`, `04-data.mdc`.

## Definition of done

Código pronto para produção quando:

- [ ] Camadas repository / service / DTO separadas
- [ ] DI e config por environment
- [ ] Authn + authz + auditoria + métricas no endpoint
- [ ] Logs estruturados e tratamento de erro
- [ ] Retry, timeout e circuit breaker onde há I/O externo
- [ ] Isolamento por tenant validado em teste
- [ ] Teste mínimo do fluxo feliz e de erro
- [ ] Sem duplicação desnecessária; contratos atualizados se mudaram
