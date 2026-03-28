# Orquestração — vários chats / agentes Cursor (4Pro_BI)

**Objetivo:** operacionalizar o plano em [PARALELA-5-FRENTES.md](./PARALELA-5-FRENTES.md) e os gates em [EXECUCAO-MESTRE.md](./EXECUCAO-MESTRE.md) com **sessões paralelas** no Cursor (ou worktrees), sem colisões no Git.

**Papel humano recomendado:** **coordenador técnico** (1 pessoa) — fila de `main.py`, Alembic heads, merges e “contrato pronto para consumir”.

---

## 1. Quantas sessões abrir

| Sessão / chat | Nome sugerido no Cursor | Foco |
|---------------|-------------------------|------|
| **C0** | `4Pro — Coordenação` | Gates, merges, conflitos, ordem de PRs, fila Alembic |
| **C1** | `4Pro — F1 Architect` | `docs/` (exceto `CHECKLISTS/`), `packages/contracts/` |
| **C2** | `4Pro — F2 Core` | API Core, `main.py`, `models/__init__.py`, migrações `core__*` |
| **C3** | `4Pro — F3 Data` | Upload/ingestão/datasets, worker, `packages/shared`, migrações `data__*` |
| **C4** | `4Pro — F4 Frontend` | `apps/web/` |
| **C5** | `4Pro — F5 QA` | `apps/api/tests/`, `docs/CHECKLISTS/`, `scripts/`, `.github/workflows/`, `e2e/` raiz |

Opcional: **C6 Security** — não é frente de código; usar para revisão de PRs (ver `docs/AGENTS.md` §7).

**Worktrees (opcional):** um worktree por frente reduz checkout misturado; o **merge** continua linear no `main`. Comando típico:

```bash
git worktree add ../4pro-f4-web main   # exemplo só para F4
```

Regra: cada agente só comita nas **pastas permitidas** da sua frente (tabela na secção 4).

---

## 2. Ordem de arranque (primeiros dias)

1. **C0** lê `docs/plans/EXECUCAO-MESTRE.md` §0.3 e confirma gate atual (**G0** … **G4**).
2. **C5** corre baseline: `pytest apps/api/tests`, `npm run build` em `apps/web`, `scripts/run-ticket-pipeline.sh` se aplicável — regista estado no canal/checklist.
3. **C1** + **C2** primeiro se ainda faltar **001** ou contratos instáveis: **contrato antes de UI/BE divergirem** (`EXECUCAO-MESTRE` §0.1).
4. Depois de **G1** (login + tokens): **C2**, **C3**, **C4**, **C5** podem trabalhar em paralelo conforme [PARALELA-5-FRENTES.md](./PARALELA-5-FRENTES.md) §2 Onda 1.
5. Depois de **G2** (004+005): Onda 2 em paralelo.
6. **Onda 3:** fechar **009**; **010** enforcement — **C2 + C3 coordenados** (um PR conjunto ou ordem explícita no C0).

---

## 3. Rituais de sincronização (curtos)

**Diário (15 min) ou assíncrono no canal**

- Qual gate estamos? Algum bloqueio em `packages/contracts`?
- Fila **Alembic:** quem tem o próximo ficheiro de revisão?
- Alguém precisa de **integração** em `main.py` / `models/__init__.py`? → só **C2**, fila no C0.

**Por PR**

- [ ] Pastas respeitam a allowlist da frente (secção 4).
- [ ] Se mudou JSON público: **C1** já mergeou contrato / ADR?
- [ ] `pytest` + build web verdes (C5 pode ajudar a corrigir CI).

---

## 4. Allowlists — zero sobreposição (recomendado)

Estas regras evitam dois agentes no mesmo ficheiro. Alinhado à prática descrita em `docs/ARCHITECTURE.md` (pacotes) e ao plano de 5 frentes.

| Dono | Pode editar |
|------|-------------|
| **F1** | `docs/**` exceto `docs/CHECKLISTS/**`; `packages/contracts/**`; opcional `packages/ui/**` |
| **F2** | `apps/api/fourpro_api/main.py`, `routers/auth.py`, `me.py`, `health.py`, `tenant.py`, `core/**`, `dependencies/auth.py`, services Core (auth, password, mail, billing), `repositories/**` exceto `ingestion_repository.py`, models Core + `models/__init__.py`, `config.py`, `limiter.py`, `logging_config.py`, `dev_seed.py`, `alembic/versions/*core__*` |
| **F3** | `routers/uploads.py`, `ingestions.py`, `datasets.py`, `upload_validation`, `ingestion_repository`, `models/ingestion.py`, `jobs/**`, `tasks_dispatch.py`, `apps/worker/**`, `packages/shared/**`, `alembic/versions/*data__*` |
| **F4** | `apps/web/**` |
| **F5** | `apps/api/tests/**`, `docs/CHECKLISTS/**`, `scripts/**`, `.github/workflows/**`, `e2e/**` (raiz) |

**Inegociável:** **F3 não edita** `main.py` nem `models/__init__.py`. Novas rotas de dados: ficheiros já existentes da F3 ou pedido de **integração** à F2 (um PR pequeno só de wiring).

**Migrações:** ficheiros **novos**; prefixo `core__` (F2) vs `data__` (F3); **não** reescrever a mesma revisão em dois chats.

---

## 5. Prompts prontos por chat (copiar para cada sessão)

**Prompts completos e autocontidos (com allowlists e objetivos):**  
→ **[PROMPTS-CHATS-CURSOR.md](./PROMPTS-CHATS-CURSOR.md)**

Abre esse ficheiro, escolhe a secção **C0** … **C6**, copia o bloco `text` inteiro para o primeiro turno do chat correspondente e anexa com `@` os ficheiros indicados na linha **Contexto (@…)** acima de cada bloco.

---

## 6. Estratégia de branches (sugestão)

- `main` — sempre integrável; protegido se possível.
- Por frente: `feat/f1-contracts-xyz`, `feat/f2-core-xyz`, `feat/f3-data-xyz`, `feat/f4-web-xyz`, `chore/f5-qa-xyz`.
- **Integração wiring:** `chore/f2-integrate-datasets-router` quando F3 terminou código mas precisa `include_router` (se ainda não existir).

---

## 7. Quando um agente “foge” da allowlist

1. Parar o PR; mover ficheiros para a frente correta ou reverter.
2. Se for inevitável toque cruzado: **PR único** com reviewer humano e nota no corpo do PR.

---

## 8. Documentos de referência rápida

| Documento | Uso |
|-----------|-----|
| [PARALELA-5-FRENTES.md](./PARALELA-5-FRENTES.md) | Ondas, prompts longos por agente |
| [EXECUCAO-MESTRE.md](./EXECUCAO-MESTRE.md) | Gates G0–G4, dependências entre tickets |
| [docs/AGENTS.md](../AGENTS.md) | Papéis da squad |
| [docs/adr/000-contract-slices.md](../adr/000-contract-slices.md) | Cortes de `fourpro_contracts` |

---

**Última nota:** orquestração boa é **merge frequente + filas explícitas** (`main.py`, Alembic). O Cursor multi-chat acelera; o **C0** evita que três agentes reescrevam o mesmo ficheiro.
