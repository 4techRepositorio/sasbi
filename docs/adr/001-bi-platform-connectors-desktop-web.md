# ADR-001 — Plataforma BI: conectores, Web e Desktop

**Estado:** aceite (planeamento)  
**Data:** 2026-07-25  
**Decisores:** Architect · Product · Backend Data · Frontend · Security  
**Relacionados:** TICKET-011, TICKET-012, TICKET-015, TICKET-016, TICKET-017; `docs/ARCHITECTURE.md` § Aceleradores

## Contexto

O produto 4Pro_BI já cobre a esteira base (auth, tenant, upload de ficheiros, pipeline, catálogo, billing). A ambição de produto aproxima-se de duas referências de mercado:

| Referência (interna) | Capacidade desejada |
|----------------------|---------------------|
| Ecossistema tipo *Power BI Get Data* | Ingestão com **muitos conectores** (ficheiros, bases, APIs, cloud storage), plugins extensíveis |
| *MicroStrategy* Desktop + Web | **Autoração** rica no Desktop; **consumo, governação e administração** no Web, com o mesmo modelo semântico e catálogo |

Na UX e documentação de utilizador final **não** se usam nomes ou marcas dessas referências — tudo é nativo **4Pro_BI** (`ARCHITECTURE.md` § Aceleradores).

## Decisão

Adoptar arquitectura em **quatro camadas** + clientes **Web e Desktop**, com aceleradores OSS só atrás da fronteira 4Pro_BI.

### 1. Framework de conectores (plugin SPI)

- Contrato estável em `packages/contracts` + implementação em `packages/connectors` (ou `apps/worker` + registry).
- Cada conector implementa: `discover` → `authenticate` → `sample_schema` → `extract` → `normalize_hint`.
- Credenciais por tenant em cofre (encriptação at-rest); nunca no frontend em claro.
- Ingestão por conector entra no mesmo ciclo de estados: `uploaded` | `validating` | `parsing` | `processed` | `failed` (estados novos, se necessários, exigem ADR + migração F1).
- Ficheiro local continua a ser o conector **file** (já existente).

### 2. Camada semântica / consulta

- Catálogo de datasets (TICKET-009) evolui para **modelo semântico** por tenant (dimensões, medidas, relações).
- API de query agregada com **RLS por tenant** e papéis; sem SQL ad-hoc do utilizador final no MVP.
- Acelerador OSS (ex. motor de métricas) permitido **apenas** via BFF/proxy no mesmo domínio, sem cromo externo.

### 3. Cliente Web (autoração leve + consumo)

- Shell Angular existente (`apps/web`): biblioteca de dashboards, visualização, admin, quotas, auditoria.
- ADR TICKET-011 confirma opção **Híbrida (C)**: canvas Angular para KPI/tabela/gráfico simples; motor avançado opcional embutido sob proxy nativo.
- Web é o canal principal de **consumo**, partilha, governação e admin SaaS.

### 4. Cliente Desktop (autoração pesada)

- App **Desktop** (Electron ou Tauri — escolha na implementação de TICKET-017) que:
  - Autentica contra a mesma API (login / refresh / MFA).
  - Configura conectores, modela datasets e monta dossiers/dashboards.
  - Publica artefactos no tenant (sync para a API / object storage).
- Partilha contratos (`packages/contracts`) e, quando possível, componentes de design system (`packages/ui`).
- Offline limitado: rascunhos locais; publicação exige rede + membership válida.

## Alternativas consideradas

| Opção | Motivo de rejeição / diferimento |
|-------|----------------------------------|
| Só Web, sem Desktop | Limita autoração pesada e percepção “enterprise”; Desktop fica fase posterior mas **planeado** |
| Só embed OSS (Superset) como produto | Viola experiência unificada se o cromo externo vazar; alto custo de multitenant |
| Canvas 100% próprio sem motor | Risco de atraso em gráficos avançados; híbrido mitiga |
| Marketplace público de plugins no dia 1 | Fora de escopo; plugins **internos** versionados no monorepo primeiro |

## Consequências

- Novos tickets: **015** (framework + primeiros conectores), **016** (semântica + query + Web BI), **017** (Desktop).
- TICKET-011 permanece o MVP de workspace; 015/016 alinham contratos antes de widgets avançados.
- Billing: cotar conectores activos, volume extraído e seats Desktop (evolução TICKET-010).
- Segurança: cofre de segredos, allowlist de hosts por conector, rate limit, audit de sync/publicação.
- Documentação de produto fala em “Fontes de dados”, “Workspace”, “Desktop 4Pro_BI” — nunca marcas de terceiros.

## Critérios de sucesso (programa)

1. Pelo menos **3 famílias** de conector em produção (ficheiro, SQL, API REST) com o mesmo pipeline de status.
2. Utilizador cria dashboard no Web a partir de dataset processado, isolado por tenant.
3. Desktop autentica, configura uma fonte SQL e publica dataset visível no Web do mesmo tenant.
4. Zero marcas OSS/terceiros na UI do cliente.
