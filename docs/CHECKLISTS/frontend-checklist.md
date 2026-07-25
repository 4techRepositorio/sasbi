# Frontend Checklist

## Estados e UX
- tela criada
- loading tratado
- erro tratado
- estado vazio tratado
- sucesso tratado (feedback claro)
- responsividade básica validada

## Arquitectura (Frontend Architect)
- organização Feature-First (código na feature correcta; rota thin)
- Atomic Design respeitado; sem duplicar componentes existentes
- props tipadas em todo componente novo/alterado
- documentação (JSDoc) + exemplo de uso (`@example` ou story)
- teste mínimo do componente ou ecrã (unitário quando runner existir; e2e para fluxo crítico)
- Client Components / lógica de browser só onde necessário (stack Next); no Angular, evitar lógica de domínio no template
- lazy loading / code splitting para features pesadas (`loadComponent` / `dynamic`)
- ecrã admin mostra tenant actual
- referência de reutilização Angular: `app-storage-quota-block` (`shared/storage-quota-block.component.ts`)
- ver [docs/FRONTEND_ARCHITECTURE.md](../FRONTEND_ARCHITECTURE.md) (diretrizes completas) e skill `frontend-architect`

## Entregas actuais (`apps/web` Angular)
- área admin (Equipa / tenant-users): só visível a `admin`; consome `GET /api/v1/tenant/members`
- shell: tenant e papel visíveis; quando `plan` existe em `/me/context`, mostrar resumo do pacote (limite de uploads)
- shell e upload: quando `storage` existe em `/me/context`, mostrar uso vs limite (tenant; opcional utilizador e grupo); após upload bem-sucedido, recarregar contexto para actualizar barras
- dashboard: cartão «Pacote ativo» e «Utilização de armazenamento» quando `plan` / `storage` vêm do contexto; ao abrir o dashboard, pedir `tenantCtx.load()` em paralelo aos dados para actualizar quotas
- scripts `npm run build` / `start` usam a CLI Angular via `node node_modules/@angular/cli/bin/ng.js` (PATH sem `ng` global)
- quotas de armazenamento: componente partilhado `app-storage-quota-block` (`shared/storage-quota-block.component.ts`) na shell, upload e dashboard — evitar duplicar markup; import barrel `shared/index.ts`; aviso visual ≥90 % (`STORAGE_QUOTA_WARN_PERCENT` em `core/storage-usage.ts`) para tenant, utilizador e grupo; barras compactas para sub-quotas (utilizador / grupo)
- E2E `data-storage-warn`: scripts seed/cleanup; proxy CI `apps/web/proxy.conf.e2e-storage-warn.json` (API porta 8765); workflows `e2e-seed-storage-dispatch.yml` e `e2e-storage-warn-browser-dispatch.yml` (ver `e2e/README.md`)
- wireframe PDF: após alterar `Data Analytics Solution.pdf`, opcionalmente correr `bash scripts/export-wireframes-from-pdf.sh` e referenciar evidências em `docs/wireframes/validation-*.md` / `docs/assets/wireframes/exports/`
