# AI Workflow Designer Checklist

Usar antes de autorizar Execução de qualquer tarefa complexa modelada como pipeline.
Skill: [`.cursor/skills/ai-workflow-designer/SKILL.md`](../../.cursor/skills/ai-workflow-designer/SKILL.md).

## Estágios canónicos

- [ ] Entrada — envelope tipado (`tenant_id`, `correlation_id`, `idempotency_key`, `deadline`)
- [ ] Validação — schema, authz, quotas; rejeição sem retry cego
- [ ] Planejamento — steps, DAG, critérios de aceite
- [ ] Execução — timeouts por step; resultados idempotentes
- [ ] Verificação — verdict pass/fail com evidências
- [ ] Correção — `max_attempts`, backoff, fallback ou compensate bounded
- [ ] Entrega — status final (`delivered` | `failed` | `cancelled`) + métricas

## Avaliação (8 dimensões)

- [ ] Dependências — grafo acíclico; bloqueantes vs independentes
- [ ] Paralelismo — steps paralelos e sync points declarados
- [ ] Cache — chaves com tenant; TTL e invalidação
- [ ] Memória — efémero vs persistente; segredos só em env
- [ ] Persistência — Postgres / object storage / Redis conforme o dado
- [ ] Retries — transitório vs permanente; `max_attempts` explícito
- [ ] Fallback — plano B documentado ou fail-fast claro
- [ ] Métricas — latência por estágio, fail/retry, profundidade de fila

## Anti loop infinito

- [ ] Nenhum caminho reentra sem incrementar `attempt`
- [ ] Deadline absoluto do run definido
- [ ] Saída `failed` / DLQ quando attempts esgotam
- [ ] Validação/authz/tenant leak **sem** auto-retry

## Multitenancy e segurança

- [ ] `tenant_id` na entrada, mensagens e persistência
- [ ] Sem cache/fila cross-tenant
- [ ] Logs com mensagem técnica + amigável; sem segredos/PII em claro
