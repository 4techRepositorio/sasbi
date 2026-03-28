# Planos por ticket (011–014) — fase pós-MVP

Resumo executável; planos detalhados em `docs/plans/TICKET-01X-*-detailed-plan.md`. Marcos em `EXECUCAO-MESTRE.md` §2.

---

## TICKET-011 — Workspace e dashboards (Marco C)

**Objetivo:** BI utilizável multitenant; ADR motor incorporado (OSS) vs canvas Angular; cumprir experiência unificada em `docs/ARCHITECTURE.md`.

**Plano:** Modelos `dashboards`; APIs com `tenant_id`; UI lista/editor; export snapshot; wireframes `validation-workspace-dashboards.md`.

**Saída:** ADR escrito; critérios W1–D5 do wireframe endereçados no MVP escolhido.

---

## TICKET-012 — Governança de dados (Marco B)

**Objetivo:** Camadas dados + lineage mínimo + retenção documentada.

**Plano:** ADR armazenamento; migrations metadados; job promoção; API catálogo com filtro de camada.

**Saída:** Nenhuma promoção cruza tenant; ARCHITECTURE descreve camadas.

---

## TICKET-013 — Observabilidade enterprise (Marco E)

**Objetivo:** `correlation_id`, auditoria persistida, métricas/health.

**Plano:** Middleware; `audit_events`; worker propagando ID; `/metrics` opcional.

**Saída:** Fluxo upload→worker rastreável; ações críticas auditadas.

---

## TICKET-014 — CI quality gates

**Objetivo:** Workflow remoto: pytest + build Angular (e extensões documentadas).

**Plano:** GitHub Actions ou GitLab CI; cache; DB efémero se preciso.

**Saída:** Branch protection com CI verde.

---

## Ordem e paralelismo

- **014** e **013** são transversais: podem avançar **em paralelo** com **011** e **012** assim que existir base (Git remoto; API/worker tocáveis).
- **011** após **009** (+**010** recomendado para quotas).  
- **012** em **paralelo** com **011** após ADRs alinhados (dados vs BI).  
- Ver trilhos e gates em [`EXECUCAO-MESTRE.md`](./EXECUCAO-MESTRE.md) §0 e §1.1.
