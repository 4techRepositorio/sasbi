# Checklist — Orquestração Multiagente (4Pro_BI)

Usar em entregas do agente **Multi-Agent Systems Architect**.  
Skill: [`.cursor/skills/multi-agent-systems-architect/SKILL.md`](../../.cursor/skills/multi-agent-systems-architect/SKILL.md).

**Run / objetivo:** _______________________  
**Âmbito:** [ ] chats Cursor  [ ] runtime produto  [ ] ambos  
**Data / responsável:** _______________________

## Papéis

- [ ] Supervisor definido (dono de gates/merges/DLQ)
- [ ] Planner definido
- [ ] Executor(es) / Workers com allowlists
- [ ] Reviewer definido
- [ ] Critic no gate de plano (obrigatório se contrato/auth/billing/tenant)
- [ ] Memory (onde vivem decisões e estado do run)
- [ ] Knowledge (fontes de verdade)
- [ ] Tools inventariadas (e timeouts por tool)
- [ ] Nenhum agente monolítico

## Contratos de orquestração

- [ ] Mapa dos agentes (grafo + paralelismo máximo seguro)
- [ ] Fluxo ponta a ponta documentado
- [ ] Envelope de mensagens (ids, correlation, tipos, aceite)
- [ ] Estados de run e de task (fechados)
- [ ] Eventos mínimos emitidos / registados
- [ ] Filas / partições por classe de Worker
- [ ] Retries com `max_attempts` e política por tipo de falha
- [ ] Timeouts por camada (task, review, critic, tool, run)
- [ ] Dead Letter Queue + dono de reprocessamento
- [ ] Observabilidade (logs, métricas, traces, dashboard mínimo)

## Avaliação

- [ ] Latência (caminho crítico + paralelismo)
- [ ] Custo (agentes × turns × tools)
- [ ] Tokens (resumos vs dumps)
- [ ] Context window (um Worker = um slice)
- [ ] Memória (efémero vs durável)
- [ ] Escalabilidade (novos Workers sem redesenhar Supervisor)

## Alinhamento 4Pro_BI

- [ ] Allowlists coerentes com `docs/plans/ORQUESTRACAO-CHATS-AGENTES.md`
- [ ] Gates / sync com `docs/plans/EXECUCAO-MESTRE.md` quando aplicável
- [ ] Multitenancy respeitado se runtime de produto
- [ ] Fronteira clara com `ai-workflow-designer` (quem vs como)

## Resultado

- [ ] **Pronto para despacho** / [ ] **Ajustar** (notas abaixo)

### Notas

_…
_
