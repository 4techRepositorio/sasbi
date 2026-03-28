# Governança de dados / camadas (Marco B)

**ID:** TICKET-012  
**Plano detalhado:** [`docs/plans/TICKET-012-data-governance-detailed-plan.md`](../docs/plans/TICKET-012-data-governance-detailed-plan.md)

## Objetivo

Camadas bronze/silver/gold (ou equivalente), lineage mínimo e políticas de retenção documentadas.

## Escopo

ADR de armazenamento; metadados de camada; promoção controlada.

## Fora de escopo

Data catalog enterprise completo.

## Impacto técnico

Worker, BD, possivelmente dbt ou SQL versionado.

## Subtarefas

Ver plano detalhado.

## Critérios de aceite

Sem cruzamento de tenant; falhas rastreáveis; ARCHITECTURE atualizado.

## Riscos

Complexidade operacional prematura.

## Dependências

TICKET-008, 009.
