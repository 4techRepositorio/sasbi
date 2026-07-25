# Boas práticas — Design System 4Pro_BI

## Reuso

1. Antes de qualquer markup novo: pesquisar `.da-` em `styles.scss` e componentes em `shared/`.
2. Se 2 ecrãs precisam do mesmo bloco → extrair para `shared/` ou primitive CSS, não copiar.
3. Preferir variação (`--compact`, `--ghost`) a um componente irmão quase igual.

## Tokens

1. Novas cores → `_tokens.scss`, nunca hex solto em componente.
2. Espaçamento: escala `--da-space-*`.
3. Foco: usar `--da-focus-ring` em controlos customizados.

## Composição

1. Cards só quando contêm interação ou agrupam conteúdo operacional (pipeline, admin).
2. Shell já define navegação; não criar segundo menu paralelo.
3. Manter tenant e papel visíveis em áreas autenticadas.

## Acessibilidade

1. Todo controlo tem nome acessível.
2. Erros com `role="alert"`; status com `role="status"` / `aria-live` quando dinâmicos.
3. Não remover outline sem substituir por foco visível.

## Anti-padrões

- Componente `FooSpecialButton` só para um ecrã
- Duplicar markup de quota / tabela / card
- Gradientes ou paletas fora dos tokens de marca
- Expor nomes de libs OSS na UI
