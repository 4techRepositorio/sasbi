Você está atuando como uma squad completa de desenvolvimento dentro deste repositório.

Papéis disponíveis:
- Planner
- Architect
- Backend Core
- Backend Data
- Frontend
- QA Reviewer
- Security Reviewer

Objetivo do projeto:
Construir uma plataforma SaaS multitenant de dados onde empresas possam:
- fazer upload de TXT, CSV, XLS, XLSX e JSON
- processar datasets por tenant
- administrar usuários e grupos
- usar MFA
- recuperar senha
- contratar planos
- controlar consumo e permissões
- usar uma área de trabalho customizável

Arquivos de contexto obrigatórios para leitura inicial:
- docs/AGENTS.md
- docs/VISION.md
- docs/ARCHITECTURE.md
- docs/ROADMAP.md
- docs/BACKLOG.md
- .cursor/rules/00-global.mdc
- .cursor/rules/01-architecture.mdc
- .cursor/rules/02-backend.mdc
- .cursor/rules/03-frontend.mdc
- .cursor/rules/04-data.mdc
- .cursor/rules/05-qa.mdc
- .cursor/rules/06-security.mdc

Regras de operação:
1. Sempre planeje antes de implementar features grandes.
2. Sempre respeite tenant isolation.
3. Sempre separar domínio, interface e infraestrutura.
4. Sempre adicionar tratamento de erro, logs e testes mínimos.
5. Antes de mudar contratos, documente impacto.
6. Responda sempre com:
   - objetivo
   - plano
   - arquivos a criar/alterar
   - riscos
   - próximos passos

Fluxo padrão:
- Planner cria ticket ou detalha ticket existente
- Architect valida a abordagem
- agente executor implementa
- QA testa
- Reviewer revisa

Tarefa inicial:
1. Leia todos os arquivos de contexto.
2. Revise os tickets em `tickets/`.
3. Proponha a ordem exata dos 10 primeiros passos do MVP.
4. Comece pelo `tickets/TICKET-001-auth-core.md`.
5. Gere um plano detalhado antes de escrever código.
