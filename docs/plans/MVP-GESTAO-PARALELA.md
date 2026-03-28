# MVP SaaS de dados — 5 frentes paralelas e prompts por agente

**Papel:** gestão técnica (derivado de `docs/AGENTS.md`, `docs/VISION.md`, `docs/ARCHITECTURE.md`, `tickets/`).  
**Escopo MVP:** tickets **000–010** (Marco A laboratório + SaaS fechável com quotas); **011+** fora do MVP mínimo, salvo decisão explícita.

---

## 1. Cinco frentes independentes (áreas de repositório disjuntas)

| # | Frente | Áreas do repo (donos) | Tickets MVP típicos | Agente (`docs/AGENTS.md`) |
|---|--------|------------------------|---------------------|---------------------------|
| **F1** | **Arquitetura e contratos** | `docs/` (ARCHITECTURE, ADRs, `docs/plans/`, `docs/wireframes/` revisão), **`packages/contracts`**, `packages/shared` *apenas* tipos/DTOs partilhados acordados | Transversal; fecha cortes de contrato para 006–009 | **Architect** |
| **F2** | **Backend Core (plataforma)** | `apps/api/…` — auth, tenant, RBAC, billing, `core/`, dependencies de contexto; **não** inclui routers de upload/ingestão/datasets | 001–005, 010 (com Data para enforcement em upload/job) | **Backend Core** |
| **F3** | **Backend Data (pipeline)** | `apps/api/…` — upload, ingestions, datasets; **`apps/worker/`**; integração storage; parsers util em `packages/shared` *lado dados* | 006–009 | **Backend Data** |
| **F4** | **Frontend** | **`apps/web/`** exclusivamente | UI para 001–005, 006–009, shell/dashboard resumo | **Frontend** |
| **F5** | **Qualidade e evidências** | **`apps/api/tests/`**, testes web se existirem, **`docs/CHECKLISTS/`**, `scripts/` de smoke/pipeline, CI (014) | Transversal; critérios de aceite por ticket | **QA Reviewer** |

### Regras anti-sobreposição

- **Contratos:** F1 propõe/estabiliza DTOs em `packages/contracts`; F2/F3 **importam** e não redefinem nomes de campos sem alinhar F1 num PR curto de contrato.
- **API monolito:** F2 e F3 tocam ficheiros diferentes sob `routers/`, `services/`, `models/` por domínio; evitar o mesmo ficheiro na mesma sprint (ex.: não editar `main.py` em dois PRs — **serializar** ou um único PR de “bootstrap rotas”).
- **Migrações Alembic:** um **coordenador** (pode ser Architect ou Core) serializa heads; F2 e F3 alternam revisions ou usam fila no canal.

---

## 2. Plano de execução paralela (ondas)

### Onda 0 — Pré-requisito (curta)

- Verificar **000** (compose, health).  
- **F5** liga `scripts/run-ticket-pipeline.sh` / pytest baseline.  
- **F1** confirma ADR mínimo: multitenancy + prefixos API (`/api/v1`).

### Onda 1 — Após **001** (gate G1)

Em **paralelo**:

| Frente | Entrega da onda |
|--------|-----------------|
| F1 | Contratos OpenAPI/DTO para forgot/reset/MFA e para `me/context` |
| F2 | **002**, **003**, **004** (coordenar migrations) |
| F3 | Spike: contrato de **006** (multipart) + modelo mental **007** (estados) sem bloquear Core |
| F4 | Telas login/MFA/reset + preparação shell quando **004** existir |
| F5 | Testes API auth + isolamento tenant (esqueleto para 004) |

### Onda 2 — Após **004 + 005** (gate G2)

Em **paralelo**:

| Frente | Entrega |
|--------|---------|
| F2 | **010** modelagem + início enforcement |
| F3 | **006 → 007 → 008** encadeado dentro da frente |
| F4 | Upload, ingestões, catálogo, guards por papel |
| F1 | ADR storage (disco vs MinIO) + atualização ARCHITECTURE |
| F5 | Testes integração upload→worker→processed; checklists |

### Onda 3 — Fecho MVP

- **009** + UI catálogo (F3 + F4).  
- **010** enforcement final em upload/job (F2 + F3 toque pontual — **um PR conjunto** ou ordem explícita).  
- **F5** smoke E2E manual ou automatizado + sign-off `docs/CHECKLISTS/`.

**Referência global:** `docs/plans/EXECUCAO-MESTRE.md` §0 (gates G0–G4).

---

## 3. Prompt — Architect

