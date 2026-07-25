# ADR-002 — Runtime Desktop (Electron)

**Estado:** aceite  
**Data:** 2026-07-25  
**Ticket:** TICKET-017  

Documento canónico no app: [`apps/desktop/ADR-RUNTIME.md`](../../apps/desktop/ADR-RUNTIME.md).

## Decisão (resumo)

**Electron + Vite + TypeScript** para o cliente Desktop 4Pro_BI, priorizando reutilização de TypeScript (contratos, cliente HTTP, UI React só em `apps/desktop`). O Web permanece Angular.

Tokens de sessão em `electron.safeStorage` via IPC; OS prioritários: Linux e Windows.
