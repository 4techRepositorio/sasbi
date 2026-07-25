# ADR-002 — Modular monolith, Clean Architecture e limites assíncronos

**Estado:** aceite  
**Data:** 2026-07-25  
**Decisores:** Architect · Backend Core · Backend Data · Platform  
**Relacionados:** [BLUEPRINT](../architecture/BLUEPRINT.md) · [ADR-000](./000-contract-slices.md) · [ADR-001](./001-bi-platform-connectors-desktop-web.md)

## Contexto

O monorepo 4Pro_BI cresce em domínios (identity, tenancy, billing, ingestion, catálogo e, em breve, conectores/semântica/desktop). Sem decisão explícita de estilo, o risco é:

- acoplamento router ↔ ORM;
- microserviços prematuros;
- filas sem contrato;
- violações de tenant isolation.

É preciso fixar **como** o sistema escala em complexidade sem partir o deploy cedo demais.

## Decisão

1. **Modular monolith** para `apps/api` (um processo FastAPI, um PostgreSQL de aplicativo).  
2. **Clean Architecture pragmática:** adapters (`routers`, `repositories`, storage, mail) → application services → políticas/domínio; sem over-engineering de frameworks DDD.  
3. **Worker separado** (`apps/worker`) para CPU/IO pesado; comunicação via **Celery + Redis** com nomes de task estáveis (`fourpro.*`) e payload mínimo tipável.  
4. **Contratos partilhados** só em `packages/contracts`; shared técnico em `packages/shared`; SPI de conectores em `packages/connectors` (programa BI).  
5. **Partição futura por pastas de contexto** dentro da API (não por rede) quando a coesão o exigir — ver blueprint §5.  
6. **Event bus / outbox** diferido até existirem múltiplos consumidores reais do mesmo facto de domínio.

## Alternativas consideradas

| Alternativa | Motivo de rejeição / diferimento |
|-------------|----------------------------------|
| Microserviços por bounded context | Custo ops, distributed transactions e latência injustificados no estágio actual |
| Só monólito anémico (SQL nos routers) | Impede testes, viola SOLID e misturação Core/Data |
| Kafka / NATS desde já | Complexidade; Celery cobre jobs de ingestão/sync |
| CQRS completo | Prematuro; catálogo como vista de `processed` basta até Semantic (016) |

## Consequências

### Positivas

- Entrega rápida com boundaries auditáveis (checklist de arquitectura).
- Ownership Core vs Data continua válido ([ARCHITECTURE.md](../ARCHITECTURE.md)).
- Caminho claro para extrair serviços depois (contratos e eventos já nomeados).

### Negativas / custos

- Disciplina de PR necessária para não criar dependências cruzadas.
- Celery directo sem outbox pode perder eventos se o processo cair entre commit e enqueue — mitigação: reprocess endpoint + idempotência do worker; outbox quando o risco materializar.

### Obrigações

- Features grandes passam pelo [architecture-checklist](../CHECKLISTS/architecture-checklist.md).
- Novos consumidores de um mesmo facto de domínio → ADR de messaging (outbox/fila dedicada).
- Breaking API → versionamento `/api/vN` conforme blueprint §12.

## Critérios de sucesso

1. Nenhuma feature nova grava ou lê dados tenant-scoped sem `Principal` + filtro `tenant_id`.  
2. Parsers e integrações externas não são chamados a partir de routers.  
3. Alterações de contrato passam pela Frente Architect com nota de impacto.  
4. Blueprint permanece a referência; desvios exigem ADR.
