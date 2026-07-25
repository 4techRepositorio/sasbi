# Desktop 4Pro_BI — autoração e publicação

**ID:** TICKET-017  
**Plano detalhado:** [`docs/plans/TICKET-017-desktop-authoring-detailed-plan.md`](../docs/plans/TICKET-017-desktop-authoring-detailed-plan.md)  
**ADR:** [`docs/adr/001-bi-platform-connectors-desktop-web.md`](../docs/adr/001-bi-platform-connectors-desktop-web.md)  
**Plano mestre:** [`docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](../docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md)

## Objetivo

Entregar cliente Desktop para autoração pesada (fontes, modelagem, dashboards) com autenticação na mesma API, publicação de artefactos no tenant e consumo posterior no Web — dualidade Desktop/Web nativa 4Pro_BI.

## Escopo

- Scaffold `apps/desktop` (Electron **ou** Tauri — decisão no plano detalhado / spike)
- Auth: login, refresh, MFA; tenant activo visível
- Fluxos: configurar conector O1 → sample → publish dataset; autorar dashboard → publish
- Rascunhos locais limitados; sync com API
- Empacotamento CI mínimo (artefacto por OS prioritário)

## Fora de escopo

- Paridade total com Web admin/billing
- Offline completo / peer-to-peer
- Loja de plugins no Desktop
- iOS/Android

## Impacto técnico

Novo app no monorepo; contratos `desktop_sync`; segurança (secure storage de tokens); billing seats; docs de instalação.

## Subtarefas

Ver plano detalhado.

## Critérios de aceite

- Utilizador autentica no Desktop e opera só no tenant do JWT.
- Dataset publicado no Desktop aparece no catálogo Web do mesmo tenant.
- Dashboard publicado é visível no Web (read).
- Tokens não ficam em logs; logout limpa secure storage.

## Riscos

Duplicação de UI Web/Desktop; superfície de ataque do cliente grosso; custo de build multi-OS.

## Dependências

TICKET-015, 016 (APIs); 001 auth; 011 modelo de dashboard; 010 seats Desktop.