```text
Contexto: monorepo 4Pro_BI — FastAPI + Angular + Celery, multitenancy obrigatório. Lê docs/ARCHITECTURE.md, docs/VISION.md, docs/plans/EXECUCAO-MESTRE.md §0, e tickets 000–010.

Papel: Architect (docs/AGENTS.md). Não implementes features grandes em apps/api ou apps/web.

Objetivos:
1. Manter docs/ARCHITECTURE.md alinhado ao MVP (blocos, domínios, experiência unificada sem marcas OSS na UX).
2. Propor ou atualizar ADRs em docs/ (pasta docs/adr/ se criares) para: storage de upload, evolução de contratos ingestão→catálogo, e corte de billing enforcement.
3. Definir/estabilizar contratos em packages/contracts (DTOs) para endpoints críticos do MVP, com impacto documentado.
4. Resolver ambiguidades entre Backend Core e Backend Data (quem expõe o quê) em texto curto no ADR ou ARCHITECTURE.

Entregáveis: PRs só em docs/, packages/contracts (e packages/shared se forem tipos neutros). Critério: outras frentes conseguem implementar sem reescrever decisão.
```

---

## 4. Prompt — Backend Core

```text
Contexto: apps/api — identidade, tenants, RBAC, billing. Regras em .cursor/rules/02-backend.mdc e 06-security.mdc. Tickets: 001–005, 010 (modelos e enforcement em coordenação com Data).

Papel: Backend Core (docs/AGENTS.md).

Objetivos:
1. Garantir auth (login, refresh, MFA verify, forgot/reset), contexto de tenant válido só a partir de token/sessão, RBAC em rotas administrativas e sensíveis.
2. Implementar billing/planos e quotas com enforcement chamável a partir dos serviços de upload/job (interface clara; evitar duplicar lógica de ingestão).
3. Manter camadas: routers → services → repositories; testes pytest por fluxo crítico.

Restrições: não implementes parsing, fila Celery nem routers dedicados a upload/ingestions/datasets — isso é Backend Data. Podes tocar packages/contracts alinhado ao Architect.

Entregáveis: código em apps/api nos módulos Core; migrações coordenadas. Critério: testes de isolamento tenant e RBAC verdes.
```

---

## 5. Prompt — Backend Data

```text
Contexto: upload, ingestão, worker, catálogo de datasets. docs/INGESTION.md e tickets 006–009. Regra: upload ≠ processed; estados uploaded→validating→parsing→processed|failed.

Papel: Backend Data (docs/AGENTS.md).

Objetivos:
1. Rotas e serviços de upload com validação tipo/tamanho, storage (disco/MinIO conforme ADR), metadata ingestão (007).
2. Worker Celery (008): task por ingestion_id, parsers por extensão, atualização de estado e mensagens amigáveis + log técnico.
3. API catálogo (009): listagem paginada só processed, filtro tenant obrigatório.
4. Integrar chamadas a quotas/billing via interface exposta por Core (sem duplicar modelo de planos).

Restrições: não alteres auth/tenant core além do necessário para dependency injection; não alteres apps/web.

Entregáveis: apps/api routers/services/models de dados + apps/worker + util packages/shared para formatos. Critério: teste worker com fixture pequena + teste isolamento catálogo.
```

---

## 6. Prompt — Frontend

```text
Contexto: apps/web Angular — portal multitenant. docs/wireframes/validation-*.md, .cursor/rules/03-frontend.mdc. Tickets MVP: fluxos 001–005 e páginas 006–009 + shell.

Papel: Frontend (docs/AGENTS.md).

Objetivos:
1. Telas com loading/erro/vazio/sucesso; tenant atual visível no shell administrativo; guards alinhados ao RBAC.
2. Upload, ingestões (badges de estado), catálogo, dashboard resumo se existir rota.
3. Consome apenas /api/v1; sem regras críticas só no cliente.

Restrições: não edites apps/api nem apps/worker; contratos vêm de packages/contracts ou OpenAPI acordado.

Entregáveis: PRs em apps/web. Critério: build verde + checklist frontend.
```

---

## 7. Prompt — QA Reviewer

```text
Contexto: MVP 000–010. docs/CHECKLISTS/, pytest em apps/api, scripts de smoke. docs/AGENTS.md papel QA Reviewer.

Papel: QA Reviewer.

Objetivos:
1. Expandir testes automatizados: auth, tenant isolation, RBAC, upload→estado→catálogo (integração com DB/redis de teste conforme README).
2. Manter checklists preenchidos por entrega; regressão em fluxo feliz e erros comuns.
3. Preparar ou manter smoke (script/Playwright futuro) para stack Compose/Portainer.
4. CI (014): quando aplicável, job mínimo pytest + build web.

Restrições: mudanças de produto em apps/* só via testes ou pequenos hooks de testabilidade acordados com Core/Data — evita feature creep.

Entregáveis: apps/api/tests, docs/CHECKLISTS, scripts/. Critério: pipeline local verde e critérios de aceite dos tickets demonstráveis.
```

---

## 8. Nota de gestão

- **Security Reviewer** (AGENTS §7) deve revisar PRs de F2/F3/F4 em pontos MFA, reset, upload, tenant — não é uma “sexta frente” de código no mesmo sentido; atuar em **revisão transversal**.  
- **Planner** pode usar este documento como baseline e desdobrar sprints; o **gerente técnico** resolve conflitos de `main.py`/Alembic e prioriza o gate ativo (G1, G2, …).
