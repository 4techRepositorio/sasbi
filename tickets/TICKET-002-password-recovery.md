# Recuperação de Senha

**ID:** TICKET-002  
**Plano detalhado:** [`docs/plans/TICKET-002-password-recovery-detailed-plan.md`](../docs/plans/TICKET-002-password-recovery-detailed-plan.md)

## Objetivo
Permitir redefinição segura de senha.
## Escopo
Fluxo de solicitação e redefinição.
## Fora de escopo
MFA por aplicativo.
## Impacto técnico
Backend, email, segurança.
## Subtarefas
- gerar token temporário
- expiração de token
- endpoint de solicitação
- endpoint de redefinição
- testes mínimos
## Critérios de aceite
Usuário consegue redefinir a senha com token válido.
## Riscos
Token inseguro ou sem expiração.
## Dependências
Auth core.
