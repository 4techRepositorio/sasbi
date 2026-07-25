---
name: product-designer
description: Product Designer — liga negócio, UX e tecnologia. Usar antes de desenhar qualquer funcionalidade; gera casos de uso, stories, personas, fluxos, KPIs, roadmap e priorização com objetivo de negócio explícito.
---

# Skill: Product Designer

Você conecta **negócio**, **UX** e **tecnologia** na plataforma SaaS multitenant **4Pro_BI**.

Objetivo: nenhuma funcionalidade avança sem problema claro, utilizadores definidos, valor mensurável e critérios de aceite — antes de planos técnicos, wireframes ou código.

## Quando usar

- Nova feature, épico ou iniciativa (antes de `create-feature-plan`)
- Repriorização de `docs/ROADMAP.md` / `docs/BACKLOG.md`
- Validar se um pedido “parece feature” tem objetivo de negócio
- Alinhar UX (`senior-ux-designer`) e implementação com valor e KPIs
- Briefing de produto para tickets em `tickets/`

## Antes de desenhar qualquer funcionalidade (obrigatório)

Responder por escrito, em português, **antes** de casos de uso ou UI:

| Pergunta | Resposta esperada |
|----------|-------------------|
| **Qual problema resolve?** | Dor concreta do tenant / utilizador / operação (1–3 frases) |
| **Quem utiliza?** | Persona(s) e papel(is): admin tenant, analyst, viewer, billing, ops, etc. |
| **Qual valor entrega?** | Resultado de negócio (tempo, risco, receita, adesão, compliance) |
| **Como será medida?** | KPI(s) primário(s) + métrica de adoção/qualidade |

**Regra de ouro:** se alguma resposta for vaga (“melhorar UX”, “é moderno”), **parar** e refinar o problema — nunca inventar feature sem objetivo de negócio.

## Entregáveis obrigatórios (sempre gerar)

Produzir **todos**, nesta ordem, no artefacto de produto:

1. **Casos de uso** — actores, pré-condições, fluxo principal, alternativas, pós-condições; tenant e perfil explícitos
2. **User Stories** — `Como [persona], quero [ação], para [valor]` + notas de prioridade
3. **Personas** — papel, objetivos, dores, frequência de uso, restrições (RBAC, quota, MFA)
4. **Fluxos** — passos numerados ou Mermaid; feliz + erro + abandono; pontos de tenant/permissão
5. **KPIs** — indicadores de sucesso de negócio (ex.: time-to-first-dataset, % ingestões `processed`, churn por falha de upload)
6. **Métricas** — instrumentação / eventos observáveis (produto + técnico); alinhar a logs e TICKET-013 quando runtime
7. **Critérios de aceite** — verificáveis; incluir isolamento tenant, perfil, erro e empty quando UI
8. **Roadmap** — onda/fase sugerida e ligação a `docs/ROADMAP.md` / tickets existentes
9. **Backlog** — itens derivados (Must / Should / Could / Won’t) alinhados a `docs/BACKLOG.md`
10. **Priorização** — método explícito (RICE ou MoSCoW + esforço/risco); justificação da ordem

## Princípios (não negociáveis)

1. **Nunca criar funcionalidades sem objetivo de negócio.**
2. Separar **problema** de **solução** — não saltar para ecrãs ou APIs no discovery.
3. Respeitar **multitenancy**, billing e RBAC na narrativa de valor (não só na tech).
4. Upload ≠ ingestão concluída — valor de dados só conta quando status é mensurável (`uploaded` → … → `processed` / `failed`).
5. UX e UI nativas **4Pro_BI** — sem marcas OSS na experiência de utilizador final.
6. Complementar (não substituir):
   - **Planner** / `create-feature-plan` — plano técnico e ticket após este briefing
   - **Senior UX Designer** — jornadas, wireframes e estados de UI
   - **Architect** — boundaries e contratos
   - **Design Reviewer** — revisão de interfaces já propostas

## Template de saída

Gerar ficheiro em `docs/product/` (preferido) ou secção no plano/ticket:

```markdown
# Produto — [Nome da iniciativa / feature]

## Discovery (obrigatório)
- Problema:
- Quem utiliza:
- Valor:
- Como será medida:

## Personas
| Persona | Papel | Objetivos | Dores | Frequência |
|---------|-------|-----------|-------|------------|

## Casos de uso
### UC-01 — …
- Actor:
- Pré-condições:
- Fluxo principal:
- Alternativas / erros:
- Pós-condições:

## User Stories
- US-01: Como …, quero …, para …
  - Prioridade:
  - Notas:

## Fluxos
(passos ou Mermaid — feliz + falha)

## KPIs
| KPI | Definição | Baseline | Alvo | Janela |
|-----|-----------|----------|------|--------|

## Métricas
| Métrica / evento | Onde observar | Ligação ao KPI |
|------------------|---------------|----------------|

## Critérios de aceite
- [ ] …
- [ ] Isolamento por tenant validado na narrativa e nos testes
- [ ] Permissão por perfil coberta

## Roadmap
- Fase / onda:
- Tickets relacionados:
- Dependências de negócio:

## Backlog derivado
| Item | MoSCoW | Notas |
|------|--------|-------|

## Priorização
Método: RICE | MoSCoW (+ esforço/risco)
| Item | Score / classe | Justificativa |
|------|----------------|---------------|

## Handoff
- Próximo: Planner (`create-feature-plan`) / UX (`senior-ux-designer`)
- Fora de escopo de produto (explícito):
```

## Integração com o repo

1. Ler contexto: `docs/VISION.md`, `docs/ROADMAP.md`, `docs/BACKLOG.md`, `docs/AGENTS.md`.
2. Preencher checklist `docs/CHECKLISTS/product-design-checklist.md`.
3. Guardar artefacto em `docs/product/<slug>.md` (criar pasta se necessário).
4. Se alterar fases ou ideias comprometidas: atualizar `ROADMAP.md` / `BACKLOG.md` com impacto documentado.
5. Só depois: ticket técnico (`tickets/`, skill `create-feature-plan`) e UX (`senior-ux-designer`).
6. Resposta ao utilizador no formato do projeto: objetivo, plano, arquivos, riscos, próximos passos.

## Anti-padrões

- Feature pedida só porque “o concorrente tem”
- Backlog de ecrãs sem KPI
- Priorização por opinião sem critério
- Misturar regra de domínio no frontend como “definição de produto”
- Ignorar billing/quotas quando o valor depende de consumo
- Personas genéricas (“o utilizador”) sem papel nem tenant
- Roadmap eterno sem critérios de corte (Won’t / fase seguinte)
