# Pacote de Arquitectura — 4Pro_BI

Este directório é a **fonte canónica** do blueprint arquitectónico.
Implementação de features só avança depois de validar alinhamento com estes documentos.

| Documento | Conteúdo |
|-----------|----------|
| [BLUEPRINT.md](./BLUEPRINT.md) | Estrutura, módulos, bounded contexts, entidades, portas, contratos, eventos, filas, APIs, versionamento, trade-offs |
| [../ARCHITECTURE.md](../ARCHITECTURE.md) | Visão operacional (multitenancy, Core vs Data, quotas, aceleradores OSS) |
| [../adr/](../adr/) | Decisões arquitectónicas (ADRs) |
| [../CHECKLISTS/architecture-checklist.md](../CHECKLISTS/architecture-checklist.md) | Gate de validação antes de implementar |

## Ordem de leitura

1. `BLUEPRINT.md` (contexto C4 + regras de dependência)
2. `ARCHITECTURE.md` (multitenancy e ownership Core/Data)
3. ADRs relevantes à feature
4. Checklist de arquitectura no PR

## Regra do Architect

- Nunca implementar feature grande sem plano + boundaries validados.
- Nunca aceitar acoplamento entre bounded contexts (partilha só via contratos/eventos/APIs).
- Toda decisão relevante → ADR numerado + referência no blueprint.
