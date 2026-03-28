# Arquitetura

## Blocos

- **Web App** — `apps/web` (Angular 19): portal administrativo, workspace e upload (evolução).
- **API** — `apps/api` (FastAPI): identidade, tenancy, billing, ingestão, catálogo.
- **Worker** — `apps/worker` (Celery + Redis): parsing e jobs assíncronos.
- **PostgreSQL** — dados de aplicativo e, no futuro, camadas analíticas conforme ADR.
- **Redis** — broker/backend Celery e cache (evolução).
- **Armazenamento de objetos** — MinIO em `infra/compose` para stage de arquivos (upload).

## Pacotes

- `packages/contracts` — DTOs Pydantic compartilhados (ex.: auth); espelhar contrato com OpenAPI/TS quando necessário.
- `packages/shared` — utilitários comuns (API + worker).

## Domínios principais

- Identity & Access
- Tenancy
- Billing
- File Upload
- Ingestion
- Dataset Catalog
- Workspace
- Admin

## Estrutura da API (camadas)

- `routers/` — HTTP, validação de entrada, rate limits.
- `services/` — regras de negócio.
- `repositories/` — persistência.
- `models/` — SQLAlchemy.
- `core/` — segurança (hash, JWT).

Migrações: **Alembic** em `apps/api/alembic/`.

## Regra central

Nada cruza **tenant** sem autorização explícita e validada no backend (contexto de tenant após TICKET-004).

## Aceleradores open-source e experiência unificada

O produto pode incorporar **capacidades open-source** (motores analíticos, armazenamento compatível com APIs padrão, filas, bibliotecas de parsing, etc.) para ganhar velocidade de entrega. **Requisito transversal:** na **superfície que o cliente vê** (web, exports, mensagens de erro, URLs do browser, documentação de utilizador), **não aparecem nomes, marcas, “powered by”, logos ou links para projetos externos** — tudo é apresentado como parte da solução 4Pro_BI.

### Padrões de integração (para equipa de implementação)

1. **Transporte e URL** — capacidades expostas via HTTP passam pelo **mesmo domínio** da app (reverse proxy / API gateway / BFF), com caminhos sob o prefixo da aplicação (ex.: `/app/...`, `/api/v1/...`). Evitar redirecionamentos para domínios de terceiros na jornada do utilizador.
2. **Autenticação** — troca de credenciais e emissão de sessão **na nossa API**; tokens de convidado ou equivalentes gerados pelo backend e com tempo de vida curto, **nunca** pedir ao utilizador final credenciais num “segundo login” de outro produto.
3. **UI embedável** — quando existir iframe ou módulo incorporado: tema, tipografia e cores alinhados ao **design system** do `apps/web`; desativar ou ocultar **cromo de produto** (menus de sistema, rodapés de projeto, links de ajuda genéricos) conforme permitido por configuração ou fork mínimo **mantido internamente** — sem expor essa origem ao utilizador.
4. **Bibliotecas em processo** — uso como dependência Python/TS/npm no repositório: sem exportar ao cliente stack traces com namespaces de pacotes reconhecíveis em produção; logs técnicos completos ficam no servidor.
5. **Observabilidade** — métricas e tracing podem usar stacks standard internamente; dashboards operacionais são **internos**, não parte do portal do cliente.

### Onde documentar nomes técnicos

Nomes concretos de projetos OSS usados no **build** e **ops** ficam em ADRs internos, `infra/README`, manifestos e comentários de código quando necessário — **não** em strings i18n, tooltips, emails transacionais nem PDFs entregues ao cliente.

### Diagramas e evidências visuais

Política de geração e armazenamento de imagens para documentação (Mermaid, exports, captures, vs runtime): ver [`docs/assets/README.md`](./assets/README.md).

## Decisões em aberto (ADR futuro)

- Quais **famílias** de componente entram (identidade federada, motor de relatórios, orquestração de transformações, etc.) versus implementação só no monorepo — ver `docs/wireframes/REFERENCIAS-MATERIAIS-LEGADOS.md` como histórico de opções; cada escolha concreta deve referenciar esta secção e cumprir **experiência unificada** acima.
