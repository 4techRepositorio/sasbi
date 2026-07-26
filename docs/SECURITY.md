# Segurança (4Pro_BI)

Documento único: **reporte de vulnerabilidades**, **divulgação responsável** e **controlos obrigatórios** na implementação (alinhado a `.cursor/rules/06-security.mdc`).

## Reportar vulnerabilidades

Se descobrir uma vulnerabilidade de segurança no **4Pro_BI**, contacte os mantenedores por um **canal privado** (por exemplo, *Security advisories* do GitHub no repositório, se estiver activo, ou email acordado pela equipa).

**Não** abra um issue público com detalhes exploráveis antes de existir correcção ou plano acordado.

## Âmbito

- API, worker, frontend, infraestrutura e dependências incluídas neste monorepo.
- Configuração e segredos: nunca os commite; use variáveis de ambiente e gestão de secrets do ambiente de deploy.

## Divulgação responsável

Agradecemos a divulgação coordenada para permitir análise e patch antes de divulgação pública.

## Controlos obrigatórios na implementação

- Hash de senha seguro
- MFA onde o fluxo de autenticação o preveja
- Reset de senha com token com expiração
- Rate limiting em login (e noutros endpoints sensíveis conforme desenho)
- Audit log para acções críticas
- Segredos fora do código
- Validação de upload (tipo/conteúdo)
- Limite por tipo e tamanho de ficheiro
- Isolamento por tenant: não confiar em `tenant_id` vindo só do cliente sem validação de sessão

## Observabilidade e retenção (TICKET-013)

- Toda a resposta HTTP inclui `X-Request-ID` (UUID). O mesmo ID propaga-se para tasks Celery de parse/sync e para `audit_log.correlation_id` / `file_ingestions.correlation_id`.
- Métricas operacionais: `GET /api/v1/metrics` (formato Prometheus; não expor no portal do cliente sem autenticação de edge).
- Logs estruturados JSON quando `LOG_JSON=true` (campo `correlation_id`).
- **Retenção recomendada:** logs de aplicação 30 dias; `audit_log` 365 dias (ou até encerramento do tenant); samples de métricas 90 dias. Amostragem só para eventos não críticos — acções de auth, upload, sync e dashboards são sempre persistidas.

## Cofre de conectores (TICKET-015)

- Segredos em `connector_credentials.secret_encrypted` (Fernet; chave `CREDENTIALS_FERNET_KEY` ou derivada de `JWT_SECRET` em desenvolvimento).
- Respostas de listagem/detalhe de fontes **nunca** incluem o segredo — apenas `has_secret`.
- REST JSON: allowlist de hosts; bloqueio de IPs privados por defeito.

## Ponto de entrada na raiz do repositório

O ficheiro [SECURITY.md](../SECURITY.md) na raiz existe para o GitHub mostrar a *Security policy* e remete a este documento.
