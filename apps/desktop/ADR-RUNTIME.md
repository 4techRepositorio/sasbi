# ADR — Runtime do cliente Desktop 4Pro_BI

**ID:** ADR-002 (local ao app; espelho em `docs/adr/002-desktop-runtime.md`)  
**Estado:** aceite  
**Data:** 2026-07-25  
**Ticket:** TICKET-017  
**Relacionados:** ADR-001 (`docs/adr/001-bi-platform-connectors-desktop-web.md`)

## Contexto

O programa BI exige um cliente Desktop de autoração (fontes, datasets, dashboards)
que autentica na mesma API FastAPI, publica artefactos no tenant e partilha contratos
TypeScript/Pydantic com o resto do monorepo. Duas opções de runtime foram avaliadas:

| Opção | Prós | Contras |
|-------|------|---------|
| **Electron** | Ecossistema maduro; UI React/TS no renderer; IPC e `safeStorage` nativos; alinhado a tooling Vite já familiar | Binário mais pesado; Chromium embutido |
| **Tauri** | Binário leve; bom isolamento Rust | Curva Rust; menos reutilização directa de componentes TS/React do ecossistema web interno |

## Decisão

**Adoptar Electron + Vite + TypeScript** para o MVP de `apps/desktop`.

Motivos principais:

1. **Reutilização de TypeScript** — tipos alinhados a `packages/contracts`, cliente HTTP e UI
   React só no Desktop (o Web permanece Angular).
2. **Secure storage** — `electron.safeStorage` cobre encriptação de tokens ao nível do SO
   sem depender de plugins externos no MVP.
3. **Velocidade de entrega** — scaffold Vite + React reduz risco de atraso no round-trip
   Desktop → API → Web exigido pelos critérios de aceite.

**OS prioritário inicial:** Linux (AppImage/deb) e Windows (NSIS), documentados no README.
macOS fica fase 2 (assinatura/notarização).

## Consequências

- `apps/desktop` usa React **apenas** neste app; não introduz React em `apps/web`.
- Empacotamento via `electron-builder`; CI pode precisar de `xvfb-run` em runners headless.
- Tokens nunca em `localStorage` do renderer em claro — apenas via IPC + `safeStorage`.
- Revisão futura (pós-MVP): avaliar Tauri se o peso do binário ou a superfície Chromium
  se tornarem risco operacional relevante.

## Alternativas rejeitadas / diferidas

- **Tauri no MVP** — diferido; reavaliar após estabilizar fluxos 015/016/017.
- **App nativa C#/Swift** — fora do stack do monorepo e do objectivo de reuso TS.
