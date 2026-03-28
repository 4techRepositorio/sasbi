# Auth Core

**ID:** TICKET-001  
**Plano detalhado:** [`docs/plans/TICKET-001-auth-core-detailed-plan.md`](../docs/plans/TICKET-001-auth-core-detailed-plan.md)

## Objetivo
Criar login base com email e senha.
## Escopo
Autenticação inicial do usuário.
## Fora de escopo
MFA e recuperação de senha.
## Impacto técnico
Backend, segurança e contratos.
## Subtarefas
- tabela users
- hash de senha
- endpoint login
- sessão/token
- teste básico
## Critérios de aceite
Usuário consegue autenticar com sucesso.
## Riscos
Armazenamento inseguro de credenciais.
## Dependências
Estrutura base do backend.
