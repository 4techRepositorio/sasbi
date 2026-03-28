---
name: create-ingestion-pipeline
description: Cria pipeline de ingestão para arquivos
---

Fluxo obrigatório:
1. upload físico
2. registro metadata
3. validação
4. parsing
5. normalização
6. persistência
7. catálogo
8. logs
9. status final

Sempre prever:
- tenant_id
- tipo de arquivo
- tamanho
- status
- mensagem técnica
- mensagem amigável
