# Validação de wireframe — Admin e Identidade

**Versão:** 0.2  
**Escopo de produto:** login, MFA (ticket), recuperação de senha, administração de usuários e grupos, indicação clara do tenant atual.

## 0. Evidências visuais (exports)

Colocar capturas ou exports em [`docs/assets/wireframes/exports/`](../assets/wireframes/exports/) e referenciar aqui.

| Sugestão de ficheiro | Conteúdo |
|----------------------|----------|
| `identity-login-v1-YYYYMMDD.png` | Ecrã `/login` (passo email/senha) |
| `identity-mfa-v1-YYYYMMDD.png` | Mesmo ecrã, passo código MFA |
| `identity-forgot-v1-YYYYMMDD.png` | `/forgot-password` |
| `identity-reset-v1-YYYYMMDD.png` | `/reset-password` |
| `identity-admin-users-v1-YYYYMMDD.png` | *Quando existir UI de admin de utilizadores* |

*Exemplo de referência no markdown (quando o ficheiro existir):*  
`![Login](../assets/wireframes/exports/identity-login-v1-20260327.png)`

## 0.1 Mapeamento — implementação atual (`apps/web`)

| Bloco | Rotas / componente | Cobertura MVP |
|-------|-------------------|---------------|
| Login L1–L5 | `/login` → `LoginComponent` | Sim |
| MFA M1–M3 | `/login` (passo interno `mfa`) | Parcial: reenvio/throttle M2 a validar na UI |
| Reset R1–R3 | `/forgot-password`, `/reset-password` | Sim |
| Admin A1–A4 | — | **Não** há ecrã dedicado de gestão de utilizadores/grupos; tenant visível na sidebar do shell (`ShellComponent`) |

## 1. Objetivo da validação

Garantir que as telas de identidade e administração cubram estados obrigatórios (loading, erro, vazio, sucesso), não expõem diferenças semânticas que permitam enumeração de contas, e deixam explícito **qual tenant** está ativo em contexto administrativo.

## 2. Telas / blocos

### 2.1 Login (TICKET-001)

| # | Elemento / comportamento | Critério de aceite |
|---|---------------------------|--------------------|
| L1 | Campos email, senha | Validação client-side mínima; servidor é fonte da verdade |
| L2 | Erro de credenciais | Mensagem genérica (“Credenciais inválidas”) |
| L3 | Loading | Desabilitar submit durante requisição |
| L4 | Sucesso | Redirecionar para shell da aplicação ou passo MFA (TICKET-003) |
| L5 | Rate limit | Mensagem amigável + opcional tempo de espera |

### 2.2 MFA por email (TICKET-003) — wireframe lógico

| # | Comportamento | Critério |
|---|---------------|----------|
| M1 | Após login, se MFA exigido | Tela de código; sem dados sensíveis na URL |
| M2 | Reenvio de código | Throttle visível; confirmação sem revelar email completo |
| M3 | Código expirado | Mensagem clara; fluxo para solicitar novo |

### 2.3 Recuperação de senha (TICKET-002)

| # | Comportamento | Critério |
|---|---------------|----------|
| R1 | Solicitar reset | Confirmação única (“Se existir conta, enviaremos email”) |
| R2 | Link com token | Tela nova senha; token inválido/expirado tratado |
| R3 | Pós-sucesso | Login; sem auto-login por padrão (decisão de produto a validar) |

### 2.4 Admin — usuários e grupos (TICKET-005 + tenant)

| # | Comportamento | Critério |
|---|---------------|----------|
| A1 | Cabeçalho | Nome/slug do **tenant atual** sempre visível |
| A2 | Lista usuários | Vazia: CTA para convite/cadastro conforme política |
| A3 | Papéis | Diferença visual admin vs consumidor; ações condicionadas |
| A4 | Erro de permissão | 403 com explicação e sem vazar dados de outro tenant |

## 3. Riscos de UX/segurança

- Indicar “email não cadastrado” no login → **rejeitar** no wireframe final.  
- MFA: código em banner/notificação persistente → evitar vazamento em screenshots.  
- Admin global vs tenant: se existir super-admin futuro, wireframe deve separar contextos visualmente (cor, label).

## 4. Sign-off

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| UX/CS | | | |
| Security | | | |
| Frontend | | | |
