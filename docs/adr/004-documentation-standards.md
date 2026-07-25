# ADR-004 — Padrões de documentação técnica

## Estado

Aceite

## Contexto

O monorepo 4Pro_BI acumulava documentação útil (arquitectura, planos, wireframes) mas sem guias canónicos de instalação/deploy/desenvolvimento, sem OpenAPI versionado no Git, sem exemplos HTTP nem pasta de diagramas UML/Mermaid indexada. A regra do produto exige que nenhuma feature grande exista sem documentação mínima.

**Nota de numeração:** no ramo de origem esta decisão foi redigida como ADR-002; no `main` o número **002** ficou com a stack frontend React/Next. Renumerada para **004** no merge. **ADR-003** permanece reservado ao runtime Desktop (TICKET-017).

## Decisão

1. **Documentação como entrega** — toda feature que altere API, dados, auth, billing ou fluxo visível actualiza documentação no mesmo PR (ou PR irmão imediato).
2. **Seis perguntas obrigatórias** em cada guia/documento de domínio:
   - O que faz
   - Como funciona
   - Como instalar
   - Como configurar
   - Como testar
   - Como evoluir
3. **Fontes canónicas**
   - Arquitectura: `docs/ARCHITECTURE.md`
   - Instalação: `docs/INSTALLATION.md`
   - Deploy: `docs/DEPLOYMENT.md`
   - Desenvolvimento: `docs/DEVELOPMENT.md`
   - API HTTP: OpenAPI em runtime (`/docs`, `/redoc`, `/openapi.json`) + snapshot em `docs/openapi/`
   - Exemplos: `docs/examples/`
   - Diagramas: `docs/diagrams/` (Mermaid no Markdown; PNG opcional em `docs/assets/diagrams/exports/`)
   - ADRs: `docs/adr/`
4. **OpenAPI** — regenerar o snapshot com `scripts/export-openapi.sh` quando routers/contratos mudarem; o schema no Git é a referência para review e clientes offline.
5. **UX nativa** — documentação de utilizador final e strings da UI não citam marcas OSS externas (ver `docs/ARCHITECTURE.md` § Aceleradores). Nomes técnicos de libs ficam em ADRs/ops.
6. **ADR numeração** — decisões arquitecturais relevantes recebem ADR sequencial; runtime Desktop (Electron vs Tauri) fica reservado a **ADR-003** após spike TICKET-017; stack frontend alvo é **ADR-002**.

## Consequências

- DoD e checklist de documentação passam a bloquear “código sem docs”.
- READMEs de app/infra permanecem curtos e apontam para os guias canónicos (evitar duplicação divergente).
- Risco de schema OpenAPI desactualizado mitigado pelo script + checklist em PRs de API.

## Alternativas rejeitadas

- Documentar só em wiki externa — perde revisão em PR e versionamento com o código.
- Gerar apenas `/docs` em runtime sem snapshot — dificulta review offline e diff de contratos.
