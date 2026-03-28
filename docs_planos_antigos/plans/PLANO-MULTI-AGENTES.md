# Plano multi-agente — programar o Data_4tech BI SaaS

Objetivo: **vários agentes** (ou desenvolvedores) trabalharem **em paralelo** sem pisar o mesmo código nem quebrar contratos. Use com Cursor (várias janelas / Composer), ou equipa humana.

---

## Princípios

1. **Um sub-plano ativo por agente** — nunca dois agentes no mesmo `P*-*` ao mesmo tempo.
2. **Contratos antes de implementação** — ADR P0-05 (multitenant), formatos de evento (`dataset_ready`), prefixos MinIO, claims JWT (`tenant_id`).
3. **Integração só em pontos de sincronização** — merges curtos; `main` sempre deployável em dev.
4. **Dono por pacote no monorepo** — cada trilha tem pastas preferenciais (abaixo).

---

## Papéis (trilhas) e sub-planos sugeridos

### Trilha A — Fundação e infra (`infra/`, Compose)

**Dono:** Agente **Infra**

| Ordem | Sub-plano | Notas |
|--------|-----------|--------|
| 1 | P0-02 | Postgres + Redis |
| 2 | P0-03 | MinIO |
| 3 | P0-04 | Keycloak |
| paralelo após P0-01 | P0-05 | ADR multitenant — **bloqueante** para Trilhas C e D |

Pode preparar `docker-compose.yml` modular (profiles: `core`, `bi`, `ops`).

---

### Trilha B — Monorepo e API base (`platform-api/`)

**Dono:** Agente **Platform**

| Ordem | Sub-plano | Notas |
|--------|-----------|--------|
| 1 | P0-01 | Estrutura monorepo — **primeiro na fila global** |
| 2 | P0-06 | Health + Postgres + MinIO client |
| 3 | P0-07 | CI mínimo |
| 4 | P1-06 | Sync user/tenant no DB app |
| 5 | P2-01, P2-02 | Upload + modelo ingestions |
| 6 | P5-06 | Webhook/evento `dataset_ready` (após Trilha D estar no P3-02) |
| 7 | P6-01 … P6-03 | Billing e enforcement |
| 8 | P8-03 | Auditoria exports |

**Depende de:** P0-05 para queries com `tenant_id`/schema; P1-03 para JWT.

---

### Trilha C — Identidade e front (`portal/`)

**Dono:** Agente **Portal**

| Ordem | Sub-plano | Notas |
|--------|-----------|--------|
| 1 | P1-01 | Email + reset (Keycloak) |
| 2 | P1-02 | MFA |
| 3 | P1-03 | Grupos e claims — **sincroniza com Platform** |
| 4 | P1-04 OIDC | |
| 5 | P1-05 | Whitelabel — consome `GET /tenants/:id/branding` |
| 6 | P2-07 | UI ingestões |
| 7 | P5-04 | Embed Superset |
| 8 | P6-04 | UI planos |
| 9 | P7-02, P7-03 | Host/TLS e tema Keycloak (fase tardia) |

**Depende de:** P0-04 (Keycloak); P0-06 (API branding); P5-01+ para embed real.

---

### Trilha D — Pipeline de dados (`dagster/`, `dbt/`)

**Dono:** Agente **Data**

| Ordem | Sub-plano | Notas |
|--------|-----------|--------|
| 1 | P2-03 | Dagster skeleton |
| 2 | P2-04 | Loader CSV/JSON Bronze |
| 3 | P2-05, P2-06 | TXT, XLSX |
| 4 | P3-01 | dbt camadas |
| 5 | P3-02 | dbt via Dagster — **marco de integração** |
| 6 | P3-03 | Retenção/purge |
| 7 | P3-04, P3-05 | GE mínimo; OpenLineage opcional |
| 8 | P8-01, P8-02 | Qualidade e performance (tardio) |

**Depende de:** P0-05; P2-02 (ingestion_id, paths MinIO); API pode **disparar** run via webhook após P3-02.

