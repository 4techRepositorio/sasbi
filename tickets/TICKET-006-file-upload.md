# Upload de Arquivos

**ID:** TICKET-006  
**Plano detalhado:** [`docs/plans/TICKET-006-file-upload-detailed-plan.md`](../docs/plans/TICKET-006-file-upload-detailed-plan.md)

## Objetivo
Permitir upload inicial de CSV, TXT, XLS, XLSX e JSON.
## Escopo
Upload e armazenamento físico.
## Fora de escopo
Parsing completo.
## Impacto técnico
Backend data, frontend, segurança.
## Subtarefas
- endpoint upload
- validação de tipo
- validação de tamanho
- persistência física
- tela de upload
## Critérios de aceite
Arquivo válido é recebido e armazenado.
## Riscos
Upload de arquivo inválido ou muito grande.
## Dependências
Tenant foundation.
