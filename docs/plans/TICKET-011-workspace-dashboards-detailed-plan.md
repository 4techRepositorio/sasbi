# Plano detalhado — TICKET-011 Workspace e dashboards (Marco C)

**Papéis:** Architect · Product · Backend · Frontend · Security  
**Status:** planejado (pós TICKET-009 + 010)  
**Ticket:** `tickets/TICKET-011-workspace-dashboards.md`  
**Alinhamento:** `docs/ROADMAP.md` Fase 3; `docs/wireframes/validation-workspace-dashboards.md`; Marco **C** em `EXECUCAO-MESTRE.md`.

## 1. Objetivo

Entregar **BI utilizável** multitenant: workspace com dashboards que consomem datasets do catálogo (`processed`), com edição vs visualização, export mínimo e isolamento garantido por tenant e papel.

## 2. Validação arquitetural — ADR obrigatório antes de implementação pesada

| Opção | Prós | Contras |
|-------|------|---------|
| **A — Motor incorporado** | Rápido para gráficos avançados via OSS sob proxy/BFF | SSO, RLS e multitenant no embed exigem desenho cuidadoso |
| **B — Canvas próprio** (Angular) | Controlo total, alinhado ao Figma Make | Esforço de widgets e motor de query |
| **C — Híbrido** | Relatórios embutidos + shell Angular | Dois subsistemas a operar |

**Experiência unificada (obrigatório):** qualquer opção deve cumprir `docs/ARCHITECTURE.md` § *Aceleradores open-source e experiência unificada* — mesmo domínio, tema da app, sem cromo ou marcas de terceiros visíveis ao cliente.

**Saída da fase de planeamento:** ADR em `docs/` escolhendo A/B/C + modelo de autorização (quem cria/edita dashboard).

## 3. Escopo MVP sugerido

| Incluído | Excluído (fases seguintes) |
|----------|----------------------------|
| Lista de dashboards por tenant | Whitelabel completo (Marco E) |
| Canvas ou páginas com widgets KPI + gráfico simples + tabela | Cubo OLAP / drill infinito |
| Vínculo widget → dataset do catálogo | SQL ad-hoc do utilizador final |
| Export snapshot (PNG/PDF ou pacote definido no ADR) | Refresh ao vivo tipo streaming |

## 4. Contratos e backend

1. Modelos: `dashboards`, `dashboard_versions` ou JSON de layout; sempre `tenant_id`.
2. APIs: CRUD restrito por tenant e RBAC (alinhado TICKET-005); leitura de dados apenas via serviços que reutilizam queries do catálogo.
3. Nunca aceitar `tenant_id` do cliente sem validação de membership.

## 5. Frontend (Angular)

1. Rotas sob `/app/...` com guard de papel (analyst/admin vs consumer read-only).
2. Estados: loading / erro / vazio / sucesso em lista e editor.
3. Indicação clara do **tenant ativo** (regra `.cursor/rules/03-frontend.mdc`).

## 6. Subtarefas (ordem lógica)

1. ADR + desenho de dados (layout JSON schema).
2. Migrations + APIs dashboard + testes de isolamento.
3. UI lista + editor mínimo + modo visualização.
4. Integração com API de datasets (metadados + amostra agregada se necessário).
5. Export MVP + documentação em `docs/ARCHITECTURE.md`.

## 7. QA — critérios de aceite

- [ ] Tenant A não vê dashboards de B.
- [ ] Consumer não edita se a matriz RBAC assim definir.
- [ ] Widget com dataset indisponível: UX de placeholder (critério D5 do wireframe).
- [ ] Checklists frontend + backend atualizados.

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Scope de embed mal dimensionado | Timebox ADR; spike técnico 2–3 dias |
| Performance em datasets grandes | Paginação/agregação no backend; limites por plano (010) |

## 9. Dependências

TICKET-004, 005, 009; TICKET-010 recomendado para quotas de dashboards/export.

## 10. Próximo ticket

TICKET-012 (governança de dados) pode paralelizar após ADR de armazenamento analítico.

## Nota de UX

Textos de UI, exports e emails devem usar apenas a marca e terminologia do produto; mensagens de erro genéricas (“Não foi possível carregar o relatório”) em vez de identificadores de componente interno.
