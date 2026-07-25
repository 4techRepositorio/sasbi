---
name: create-feature-plan
description: Cria um plano estruturado para uma nova feature
---

Quando receber uma nova feature:
0. Se não houver briefing de produto (problema, quem, valor, medição), acionar primeiro a skill `product-designer` e/ou exigir `docs/product/<slug>.md`.
1. Resuma o objetivo em 1 parágrafo (ligado ao valor de negócio).
2. Liste regras de negócio.
3. Liste impacto em:
   - backend
   - frontend
   - dados
   - segurança
   - billing
4. Quebre em subtarefas.
5. Defina critérios de aceite.
6. Gere um arquivo em tickets/ com o padrão:
   TICKET-XXX-nome-da-feature.md

Template:
# Título
## Objetivo
## Escopo
## Fora de escopo
## Impacto técnico
## Subtarefas
## Critérios de aceite
## Riscos
## Dependências

Se a feature for uma tarefa complexa com estágios, filas, retries ou paralelismo,
carregar também a skill `ai-workflow-designer` (pipeline Entrada→Entrega + bounds).
