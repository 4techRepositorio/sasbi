# Planos por ticket (015–017) — plataforma BI

Resumo executável; planos detalhados em `docs/plans/TICKET-01X-*-detailed-plan.md`.  
Programa: [`PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](./PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md) · ADR [`001`](../adr/001-bi-platform-connectors-desktop-web.md).

---

## TICKET-015 — Framework de conectores

**Objetivo:** SPI de plugins, cofre de credenciais, jobs de sync; conectores `file` + `postgres` + `rest_json`.

**Plano:** Pacote `packages/connectors`; modelos `data_sources`; APIs test/sync; worker extract → pipeline de ingestão existente.

**Saída:** Fonte SQL/REST syncada aparece no catálogo do tenant; secrets não vazam; isolamento testado.

---

## TICKET-016 — Semântica e BI Web

**Objetivo:** Modelo semântico mínimo + query agregada; widgets Web (TICKET-011) consomem a API; UI Fontes de dados.

**Plano:** Contracts `semantic`; `/query` com allowlist; híbrido canvas Angular; experiência unificada.

**Saída:** KPI/dashboard no Web a partir de dataset processado; zero cross-tenant.

---

## TICKET-017 — Desktop authoring

**Objetivo:** App Desktop autentica, configura fonte, publica dataset/dashboard para o Web.

**Plano:** Spike Electron vs Tauri → ADR-003; `apps/desktop`; publish via APIs 015/016/011; secure storage.

**Saída:** Round-trip Desktop → API → Web no mesmo tenant; build documentado para OS prioritário.

---

## Ordem e paralelismo

```text
015 (SPI + O1) ──┬──► 016 (query + Web) ──► 017 (Desktop)
                 │
011 (canvas) ────┘  (em paralelo após contratos de query estáveis)
012 (camadas) ─────── paralelo com 015/016 quando ADRs de storage alinhados
```

- **015** bloqueia sync real no Desktop e a UI de Fontes.
- **016** e **011** partilham modelo de dashboard — um PR de contratos antes de ambos fecharem UI.
- **017** só após APIs de publish estáveis (015+016 mínimos).
