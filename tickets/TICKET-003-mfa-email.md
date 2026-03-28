# MFA por Email

**ID:** TICKET-003  
**Plano detalhado:** [`docs/plans/TICKET-003-mfa-email-detailed-plan.md`](../docs/plans/TICKET-003-mfa-email-detailed-plan.md)

## Objetivo
Adicionar segundo fator via código por email.
## Escopo
Código temporário e validação.
## Fora de escopo
MFA por app autenticador.
## Impacto técnico
Backend, segurança, email.
## Subtarefas
- gerar código
- armazenar expiração
- enviar por email
- validar código
- testes mínimos
## Critérios de aceite
Login exige código adicional válido.
## Riscos
Códigos previsíveis ou sem expiração.
## Dependências
Auth core.
