# Observabilidade e enterprise (Marco E)

**ID:** TICKET-013  
**Plano detalhado:** [`docs/plans/TICKET-013-observability-enterprise-detailed-plan.md`](../docs/plans/TICKET-013-observability-enterprise-detailed-plan.md)

## Objetivo

Correlation ID end-to-end, auditoria persistida, métricas/logs preparados para produção.

## Escopo

Middleware request ID, `audit_events`, métricas básicas, documentação SECURITY.

## Fora de escopo

Certificação formal SOC2/ISO neste ticket.

## Impacto técnico

API, worker, infra, compliance operacional.

## Subtarefas

Ver plano detalhado.

## Critérios de aceite

Fluxo rastreável por ID; eventos críticos auditados; testes mínimos.

## Riscos

Volume e custo de armazenamento de logs/auditoria.

## Dependências

Core da API e worker estáveis.
