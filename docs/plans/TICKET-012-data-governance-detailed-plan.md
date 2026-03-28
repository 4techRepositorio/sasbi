# Plano detalhado — TICKET-012 Governança de dados / camadas (Marco B)

**Papéis:** Architect · Data · Backend · DevOps  
**Status:** planejado (evolução pós MVP ingestão)  
**Ticket:** `tickets/TICKET-012-data-governance.md`  
**Alinhamento:** Marco **B** em `EXECUCAO-MESTRE.md`; planos antigos P3 (silver/gold).

## 1. Objetivo

Evoluir de “ficheiro processado” para **dados governados**: camadas lógicas (bronze / silver / gold ou equivalente na API), rastreabilidade e políticas de retenção documentadas — sem obrigar stack OSS completa até ADR.

## 2. Validação arquitetural — ADR

Decidir explicitamente:

1. **Onde** vive cada camada: mesma BD PostgreSQL (schemas), warehouse externo, ou armazenamento de objetos + formatos colunares.
2. Se ferramenta de **modelação SQL versionada** (ou apenas pipelines no worker) executa transformações.
3. Como o **catálogo** (TICKET-009) expõe a camada ao utilizador (badge, filtro).

## 3. Escopo sugerido

| Incluído | Excluído |
|----------|----------|
| Convenção de naming + metadados de camada na ingestão/transformação | Data catalog enterprise (DataHub) no MVP |
| Job ou passo de “promoção” silver/gold com logs | ML features store |
| Retenção por tipo de dado documentada em `docs/` | Apagado automático legal-grade sem revisão jurídica |

## 4. Subtarefas

1. ADR com diagrama (Mermaid) do fluxo atual → alvo.
2. Migrations para colunas/tabelas de lineage mínimo (`source_ingestion_id`, `layer`, `transform_version`).
3. Worker ou task secundária para materializar silver/gold conforme ADR.
4. Atualizar API de datasets para refletir camada (filtro opcional).
5. Testes: reprodutibilidade de transformação em fixture.

## 5. QA — critérios de aceite

- [ ] Nenhum dado cruza tenant em promoção de camada.
- [ ] Falha de transformação gera estado/ log rastreável.
- [ ] `docs/ARCHITECTURE.md` descreve o modelo de camadas.

## 6. Riscos

| Risco | Mitigação |
|-------|-----------|
| Complexidade operacional (modelação + orquestrador) | Fase 1: apenas metadados + uma transformação canónica |
| Custo de storage | Integração com quotas TICKET-010 |

## 7. Dependências

TICKET-008 (pipeline); TICKET-009 (catálogo); recomendado TICKET-010.

## 8. Próximo ticket

TICKET-011 pode consumir apenas `gold` ou equivalente — alinhar contrato na API.
