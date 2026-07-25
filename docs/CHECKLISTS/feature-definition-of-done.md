# Definition of Done
- objetivo atendido
- regras de negócio respeitadas
- tratamento de erro implementado
- logs mínimos incluídos
- testes mínimos criados
- documentação mínima atualizada — checklist [`documentation-checklist.md`](./documentation-checklist.md) (seis perguntas; ADR-004)
- se a feature altera fluxo visível ou arquitetura documentada: diagramas Mermaid em [`docs/diagrams/`](../diagrams/) ou evidência em `docs/assets/` conforme [`docs/assets/README.md`](../assets/README.md)
- se a feature altera API/contratos: regenerar [`docs/openapi/openapi.json`](../openapi/openapi.json) (`./scripts/export-openapi.sh`) e actualizar exemplos se a jornada HTTP pública mudar
