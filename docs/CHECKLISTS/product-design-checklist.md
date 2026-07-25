# Product Design Checklist

Usar **antes** de plano técnico, wireframes ou implementação. Skill: `.cursor/skills/product-designer/SKILL.md`.

## Discovery (bloqueante)

- [ ] Problema de negócio / dor descrito em 1–3 frases
- [ ] Quem utiliza (persona + papel) identificado
- [ ] Valor entregue explícito (tempo, risco, receita, adesão, compliance, …)
- [ ] Forma de medir definida (KPI primário + janela)
- [ ] Nenhuma feature avançou só por “pedido” ou paridade sem objetivo

## Entregáveis obrigatórios

- [ ] Casos de uso (feliz + alternativas/erros; tenant e perfil)
- [ ] User Stories (`Como… quero… para…`)
- [ ] Personas (objetivos, dores, frequência, restrições)
- [ ] Fluxos (passos ou Mermaid; feliz + falha)
- [ ] KPIs (definição, baseline/alvo quando conhecido)
- [ ] Métricas / eventos observáveis ligados aos KPIs
- [ ] Critérios de aceite verificáveis
- [ ] Roadmap (fase/onda + tickets relacionados)
- [ ] Backlog derivado (MoSCoW ou equivalente)
- [ ] Priorização com método explícito (RICE ou MoSCoW + esforço/risco)

## Alinhamento 4Pro_BI

- [ ] Multitenancy e RBAC considerados na narrativa de valor
- [ ] Impacto em billing/quotas referido quando aplicável
- [ ] Ingestão: upload ≠ processado (status mensurável)
- [ ] UX nativa 4Pro_BI (sem marcas OSS na experiência final)
- [ ] Artefacto em `docs/product/` (ou ticket/plano com secção completa)
- [ ] Consistente com `docs/VISION.md` / `ROADMAP.md` / `BACKLOG.md`

## Handoff

- [ ] Fora de escopo de produto explícito
- [ ] Próximo passo: Planner (`create-feature-plan`) e/ou Senior UX Designer
- [ ] Riscos de negócio / dependências listados
