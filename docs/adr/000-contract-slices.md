# ADR 000 — Cortes de contrato do projeto 4Pro_BI (Frente Architect)

## Contexto

O projeto **4Pro_BI** (entrega base alinhada aos tickets **000–010**) partilha DTOs entre `apps/api`, `apps/worker` e consumidores via `packages/contracts` (`fourpro_contracts`). A partição em cinco frentes ([gestão paralela em 5 frentes](../plans/PARALELA-5-FRENTES.md)) atribui **exclusivamente** a edição deste pacote à **Frente 1 (Architect)**.

## Decisão

1. **Auth / sessão:** `fourpro_contracts.auth` — login, refresh, MFA, reset.
2. **Ingestão / upload:** `fourpro_contracts.ingestion` — itens de histórico e resposta de criação de upload.
3. **Catálogo:** `fourpro_contracts.dataset` — listagem paginada de datasets processados.
4. **Tenant / admin:** `fourpro_contracts.tenant` — membros do tenant (listagem para administradores).
5. **Billing / contexto:** `fourpro_contracts.billing` — resumo de plano e payload de `GET /api/v1/me/context` (limites e identificação do tenant ativo).

Alterações a estes módulos devem documentar impacto em `docs/ARCHITECTURE.md` (secção Pacotes) ou num ADR numerado seguinte.

## Consequências

- Backend Core e Backend Data **importam** estes modelos; não duplicam shape em Pydantic local salvo exceção acordada.
- Estados do ciclo de ingestão (`uploaded` … `failed`) estão tipados em `fourpro_contracts.ingestion`; o catálogo (`dataset`) fixa `status` em `processed` para itens listados — ver [ARCHITECTURE.md](../ARCHITECTURE.md) (secção Core vs Data).
- `TokenResponse.token_type` é literal `bearer` em `fourpro_contracts.auth` (OAuth2-style); outro esquema de token exigiria novo campo ou versão de API.
- O frontend pode espelhar tipos localmente em TypeScript; a fonte de verdade de payload JSON é o OpenAPI gerado a partir da API.

## Status

Aceite para o projeto 4Pro_BI (fase base, tickets 000–010).
