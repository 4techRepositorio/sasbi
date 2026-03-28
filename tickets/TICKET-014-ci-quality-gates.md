# CI e quality gates

**ID:** TICKET-014  
**Plano detalhado:** [`docs/plans/TICKET-014-ci-quality-gates-detailed-plan.md`](../docs/plans/TICKET-014-ci-quality-gates-detailed-plan.md)

## Objetivo

Pipeline CI (GitHub/GitLab) com lint/testes API e build Angular obrigatórios em PR.

## Escopo

Workflow YAML, serviços efémeros para testes quando necessário, documentação.

## Fora de escopo

CD produção completo; e2e pesados (estágio 2).

## Impacto técnico

Repositório remoto, DX, qualidade.

## Subtarefas

Ver plano detalhado.

## Critérios de aceite

CI verde obrigatório para merge; falhas reproduzíveis localmente.

## Riscos

Testes flaky ou CI lento.

## Dependências

Repositório Git remoto; suíte de testes mínima.
