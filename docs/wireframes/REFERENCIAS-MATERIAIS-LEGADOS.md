# Referências: PDF, Figma e planos antigos

**Objetivo:** amarrar os materiais que você anexou ao repositório às validações de wireframe e ao roadmap atual, sem perder o fio dos marcos comerciais (A–E) do plano Data_4tech.

## 1. `Data Analytics Solution.pdf` (raiz do repositório)

| Aspecto | Detalhe |
|--------|---------|
| Localização | `/opt/4Pro_BI/Data Analytics Solution.pdf` (nome com espaço; 7 páginas, `Lang(pt)`) |
| Texto extraível | Quase só o título na capa; o corpo é **imagem/screenshot** — a validação visual deve ser feita **abrindo o PDF** ou o protótipo ligado abaixo. |
| Link encontrado no PDF | Protótipo Figma publicado: `https://dig-wired-11893301.figma.site/` (ação URI na primeira página). |

**Uso recomendado para UX/design:** tratar o PDF como **captura do protótipo**; usar o `figma.site` como referência interativa ao preencher critérios nas folhas `validation-*.md`.

## 2. Pasta `docs_planos_antigos/`

Contém o **plano mestre OSS** (fases P0–P8, sub-planos P0-01…P8-04), alinhado ao documento de solução de dados multitenant.

| Recurso | Conteúdo |
|---------|----------|
| `docs_planos_antigos/plans/README.md` | Índice executável dos sub-planos |
| `docs_planos_antigos/plans/PLANO-MAESTRE-BI-SaaS-Por-Fases.md` | Visão monolítica + todos YAML + marcos A–E |
| `docs_planos_antigos/plans/00-VISAO-E-GOVERNANCA.md` | Governança, riscos, LGPD, DoD global |
| `docs_planos_antigos/plans/00-STACK-E-FLUXOS.md` | Tabela de stack OSS (Keycloak, MinIO, Dagster, dbt, Cube, Superset…) e diagrama Mermaid |

**Marcos comerciais (extraídos dos planos antigos):**

- **Marco A** (pós P2-07): upload → bronze + UI de histórico — “laboratório credível”.
- **Marco B** (pós P3-03): silver/gold + retenção — “produto de dados mínimo”.
- **Marco C** (pós P5-04): BI embed multitenant seguro — **primeiro pacote precificável**.
- **Marco D** (pós P6-03): planos, quotas, bloqueio — “SaaS fechável”.
- **Marco E** (pós P7-03 + P8-04): whitelabel forte, observabilidade, auditoria.

## 3. Cruzamento com tickets atuais (`tickets/TICKET-*.md`)

Mapeamento **conceitual** (não 1:1 com IDs P*-*):

| Tickets 4Pro_BI | Equivalente aproximado nos planos antigos |
|-----------------|-------------------------------------------|
| TICKET-000 Scaffold / Compose | P0-01…P0-03 (infra base, repositório, CI mínimo) |
| TICKET-001 Auth core | P0-04 + P0-06 + parte portal (stack antiga: Keycloak OIDC) |
| TICKET-002 Password recovery | P1-01 |
| TICKET-003 MFA | P1-02 (e-mail; WhatsApp = P7-01 no plano antigo) |
| TICKET-004 Tenant | P0-05 + P1-06 + modelo multitenant |
| TICKET-005 RBAC | P1-03 |
| TICKET-006 Upload | P2-01 |
| TICKET-007 Metadata | P2-02 |
| TICKET-008 Parser pipeline | P2-03…P2-06 + worker |
| TICKET-009 Catalog | Visível no portal + APIs; antigo plano evolua para Gold/Cube |
| TICKET-010 Billing | P6-01…P6-03 |
| TICKET-011 Workspace / dashboards | Marco C / P5-04 (embed BI) |
| TICKET-012 Governança de dados | Marco B / P3-03 (silver/gold) |
| TICKET-013 Observabilidade enterprise | Marco E / P7-03 + P8-04 (parcial) |
| TICKET-014 CI quality gates | P0-07 equivalente (automação PR) |

## 4. Divergência de stack: planos antigos × regras atuais do workspace

| Área | Planos antigos (`00-STACK-E-FLUXOS`) | Regras `.cursor/rules` do repo 4Pro_BI |
|------|--------------------------------------|----------------------------------------|
| Identidade | Keycloak (OIDC, MFA, grupos) | FastAPI + auth na **apps/api** (JWT/sessão) |
| Frontend | Portal **React** whitelabel | **Angular** (`apps/web`) |
| Orquestração / ETL | Dagster + dbt + camadas Bronze/Silver/Gold | Celery/worker + pipeline (tickets 007–008) |
| BI / dashboards | Apache Superset + Cube | “Dashboards tipo Figma / Power BI” — **a definir** se Superset/Cube entram como ADR ou substituto próprio |

**Implicação:** os wireframes em `validation-workspace-dashboards.md` devem continuar válidos **como comportamento de produto**; a **implementação** precisa de **ADR** escolhendo entre (a) adotar a stack OSS do plano antigo embutida no monorepo, ou (b) manter stack enxuta FastAPI/Angular e integrar apenas peças selecionadas (ex.: object storage + worker).

## 5. Como usar isto nas validações de wireframe

1. Abrir o **PDF** e o link **figma.site** lado a lado com `docs/wireframes/validation-*.md`.  
2. Para cada linha das tabelas de critérios, marcar **validado** se o protótipo cobre loading/erro/vazio/sucesso e tenant explícito onde aplicável.  
3. Registrar no sign-off qual versão do PDF/protótipo foi usada (data).  
4. Evidências exportadas (PNG/PDF) alinhadas à app ou ao desenho aprovado: guardar em [`docs/assets/wireframes/exports/`](../assets/wireframes/exports/) e referenciar nas folhas `validation-*.md` — ver [`docs/assets/README.md`](../assets/README.md).
