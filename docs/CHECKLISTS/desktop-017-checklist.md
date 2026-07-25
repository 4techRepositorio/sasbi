# Checklist QA — TICKET-017 Desktop authoring

## Fluxo feliz
- [ ] Login contra API local (`VITE_API_BASE_URL`)
- [ ] MFA verify quando o backend devolve challenge
- [ ] Tenant activo visível na sidebar
- [ ] Criar fonte Postgres ou REST, testar, gravar
- [ ] Sync + publish dataset
- [ ] Adicionar widgets KPI/tabela e publish dashboard
- [ ] Logout limpa tokens (nova abertura pede login)

## Erro / degradação
- [ ] API offline → mensagem amigável no login
- [ ] Rotas 015/017 404 → fallback catálogo local / erros claros
- [ ] `/desktop/session` 404 → usa `/me/context`

## Isolamento
- [ ] Pedidos autenticados só com JWT do tenant da sessão
- [ ] Sem tokens em logs do renderer

## Build
- [ ] `npm install && npm run build && npm test` em `apps/desktop`
- [ ] CI headless: `xvfb-run` documentado no README
