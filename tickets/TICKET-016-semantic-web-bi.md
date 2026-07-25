# Camada semântica e BI Web

**ID:** TICKET-016  
**Plano detalhado:** [`docs/plans/TICKET-016-semantic-web-bi-detailed-plan.md`](../docs/plans/TICKET-016-semantic-web-bi-detailed-plan.md)  
**ADR:** [`docs/adr/001-bi-platform-connectors-desktop-web.md`](../docs/adr/001-bi-platform-connectors-desktop-web.md)  
**Plano mestre:** [`docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](../docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md)

## Objetivo

Expor uma camada semântica mínima e API de consulta agregada por tenant, e ligá-la ao workspace Web (TICKET-011) para dashboards nativos 4Pro_BI — consumo, biblioteca e governação leve.

## Escopo

- Modelos semânticos (dataset → dimensões/medidas)
- API de query agregada com RLS/tenant + RBAC
- UI Web: Fontes de dados (consumo do 015) + widgets via query API
- Export snapshot alinhado a TICKET-011
- Documentação de impacto em contratos

## Fora de escopo

- Desktop authoring completo (017)
- SQL Lab ad-hoc para utilizador final
- OLAP / drill infinito
- Whitelabel total

## Impacto técnico

Backend Data; contracts `semantic`; Angular workspace; segurança RLS; possível acelerador OSS só via BFF.

## Subtarefas

Ver plano detalhado.

## Critérios de aceite

- Query nunca cruza tenant.
- Widget no Web consome só datasets autorizados.
- Estados loading/erro/vazio/sucesso nas telas novas.
- Experiência unificada (sem marcas externas).

## Riscos

Performance em datasets grandes; scope do motor embed.

## Dependências

TICKET-009, 011 (coordenado), 015 (fontes); 005 RBAC; 010 quotas de query/export recomendado.
