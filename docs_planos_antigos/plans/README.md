# Planos Data_4tech (BI SaaS)

Cada sub-plano é **um ficheiro** → peça: «Executa o sub-plano **Px-yy**» e anexe `docs/plans/sub-planos/Px-yy.md`.

## Instruções e vários agentes

- [INSTRUCOES-USO-DOS-PLANOS.md](INSTRUCOES-USO-DOS-PLANOS.md) — passo a passo, textos prontos para colar no Cursor, ordem e boas práticas
- [PLANO-MULTI-AGENTES.md](PLANO-MULTI-AGENTES.md) — trilhas (Infra, Platform, Portal, Data, Analytics, Ops), dependências e pontos de sincronização S1–S5

## Documentos gerais

- [00-VISAO-E-GOVERNANCA.md](00-VISAO-E-GOVERNANCA.md) — escopo, regras de ouro, marcos A–E, riscos, LGPD, métricas
- [00-STACK-E-FLUXOS.md](00-STACK-E-FLUXOS.md) — tabela de ferramentas, diagrama Mermaid, fluxo ponta a ponta
- [PLANO-MAESTRE-BI-SaaS-Por-Fases.md](PLANO-MAESTRE-BI-SaaS-Por-Fases.md) — cópia monolítica (opcional); preferir ficheiros separados

## Índice de sub-planos (ordem recomendada)

- [P0-01](sub-planos/P0-01.md) — Monorepo e convenções
- [P0-02](sub-planos/P0-02.md) — Postgres e Redis (Compose)
- [P0-03](sub-planos/P0-03.md) — MinIO stage
- [P0-04](sub-planos/P0-04.md) — Keycloak realm e client OIDC
- [P0-05](sub-planos/P0-05.md) — Decisão multitenant Postgres
- [P0-06](sub-planos/P0-06.md) — platform-api esqueleto
- [P0-07](sub-planos/P0-07.md) — CI mínimo
- [P1-01](sub-planos/P1-01.md) — Email verify e reset de senha
- [P1-02](sub-planos/P1-02.md) — MFA (e-mail ou TOTP)
- [P1-03](sub-planos/P1-03.md) — Grupos e claims
- [P1-04](sub-planos/P1-04.md) — Portal OIDC
- [P1-05](sub-planos/P1-05.md) — Whitelabel mínimo
- [P1-06](sub-planos/P1-06.md) — Sincronização metadados tenant/usuário
- [P2-01](sub-planos/P2-01.md) — Upload para MinIO
- [P2-02](sub-planos/P2-02.md) — Modelo ingestões e jobs
- [P2-03](sub-planos/P2-03.md) — Dagster skeleton
- [P2-04](sub-planos/P2-04.md) — Loader CSV/JSON → Bronze
- [P2-05](sub-planos/P2-05.md) — Loader TXT
- [P2-06](sub-planos/P2-06.md) — Loader XLSX
- [P2-07](sub-planos/P2-07.md) — UI histórico ingestões
- [P3-01](sub-planos/P3-01.md) — Projeto dbt camadas
- [P3-02](sub-planos/P3-02.md) — Dagster orquestra dbt
- [P3-03](sub-planos/P3-03.md) — Retenção e purge
- [P3-04](sub-planos/P3-04.md) — Great Expectations mínimo
- [P3-05](sub-planos/P3-05.md) — (Opcional) OpenLineage + Marquez
- [P4-01](sub-planos/P4-01.md) — Cube deploy e conexão
- [P4-02](sub-planos/P4-02.md) — Modelo semântico
- [P4-03](sub-planos/P4-03.md) — Pre-aggregations e Redis
- [P4-04](sub-planos/P4-04.md) — Refresh pós-dbt
- [P5-01](sub-planos/P5-01.md) — Superset e datasource
- [P5-02](sub-planos/P5-02.md) — OIDC Keycloak no Superset
- [P5-03](sub-planos/P5-03.md) — Custom Security Manager multitenant
- [P5-04](sub-planos/P5-04.md) — Embed no portal
- [P5-05](sub-planos/P5-05.md) — Templates
- [P5-06](sub-planos/P5-06.md) — Atualização automática visual
- [P6-01](sub-planos/P6-01.md) — Modelo comercial no Postgres
- [P6-02](sub-planos/P6-02.md) — Kill Bill ou billing interno
- [P6-03](sub-planos/P6-03.md) — Enforcement
- [P6-04](sub-planos/P6-04.md) — UI planos
- [P7-01](sub-planos/P7-01.md) — OTP WhatsApp
- [P7-02](sub-planos/P7-02.md) — Host e TLS por tenant
- [P7-03](sub-planos/P7-03.md) — Tema Keycloak por tenant
- [P8-01](sub-planos/P8-01.md) — Great Expectations ampliado
- [P8-02](sub-planos/P8-02.md) — Performance Cube e Postgres
- [P8-03](sub-planos/P8-03.md) — Auditoria de exportação (LGPD)
- [P8-04](sub-planos/P8-04.md) — Observabilidade