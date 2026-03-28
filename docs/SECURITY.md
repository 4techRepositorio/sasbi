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

## Ponto de entrada na raiz do repositório

O ficheiro [SECURITY.md](../SECURITY.md) na raiz existe para o GitHub mostrar a *Security policy* e remete a este documento.
