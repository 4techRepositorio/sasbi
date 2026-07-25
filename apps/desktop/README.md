# 4Pro_BI Desktop

Cliente Desktop de autoração (TICKET-017) — **Electron + Vite + TypeScript + React**.

Decisão de runtime: [`ADR-RUNTIME.md`](./ADR-RUNTIME.md) (Electron escolhido para reutilização TypeScript).

React é usado **apenas** neste app; o portal Web permanece Angular (`apps/web`).

## Pré-requisitos

- Node.js ≥ 20
- API 4Pro_BI a correr (por omissão `http://127.0.0.1:7418`)
- Em CI Linux headless: `xvfb-run` para arrancar o Electron (ver abaixo)

## Configuração

```bash
cp .env.example .env
# edite VITE_API_BASE_URL se a API não estiver em 127.0.0.1:7418
```

| Variável | Default | Descrição |
|----------|---------|-----------|
| `VITE_API_BASE_URL` | `http://127.0.0.1:7418` | Base da API (sem barra final) |

**Não** coloque segredos (JWT, passwords) no repositório. Tokens de sessão ficam no processo principal via `electron.safeStorage`.

## Comandos

```bash
cd apps/desktop
npm install
npm run dev          # Vite :5179 + Electron
npm run build        # dist/ (renderer) + dist-electron/ (main/preload)
npm test             # vitest (cliente HTTP / auth helpers)
npm run typecheck
```

Produção local (após `npm run build`):

```bash
npm start            # electron .
```

Empacotamento (opcional, `electron-builder`):

```bash
npm run pack         # pasta unpackaged em release/
npm run dist         # instaladores (Linux AppImage/deb, Windows NSIS)
```

### CI / headless

Se o runner não tiver display:

```bash
xvfb-run -a npm run pack
# ou só para smoke do processo:
xvfb-run -a npm start
```

O job de packaging no GitHub Actions está documentado (comentado) em [`docs/packaging-ci.md`](./docs/packaging-ci.md).

## Funcionalidades MVP

1. **Auth** — login `POST /api/v1/auth/login`; MFA `POST /api/v1/auth/mfa/verify`; refresh automático; logout limpa `safeStorage`; tenant activo na barra lateral.
2. **Sessão** — `GET /api/v1/desktop/session` com fallback para `GET /api/v1/me/context`.
3. **Fontes de dados** — catálogo `GET /api/v1/connectors`; configurar Postgres / REST; testar; gravar; sync `POST .../sync`; publicar dataset `POST /api/v1/desktop/publish-dataset`.
4. **Dashboard** — widgets KPI/tabela; publicar `POST /api/v1/desktop/publish-dashboard`.

Enquanto as rotas 015/017 ainda não existirem no backend, a UI degrada com mensagens claras (catálogo local MVP para postgres/REST; erros amigáveis).

## Estrutura

```
apps/desktop/
  ADR-RUNTIME.md
  electron/          # main, preload, safeStorage
  src/
    api/             # cliente HTTP + tipos (contratos)
    auth/            # AuthProvider + token IPC
    views/           # login, fontes, dashboard, sessão
    styles/
  tests/
  docs/packaging-ci.md
```

## Segurança

- `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`
- Tokens só via IPC; renderer nunca escreve tokens em `localStorage`
- CSP restritiva no `index.html`
- Credenciais de conectores enviadas só no body autenticado para a API (cofre no servidor)

## UI

Interface em **português**, marca **4Pro_BI Desktop**, aspecto corporativo nativo — sem nomes de stacks OSS na superfície do utilizador.
