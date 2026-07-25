# Design Review Checklist

Usar em PRs de frontend, wireframes ou demos de ecrã. Skill: `.cursor/skills/design-reviewer/SKILL.md`.  
**Este papel nunca cria telas — apenas revisa.**

## Gate

- [ ] Interface intuitiva (não apenas “bonita”)
- [ ] Veredito registado: APROVAR / APROVAR COM RESSALVAS / BLOQUEAR
- [ ] Cada problema com Descrição / Impacto / Prioridade / Sugestão

## Checklist obrigatório (15)

- [ ] UX — fluxo claro, cliques mínimos, sem campos desnecessários
- [ ] UI — ação primária óbvia, densidade corporativa, marca nativa 4Pro_BI
- [ ] Design System — tokens `--da-*` / componentes `.da-*` / `packages/ui`
- [ ] Responsividade — breakpoints úteis; overflow e nav utilizáveis
- [ ] Consistência — padrões iguais entre rotas próximas
- [ ] Hierarquia — título → subtítulo → CTA; sem competição visual
- [ ] Espaçamentos — escala do DS; sem gaps aleatórios
- [ ] Tipografia — escala e pesos do DS; meta em muted
- [ ] Acessibilidade — contraste, foco, labels, teclado, não só cor
- [ ] Performance — peso visual/motion aceitável; listas densas tratadas
- [ ] Estados — loading / erro / vazio / sucesso (+ forbidden/quota se aplicável)
- [ ] Feedback visual — hover/disabled/confirmação; progresso de ingestão legível
- [ ] Navegação — contexto preservado; tenant visível em admin
- [ ] Clareza — copy útil; status da pipeline compreensível
- [ ] Componentização — reuso; sem markup duplicado sem motivo

## Alinhamento

- [ ] Sem marcas OSS na superfície do utilizador
- [ ] Upload ≠ ingestão concluída reflectido na UI quando aplicável
- [ ] Checklist frontend / UX actualizados se o contrato visual mudou
