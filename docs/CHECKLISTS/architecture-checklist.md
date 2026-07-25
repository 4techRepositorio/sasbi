# Checklist de Arquitectura (gate pré-implementação)

Usar em PRs de features novas ou mudanças estruturais. O Architect (ou autor do PR) marca os itens aplicáveis.

## 1. Boundaries

- [ ] Bounded context identificado (ver [BLUEPRINT §7](../architecture/BLUEPRINT.md))
- [ ] Owner Core / Data / Frontend / Platform explícito
- [ ] Sem dependência nova proibida (contracts↛apps, web↛ORM, router↛SQL directo com regra de negócio)

## 2. Multitenancy e segurança

- [ ] `tenant_id` vem do `Principal` / sessão validada
- [ ] Repositórios filtram por tenant
- [ ] Jobs assíncronos transportam contexto suficiente e revalidam no worker
- [ ] Segredos fora do código; upload/validação considerados se houver ficheiros

## 3. Contratos e APIs

- [ ] Impacto em `packages/contracts` documentado (ou “nenhum”)
- [ ] Compatibilidade `/api/v1` preservada; breaking → plano de versão
- [ ] OpenAPI / DTOs alinhados; sem shapes duplicados no backend

## 4. Eventos e filas

- [ ] Se assíncrono: task nomeada, payload mínimo, idempotência considerada
- [ ] Falhas: status `failed` + log técnico + mensagem amigável quando aplicável
- [ ] Reprocessamento previsto se o fluxo for de ingestão

## 5. Observabilidade e qualidade

- [ ] Logs nos pontos de falha e nas transições de estado
- [ ] Teste mínimo (feliz + erro e/ou isolamento tenant)
- [ ] Docs mínimas (`ARCHITECTURE` / blueprint / plano / ticket) actualizadas se a decisão for estrutural

## 6. Trade-offs

- [ ] Alternativas relevantes consideradas (ou N/A)
- [ ] ADR criado/actualizado se a decisão for transversal ou irreversível

## Resultado

| Campo | Valor |
|-------|-------|
| Feature / ticket | |
| Architect review | aprovado / pedido de mudanças |
| Data | |
| Notas | |
