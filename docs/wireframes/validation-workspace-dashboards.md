# Validação de wireframe — Workspace e dashboards (visão Power BI–like)

**Versão:** 0.6  
**Roadmap:** Fase 3 em `docs/ROADMAP.md`; antecipar validação para alinhar contratos (datasets, permissões, export).

**Referência visual:** `Data Analytics Solution.pdf` (raiz do repo) e protótipo `https://dig-wired-11893301.figma.site/`. O Marco **C** no plano mestre corresponde a BI multitenant **incorporado à solução** (sem superfície de marcas de terceiros ao utilizador — ver `docs/ARCHITECTURE.md`); detalhe de implementação em ADR. Contexto histórico: [REFERENCIAS-MATERIAIS-LEGADOS.md](./REFERENCIAS-MATERIAIS-LEGADOS.md).

## 0. Evidências visuais (exports)

**PDF raster (repo):** páginas do ficheiro raiz `Data Analytics Solution.pdf` como `data-analytics-solution-p-*.png` em [`../assets/wireframes/exports/`](../assets/wireframes/exports/) — regenerar com [`scripts/export-wireframes-from-pdf.sh`](../../scripts/export-wireframes-from-pdf.sh) ou `make wireframes-export`.  
**Capturas da app:** `E2E_WIREFRAME_CAPTURES=1` + `npm run test:wireframe-captures` em `e2e/` → `workspace-shell-v1-*.png` (só a sidebar `aside.da-shell__aside`) e `workspace-dashboard-v1-*.png` (página completa em `/app/dashboard`).

| Sugestão de ficheiro | Conteúdo |
|----------------------|----------|
| `workspace-shell-v1-YYYYMMDD.png` | Shell com sidebar + tenant (estado atual) |
| `workspace-dashboard-v1-YYYYMMDD.png` | `/app/dashboard` (KPIs + gráfico de barras + tabela) |
| `workspace-editor-v1-YYYYMMDD.png` | *Fase 3:* editor canvas D1–D5 |
| `workspace-export-v1-YYYYMMDD.png` | *Fase 3:* fluxo de export E1–E3 |

## 0.1 Mapeamento — implementação atual vs alvo

| Área wireframe | Estado hoje (`apps/web`) | Alvo (Fase 3 / TICKET-011) |
|----------------|--------------------------|----------------------------|
| W1 tenant visível | Sim (`ShellComponent`) | Manter |
| W2 navegação workspace | Parcial: Dashboard, Upload, Catálogo, Ingestões | Atalhos “dashboards salvos”, lixeira, etc. conforme ADR |
| W3 permissões | `roleGuard` em upload | Estender a editor de dashboards |
| D1–D5 editor | **Não** | Canvas / motor incorporado |
| E1–E3 export | **Não** | Snapshot PDF/PNG + auditoria |

O ecrã **`/app/dashboard` atual** cumpre uma **visão analítica resumida** (KPIs, distribuição por estado, atividade recente), alinhada ao espírito do protótipo, mas **não** substitui os critérios D/E até implementação TICKET-011.

## 1. Objetivo

Definir, antes do desenho pixel-perfect, como será o **workspace customizável**, **dashboards com barra de ferramentas** (inspirado em Figma/Power BI) e **exportações com dados embedados**, sempre respeitando **isolamento por tenant** e **permissões**.

## 2. Princípios de produto (para validação)

1. Canvas editável vs modo visualização: dois modos claramente distintos.  
2. Fonte de dados: widgets referenciam **datasets do catálogo** já processados; filtros aplicam escopo ao tenant.  
3. Export: formato alvo (PDF, PNG, pacote “relatório”) e se dados embedados incluem **snapshot** ou **conexão** — para Fase inicial, priorizar **snapshot** com aviso de “dados até data X”.

## 3. Blocos de UI

### 3.1 Shell do workspace

| # | Elemento | Critério |
|---|----------|----------|
| W1 | Tenant e ambiente | Indicação visível do tenant (regra frontend administrativo) |
| W2 | Navegação | Atalhos: catálogo, dashboards salvos, lixeira/arquivados se houver |
| W3 | Permissão | Ocultar ou desabilitar edição conforme papel (TICKET-005) |

### 3.2 Editor de dashboard (visão Figma-like)

| # | Elemento | Critério |
|---|----------|----------|
| D1 | Barra de ferramentas | Adicionar widget, desfazer/refazer mínimo, alinhar grade, camadas (ordem Z) |
| D2 | Tipos iniciais | Gráfico de barras/linha, KPI, tabela simples — lista fechada até evolução do workspace (011+) |
| D3 | Painel de propriedades | Título, dataset vinculado, campo de eixo/valores, cores |
| D4 | Filtros globais | Filtros que afetam todos os widgets compatíveis; estado salvo no dashboard |
| D5 | Erro de dados | Dataset indisponível ou vazio: placeholder no widget, não quebrar canvas |

### 3.3 Modo visualização e export

| # | Elemento | Critério |
|---|----------|----------|
| E1 | Visualização | Sem controles de edição; filtros podem permanecer se política permitir |
| E2 | Export | Confirmação de inclusão de dados; tamanho estimado ou limite |
| E3 | Auditoria | Ação de export registrada (security / billing futuro) |

## 4. Dependências técnicas a cruzar com Architect

- API de **definição de dashboard** (JSON versionado por tenant).  
- API de **query agregada** com autorização por dataset + papel.  
- Worker ou job para **render** pesado de export (se necessário).

## 5. Fora de escopo explícito na visão inicial (`docs/VISION.md`)

- BI semântico avançado, marketplace público de dashboards.  
→ Wireframes devem **não** prometer relacionamentos complexos entre datasets na fase base do produto.

## 6. Sign-off

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| design | | | |
| Architect | | | |
| Frontend | | | |
| Security | | | |