---

### Trilha E — Semântica e BI (`cube/`, Superset config)

**Dono:** Agente **Analytics**

| Ordem | Sub-plano | Notas |
|--------|-----------|--------|
| 1 | P4-01 | Cube + Postgres gold |
| 2 | P4-02 | Modelo semântico |
| 3 | P4-03 | Pre-agg + Redis |
| 4 | P4-04 | Refresh pós-dbt — alinha com Trilha D |
| 5 | P5-01 | Superset + datasource |
| 6 | P5-02 | OIDC |
| 7 | P5-03 | Security manager multitenant — **crítico** |
| 8 | P5-05 | Templates |

**Depende de:** P3-02 (gold estável); P1-03 (claims); P0-05.

---

### Trilha F — Enterprise e operações

**Dono:** Agente **Ops / Sec**

| Ordem | Sub-plano | Notas |
|--------|-----------|--------|
| 1 | P7-01 | WhatsApp OTP (isolado) |
| 2 | P8-04 | Prometheus, Grafana, Loki |
| 3 | P6-02 | Kill Bill ou billing interno (pode dividir com Platform) |

---

## Pontos de sincronização (todo mundo para e alinha)

| Ponto | Quando | O quê alinhar |
|--------|--------|----------------|
| **S1** | Após **P0-01** + **P0-05** | Estrutura pastas; ADR multitenant; variáveis `.env.example` partilhadas |
| **S2** | Após **P1-03** | Formato JWT; nome do claim `tenant_id`; grupos realm |
| **S3** | Após **P2-02** | Schema tabela `ingestions`; contrato webhook Dagster/API |
| **S4** | Após **P3-02** | Pipeline demo ponta a ponta; evento “job success” para Cube refresh |
| **S5** | Após **P5-03** | Teste manual 2 tenants; nunca merge sem passar |

Reunião (ou thread) curta: 15 min + checklist escrito no `docs/runbooks/sync-Sn.md`.

---

## Paralelização máxima segura (exemplo semana 1 em dev)

Depois de **P0-01** concluído:

- **Agente Infra:** P0-02, P0-03, P0-04 em sequência.
- **Agente Platform:** aguarda P0-02 + P0-03; faz P0-06; em paralelo documenta API stub.
- **Agente Data:** aguarda P0-02 + P0-05; P2-03 depois P2-04.
- **Agente Portal:** aguarda P0-04; P1-01 → P1-02.

**P0-05** deve ser fechado **antes** de P2-04 e P3-01 (idealmente dono: Platform ou Infra, um único PR).

---

## O que colar ao abrir cada agente

**Agente Infra**

```text
És o Agente Infra do Data_4tech. Segue docs/plans/PLANO-MULTI-AGENTES.md — Trilha A.
Trabalha só nos sub-planos que te indiquei (ex.: P0-02). Não edites portal/ nem dbt/ sem coordenação.
```

**Agente Platform**

```text
És o Agente Platform. Trilha B em PLANO-MULTI-AGENTES.md.
Respeita o ADR em docs/adr/ para multitenancy. Um sub-plano por PR.
```

(Repetir o padrão para Portal, Data, Analytics, Ops.)

---

## Conflitos frequentes e como evitar

- **Mesmo ficheiro:** `docker-compose.yml` — um dono (Infra); outros pedem alterações em issue ou patch pequeno.
- **`tenant_id`:** só no ADR + código gerado a partir disso; nunca cada agente inventa um formato.
- **Migrations:** sequential naming; um agente “dono” de migrações na semana ou fila explícita.

---

## Resumo

- **6 trilhas** nomeadas: Infra, Platform, Portal, Data, Analytics, Ops.
- **6 pontos S1–S5** (podes reduzir a S1/S2/S4 se a equipa for pequena).
- **46 sub-planos** continua a ser a granularidade; cada agente puxa o próximo **livre** da sua trilha conforme dependências.
