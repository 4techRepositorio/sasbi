# UX Checklist

Usar antes de implementar ou alterar telas em `apps/web`. Skill: `.cursor/skills/senior-ux-designer/SKILL.md`.

## Discovery
- [ ] Persona / papel(is) identificados
- [ ] Objetivo do usuário em uma frase
- [ ] Frequência de uso definida
- [ ] Tempo esperado para concluir a tarefa
- [ ] Erros possíveis listados (validação, permissão, rede, quota, tenant)
- [ ] Jornada ponta a ponta descrita

## Entregáveis
- [ ] Fluxo do usuário
- [ ] Jornada (etapas + fricções)
- [ ] Wireframe (ASCII e/ou `docs/wireframes/` + evidência em `docs/assets/wireframes/exports/` se houver)
- [ ] Lista de componentes reutilizáveis
- [ ] Loading / Empty / Error / Success definidos
- [ ] Cada decisão de UX justificada

## Qualidade de uso
- [ ] Sem campos desnecessários
- [ ] Cliques mínimos para a tarefa principal
- [ ] Consistência com shell e padrões existentes
- [ ] Tenant atual visível em áreas administrativas
- [ ] Contraste e foco de teclado pensados
- [ ] Layout utilizável em mobile e desktop
- [ ] Empty state com CTA claro
- [ ] Error state com recuperação (retry / ajuda / permissão)
- [ ] Mensagens amigáveis + logs técnicos no backend (não expor segredos)

## Alinhamento produto / segurança
- [ ] Critérios marcados em `docs/wireframes/validation-*.md` quando aplicável
- [ ] Isolamento por tenant respeitado na narrativa da UI
- [ ] Permissão por perfil refletida (ocultar vs. desabilitar com motivo)
- [ ] Fluxos sensíveis (login, MFA, reset) sem vazamento de existência de conta
