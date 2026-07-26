# Checklist — Onda BI (011–013, 015–017)

Data: 2026-07-25

## Fluxo feliz

- [x] Health devolve `X-Request-ID`; `/metrics` expõe contadores
- [x] Promote bronze→silver cria dataset com lineage
- [x] CRUD dashboard isolado por tenant; export JSON
- [x] Fonte com secret: listagem sem fuga; sync enfileira/processa
- [x] Query semântica agrega por dimensão
- [x] Desktop publish dataset/dashboard aparece na Web API

## Erro / permissões

- [x] Consumer não cria dashboard
- [x] Cross-tenant promote/fonte/dashboard → 404
- [x] Host REST privado bloqueado no SPI

## Contratos / billing

- [x] `DatasetItem.layer` + contratos novos exportados
- [x] Quotas existentes inalteradas no caminho de upload

## Docs

- [x] ADR-003, ADR-004, product briefing, SECURITY/ARCHITECTURE/INGESTION/CHANGELOG
