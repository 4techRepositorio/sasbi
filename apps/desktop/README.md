# Desktop 4Pro_BI (TICKET-017)

Scaffold de autoração Desktop. A API é a fonte de verdade; o Desktop autentica com os mesmos endpoints (`/auth/login`, refresh, MFA) e publica datasets/dashboards via:

- `POST /api/v1/desktop/publish/dataset`
- `POST /api/v1/desktop/publish/dashboard`

## Arranque (dev)

```bash
cd apps/desktop
cp .env.example .env   # se existir
npm install
npm start
```

Por defeito aponta para `http://127.0.0.1:7418/api/v1`. Tokens devem residir em secure storage do SO (keytar / safeStorage) — o stub em `src/main.js` usa memória de processo apenas para desenvolvimento local.

## Empacotamento

`npm run pack` gera artefactos Electron em `dist/` (CI de packaging completo fica para endurecimento posterior).

## UX

Terminologia nativa **4Pro_BI** — sem marcas de frameworks na interface do utilizador final.
