# Billing Core

**ID:** TICKET-010  
**Plano detalhado:** [`docs/plans/TICKET-010-billing-core-detailed-plan.md`](../docs/plans/TICKET-010-billing-core-detailed-plan.md)

## Objetivo
Criar planos, limites e vínculo do tenant com pacote.
## Escopo
Base de planos e restrições iniciais.
## Fora de escopo
Cobrança efetiva em gateway.
## Impacto técnico
Backend core, admin.
## Subtarefas
- tabela plans
- vínculo tenant-plan
- limites base
- validação de consumo
- testes mínimos
## Critérios de aceite
Tenant possui plano e limites aplicáveis.
## Riscos
Limites inconsistentes.
## Dependências
Tenant foundation.
