# Tenant Foundation

**ID:** TICKET-004  
**Plano detalhado:** [`docs/plans/TICKET-004-tenant-foundation-detailed-plan.md`](../docs/plans/TICKET-004-tenant-foundation-detailed-plan.md)

## Objetivo
Criar base multitenant do sistema.
## Escopo
Entidade tenant e vínculo com usuários.
## Fora de escopo
Branding avançado.
## Impacto técnico
Backend, segurança, arquitetura.
## Subtarefas
- tabela tenants
- vínculo user-tenant
- contexto de tenant
- filtros por tenant
- testes mínimos
## Critérios de aceite
Usuários acessam apenas dados do próprio tenant.
## Riscos
Vazamento entre tenants.
## Dependências
Auth core.
