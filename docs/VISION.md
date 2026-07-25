# Visão do Produto

Plataforma SaaS multitenant de dados e analytics para empresas **ingerirem** dados
(ficheiros e conectores), **processarem** datasets por tenant, **modelarem**
métricas, e **autorarem / consumirem** dashboards — no **Web** e no **Desktop** —
com segurança, cobrança por pacote e experiência 100% nativa **4Pro_BI**.

Referências internas de mercado (não aparecem na UX): ecossistema de conectores
tipo “Get Data” e dualidade Desktop (autoração) + Web (consumo/governação).
Ver [`docs/adr/001-bi-platform-connectors-desktop-web.md`](./adr/001-bi-platform-connectors-desktop-web.md).

## Objetivos iniciais (esteira base — entregue / em consolidação)
- upload de txt, csv, xls, xlsx, json
- login com MFA
- recuperação de senha
- grupos de acesso
- tenant isolation
- planos e billing
- catálogo de datasets
- área administrativa
- workspace por cliente (KPI shell → dashboards em TICKET-011)

## Objetivos de plataforma BI (programa seguinte)
- framework de **conectores** / plugins de fontes (TICKET-015)
- camada **semântica** + BI Web (TICKET-016, com TICKET-011)
- cliente **Desktop** de autoração e publicação (TICKET-017)
- governação de camadas de dados (TICKET-012)

## Não objetivos do programa inicial de BI
- paridade total com produtos comerciais de BI
- marketplace público de dashboards ou de plugins
- OLAP / MDX completo ou SQL ad-hoc para o utilizador final
- mobile nativo
