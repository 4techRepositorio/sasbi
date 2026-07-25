# Packaging CI — 4Pro_BI Desktop (opcional)

Job stub para empacotar o Desktop. **Não** está activo no `ci.yml` principal para evitar
downloads pesados do Electron em todos os PRs. Activar manualmente ou em tags `desktop-v*`.

Requisitos em runners Linux: `xvfb` para builds que arrancam o binário Electron.

```yaml
# .github/workflows/desktop-pack.yml  (exemplo — não commitado activo)
#
# name: Desktop pack
# on:
#   workflow_dispatch: {}
#   push:
#     tags: ["desktop-v*"]
# jobs:
#   pack-linux:
#     runs-on: ubuntu-latest
#     defaults:
#       run:
#         working-directory: apps/desktop
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-node@v4
#         with:
#           node-version: "22"
#           cache: npm
#           cache-dependency-path: apps/desktop/package-lock.json
#       - name: Install xvfb
#         run: sudo apt-get update && sudo apt-get install -y xvfb
#       - name: npm ci
#         run: npm ci
#       - name: Build + pack
#         run: xvfb-run -a npm run pack
#         env:
#           VITE_API_BASE_URL: http://127.0.0.1:7418
#       - uses: actions/upload-artifact@v4
#         with:
#           name: fourpro-bi-desktop-linux
#           path: apps/desktop/release/**
```

Assinatura de código (Windows/macOS) e secrets de notarização ficam **fora** do repositório.
