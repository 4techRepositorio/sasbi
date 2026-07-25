# Design System Checklist

Usar em PRs que toquem tokens, primitives `.da-*`, `packages/ui/` ou `apps/web/src/app/shared/`.

## Reuso

- [ ] Não foi criado componente visual one-off (procurado `.da-*` / `shared/` primeiro)
- [ ] Variação nova documentada (nome + quando usar)
- [ ] Barrel `shared/index.ts` atualizado se houver componente Angular novo

## Tokens

- [ ] Alterações de cor/espaço/tipo/radius em `packages/ui/scss/_tokens.scss`
- [ ] `docs/DESIGN_SYSTEM.md` atualizado se o inventário de tokens mudou
- [ ] Sem hex/magic numbers novos em templates de página

## Documentação e exemplos

- [ ] Documentação mínima em `docs/DESIGN_SYSTEM.md` e/ou `packages/ui/docs/`
- [ ] Exemplo de uso (HTML/Angular) incluído
- [ ] Boas práticas / anti-padrões mencionados quando relevante

## Variações e estados

- [ ] default
- [ ] hover / focus-visible
- [ ] disabled e/ou loading (`aria-busy` se aplicável)
- [ ] erro / vazio / sucesso quando o padrão mostra dados

## Acessibilidade

- [ ] Contraste AA nos pares texto/fundo usados
- [ ] Foco visível
- [ ] Labels / nomes acessíveis
- [ ] Teclado (Tab / Enter / Escape em overlays)
- [ ] Estado não comunicado só por cor

## Integração

- [ ] Frontend (F4) consome o padrão (sem fork local)
- [ ] `npm run build` em `apps/web` verde após mudança de tokens/estilos
- [ ] Experiência continua nativa **4Pro_BI**
