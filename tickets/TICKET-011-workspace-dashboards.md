# Workspace e dashboards (Marco C)

**ID:** TICKET-011  
**Plano detalhado:** [`docs/plans/TICKET-011-workspace-dashboards-detailed-plan.md`](../docs/plans/TICKET-011-workspace-dashboards-detailed-plan.md)

## Objetivo

Entregar BI utilizável multitenant: dashboards ligados ao catálogo de datasets, com ADR embed vs canvas.

## Escopo

Workspace, widgets iniciais, export snapshot, isolamento tenant/RBAC.

## Fora de escopo

Whitelabel completo; OLAP avançado (fases posteriores).

## Impacto técnico

Backend (modelos dashboard), Angular, segurança, ADR.

## Subtarefas

Ver plano detalhado.

## Critérios de aceite

Isolamento tenant; placeholders de erro; RBAC respeitado.

## Riscos

Subestimar integração embed multitenant.

## Dependências

TICKET-009; recomendado 010.
