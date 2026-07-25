# Checklist — documentação

Usar em PRs que alterem comportamento, contratos, infra ou fluxos.

## Seis perguntas (obrigatório no doc afectado)

- [ ] O que faz
- [ ] Como funciona
- [ ] Como instalar
- [ ] Como configurar
- [ ] Como testar
- [ ] Como evoluir

## Artefactos

- [ ] `README` / índice (`docs/README.md` ou README do módulo) actualizado se houver entrada nova
- [ ] Arquitectura (`docs/ARCHITECTURE.md`) se mudou boundary ou domínio
- [ ] Diagrama Mermaid em `docs/diagrams/` (ou secção existente) se mudou fluxo
- [ ] ADR em `docs/adr/` se foi decisão arquitectural
- [ ] OpenAPI regenerado (`./scripts/export-openapi.sh`) se mudou API/contratos
- [ ] Exemplos em `docs/examples/` se mudou jornada HTTP pública
- [ ] Guias install/deploy/dev se mudou pré-requisito, variável ou processo
- [ ] `CHANGELOG.md` (secção Unreleased)
- [ ] Roadmap/ticket se mudou compromisso de fase

## Qualidade

- [ ] Sem segredos reais; valores de exemplo alinhados a `.env.example`
- [ ] Sem marcas OSS na documentação de utilizador final (ops/ADR ok)
- [ ] Links relativos válidos a partir do ficheiro novo

Referência: [ADR-002](../adr/002-documentation-standards.md).
