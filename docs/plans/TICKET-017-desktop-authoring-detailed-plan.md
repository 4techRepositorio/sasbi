# Plano detalhado — TICKET-017 Desktop authoring

**Papéis:** Architect · Frontend · Backend Core · Security · QA  
**Status:** em implementação (scaffold Desktop entregue)  
**Ticket:** `tickets/TICKET-017-desktop-authoring.md`  
**ADR:** `docs/adr/001-bi-platform-connectors-desktop-web.md`

## 1. Objetivo

Cliente Desktop para autoração (fontes, modelo, dashboards) autenticado na API 4Pro_BI, com publicação no tenant e visualização no Web.

## 2. Spike obrigatório (antes do scaffold completo)

Escolher runtime:

| Opção | Prós | Contras |
|-------|------|---------|
| **Electron** | Ecossistema maduro, fácil partilhar TS | Binário pesado |
| **Tauri** | Leve, Rust security story | Curva; binding UI |

**Saída do spike:** ADR curto em `docs/adr/002-desktop-runtime.md` (a criar na execução) com a escolha e suporte OS inicial (Linux e/ou Windows primeiro).

## 3. Regras de negócio

1. Mesmo fluxo de auth da Web (login, refresh, MFA); tokens em secure storage do OS.
2. Todas as mutações passam pela API com tenant do JWT — Desktop não é fonte de verdade.
3. Publish dataset/dashboard cria versões no backend; Web lê as publicadas.
4. Rascunhos locais podem existir; conflito de publish: last-write com aviso ou version bump.
5. Indicação clara do tenant activo na UI Desktop.
6. Sem cromo ou nomes de stacks OSS na UI.

## 4. Impacto técnico

| Área | Mudança |
|------|---------|
| **apps/desktop** | Novo projecto no monorepo |
| **contracts** | `desktop_sync` — manifestos de publish |
| **API** | Endpoints de publish idempotentes (ou reutilizar 015/016/011) |
| **billing** | Seat Desktop / feature flag por plano |
| **CI** | Job de build artefacto (manual ou tag) |
| **docs** | Instalação Desktop; ARCHITECTURE blocos |

## 5. Escopo MVP Desktop

| Incluído | Excluído |
|----------|----------|
| Login + MFA + logout | Admin billing completo |
| Wizard conector Postgres/REST | Todos os conectores O2+ |
| Sample schema + publish dataset | Motor local de query pesado offline |
| Editor dashboard mínimo + publish | Colaboração em tempo real |
| Build para 1 OS prioritário | Auto-update sofisticado (fase 2) |

## 6. Subtarefas

1. Spike runtime → ADR-002.
2. Scaffold app + auth contra API local/staging.
3. Wizard fontes (APIs 015).
4. Publish dataset → verificar no Web.
5. Editor dashboard mínimo → publish → Web viewer.
6. Secure storage + testes e2e Desktop smoke (ou checklist manual documentada).
7. Empacotamento + nota em README/CHANGELOG.
8. Checklists security/frontend.

## 7. Critérios de aceite

- [ ] Auth e isolamento tenant iguais à Web.
- [ ] Round-trip Desktop → API → Web para dataset e dashboard.
- [ ] Logout remove tokens do secure storage.
- [ ] Build reproduzível documentado.
- [ ] Zero marcas terceiras na UI.

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Duas UIs divergentes | Reutilizar `packages/ui` / tokens; publish schema único |
| Malware supply-chain no build | Lockfile, CI assinatura futura |
| Scope “clone MicroStrategy” | MVP estrito da tabela §5 |

## 9. Dependências

015 e 016 (APIs estáveis); 011 modelo dashboard; 001 auth; 010 billing seats.
