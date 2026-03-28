## O quê

Descreva a alteração em 1–3 frases.

## Tipo

- [ ] Correção
- [ ] Funcionalidade
- [ ] Documentação / apenas CI
- [ ] Infra / Docker / Portainer

## Checklist (marque o que aplicar)

- [ ] Gates locais: `make qa` ou `./scripts/run-qa-gates.sh`
- [ ] Opcional: `make qa-optional` ou E2E (`e2e/README.md`) se o PR mexe em fluxos web/API integrados
- [ ] Migrações Alembic aplicadas / job `alembic-postgres` verde se mudou `alembic/versions/`
- [ ] Contratos `packages/contracts` revistos se alterados (impacto em API/web)
- [ ] Isolamento por tenant e RBAC considerados
- [ ] `docs/CHECKLISTS/` actualizados se a entrega o exigir

## Riscos e deploy

Notas para revisão (breaking changes, variáveis novas, ordem de migrate vs deploy).
