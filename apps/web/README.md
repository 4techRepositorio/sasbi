# 4Pro_BI — Frontend (Angular)

Interface web do produto **4Pro_BI**.

## Desenvolvimento

```bash
npm install
npm start
```

## Build de produção

```bash
npm run build
```

Saída: `dist/fourpro-bi/browser` (usada pelo `Dockerfile`). Produto: **4Pro_BI** (nome npm do projeto: `fourpro-bi`).

## Imagem Docker (`Dockerfile`)

- **`.dockerignore`** — deve excluir `node_modules` e `dist`. Sem isso, `COPY . .` sobrescreve o `npm ci` da camada anterior e o build falha de forma intermitente.
- **`NPM_CONFIG_LEGACY_PEER_DEPS`** — activo no Dockerfile para `npm ci` estável no Node 20 (Alpine) com a cadeia Angular; o `package-lock.json` continua a ser a referência.
