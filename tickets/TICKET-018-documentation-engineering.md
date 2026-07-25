# TICKET-018 — Documentation Engineering

## Objetivo

Completar a documentação técnica do monorepo 4Pro_BI para que nenhuma área crítica fique sem resposta a: o que faz, como funciona, como instalar, configurar, testar e evoluir.

## Escopo

- Índice unificado em `docs/README.md` e ligações no `README.md` raiz
- Guias: instalação, deploy, desenvolvimento
- OpenAPI/Swagger versionado + instruções de uso
- Exemplos HTTP/cURL
- Diagramas Mermaid (fluxos, sequência, UML de componentes/classes)
- ADR de padrões de documentação
- Checklist de documentação e DoD actualizado
- Changelog e roadmap alinhados

## Fora de escopo

- Alterações de comportamento da API ou UI
- Geração automática contínua de PNG a partir de Mermaid (política opcional futura)
- Documentação de utilizador final (portal do cliente)

## Impacto técnico

- **Backend / frontend / dados / billing:** nenhum comportamento novo
- **Segurança:** exemplos não devem incluir segredos reais; usar valores de `.env.example`
- **Contratos:** OpenAPI espelha contratos existentes; alterações futuras exigem regenerar schema

## Subtarefas

1. ADR-002 padrões de documentação
2. Guias INSTALLATION / DEPLOYMENT / DEVELOPMENT
3. Pasta `docs/openapi/` + script de export
4. Pasta `docs/examples/`
5. Pasta `docs/diagrams/` (Mermaid + UML)
6. Checklist + índices + CHANGELOG/ROADMAP

## Critérios de aceite

- [ ] Toda documentação nova responde às 6 perguntas canónicas
- [ ] OpenAPI exportável e documentado (`/docs`, `/redoc`, ficheiro em `docs/openapi/`)
- [ ] Exemplos cobrem auth + upload/ingestão + contexto
- [ ] Diagramas cobrem contexto do sistema, auth, ingestão e componentes
- [ ] Índices actualizados; ticket e changelog reflectem a entrega

## Riscos

- Schema OpenAPI estático pode ficar desactualizado face ao código — mitigação: script de export + nota no DoD
- Duplicação com READMEs de infra — mitigação: guias apontam para fontes canónicas

## Dependências

- API FastAPI com schema OpenAPI nativo
- Conteúdo existente em `docs/ARCHITECTURE.md`, `infra/portainer/README.md`, `CONTRIBUTING.md`
