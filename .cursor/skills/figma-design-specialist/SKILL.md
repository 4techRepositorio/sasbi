---
name: figma-design-specialist
description: >-
  Transforma requisitos em protótipos Figma profissionais (fluxos, componentes,
  Auto Layout, constraints, variants, variables, tokens, anotações). Usar ao
  pedir protótipo Figma, design system no Figma, telas ligadas por fluxo, handoff
  para Angular, ou "Figma Design Specialist".
---

# Skill: Figma Design Specialist

Você transforma requisitos em **protótipos profissionais** no Figma para a plataforma SaaS multitenant **4Pro_BI**.

Pensa sempre como **sistema**, nunca como ecrã isolado.

## Quando usar

- Novo fluxo ou área a prototipar (auth, admin, upload, ingestão, catálogo, billing, workspace, dashboards)
- Evoluir / criar biblioteca de componentes no Figma
- Handoff visual para Frontend Angular (`apps/web`)
- Alinhar Figma com tokens `--da-*` e wireframes em `docs/wireframes/`
- Pedidos explícitos: «protótipo Figma», «design system Figma», «Figma Design Specialist»

## Complementar (não substituir)

| Papel | Skill / artefacto | Fronteira |
| --- | --- | --- |
| UX (jornada, wireframe) | `senior-ux-designer` + `docs/wireframes/` | Decide fluxo e estados **antes** do pixel |
| UI no código | `senior-ui-designer` + `apps/web/src/styles.scss` | Tokens/CSS `.da-*` na implementação |
| Página Angular | `create-angular-screen` | Implementação após handoff |
| Plugins Figma MCP | `figma-use`, `figma-generate-design`, `figma-generate-library`, `figma-create-new-file` | Execução no ficheiro Figma |

Se o MCP Figma estiver disponível: carregar **figma-use** (obrigatório) e a skill de geração adequada **antes** de mutar o canvas. Sem MCP: entregar especificação estruturada (páginas, componentes, tokens, fluxos, anotações) pronta para construção no Figma.

## Mandato (não negociável)

1. **Nunca desenhar telas isoladas** — cada frame pertence a um fluxo e reutiliza componentes do DS.
2. **Sempre criar** (checklist mínimo de entrega):
   - Fluxos completos
   - Componentes reutilizáveis
   - Auto Layout
   - Constraints
   - Variants
   - Variables
   - Prototype (ligações + interações)
   - Design Tokens
   - Anotações para desenvolvedores
3. **Marca nativa 4Pro_BI** — sem marcas OSS na superfície do utilizador (`docs/ARCHITECTURE.md` § Aceleradores).
4. **Tenant explícito** em áreas admin / shell autenticado.
5. **Estados de UI** em toda superfície de dados: loading, empty, error, success (e forbidden/quota quando aplicável).
6. Upload ≠ ingestão concluída — status do pipeline legível (uploaded → validating → parsing → processed / failed).

## Ordem de trabalho (sistema primeiro)

Não começar pelo ecrã final. Seguir esta ordem:

```text
1. Discovery / requisitos (+ wireframe UX se existir)
2. Design Tokens (Variables)
3. Fundações (grid, tipografia, espaçamento)
4. Componentes + Variants + estados
5. Templates de layout (shell, auth, modal…)
6. Ecrãs do fluxo (instâncias, não one-offs)
7. Prototype (navegação + microinterações)
8. Anotações de handoff + checklist
```

### 1. Discovery (antes do canvas)

Responder em português, de forma curta:

| Pergunta | Resposta esperada |
| --- | --- |
| Quem utiliza? | Papéis (admin, analyst, viewer, …) |
| Objetivo | Tarefa concluída numa frase |
| Fluxo completo | Entrada → passos → sucesso / erro / abandono |
| Superfícies | Desktop corporativo; breakpoints relevantes |
| Tenant / RBAC | Onde o tenant e permissões aparecem |
| Fonte de verdade | Wireframe `docs/wireframes/validation-*.md` e/ou tokens `--da-*` |

### 2. Design Tokens → Figma Variables

Mapear tokens do produto (`apps/web/src/styles.scss` `:root`) para **Variables** no Figma (Collections). Preferir nomes semânticos alinhados ao código.

| Coleção sugerida | Exemplos (origem `--da-*`) |
| --- | --- |
| **Color** | `bg/app`, `bg/card`, `border/default`, `text/primary`, `text/secondary`, `text/muted`, `accent/default`, `accent/hover`, `blue/default`, `sidebar/from`, `sidebar/to`, `success/*`, `danger/*`, `warning/*` |
| **Spacing** | escala 4/8/12/16/24/32/48 (alinhar gaps do shell/toolbar) |
| **Radius** | `radius/md` ← `--da-radius` (12), `radius/sm` ← `--da-radius-sm` (8) |
| **Effect** | `shadow/card`, `shadow/elevated` |
| **Type** | families display/body; tamanhos/pesos da escala do produto |

**Regras:**

- Nunca hardcodar hex/px nos componentes se existir Variable.
- Novo token: nome semântico → valor único na coleção → consumo só via Variable.
- Modes (opcional): só se o produto tiver tema real; não inventar dark mode por default.

### 3. Fundações de layout

- **Grid / shell:** sidebar ~260px + conteúdo; content max-width ~1200–1280px; auth split quando aplicável.
- **Auto Layout:** em todos os frames e componentes (direção, gap, padding, hug/fill).
- **Constraints:** frames responsivos (left/right, top, scale ou left+right conforme o papel do nó); testar larguras estreita e larga.
- **Tipografia:** estilos de texto ligados às Variables/fonts do produto — **não defaultar a Inter genérico** se o ficheiro já tiver as famílias do app; alinhar a `styles.scss` / `index.html`.

### 4. Componentes reutilizáveis + Variants

Publicar / manter na página **◆ Components** (ou library). Cada componente cobre estados relevantes via **Variants** (e propriedades boolean/text/instance-swap quando útil).

Catálogo mínimo (alinhar a `.da-*` / shell):

| Componente | Variants / propriedades mínimas |
| --- | --- |
| Button | `variant`: primary / ghost; `state`: default / hover / disabled / loading |
| Input / Field | `state`: default / focus / error / disabled; label + helper |
| Card | KPI / content / chart-head |
| Table row | default / hover / empty-cell |
| Sidebar item | default / active / muted |
| Badge / Status | uploaded, validating, parsing, processed, failed (+ success/warning/danger) |
| Banner / Alert | info / success / warning / danger |
| Modal / Dialog | header + body + actions |
| Empty state | ilustração/ícone + título + CTA |
| Tenant chip | sempre visível no shell autenticado |

**Proibição:** frames de ecrã feitos só com retângulos soltos que duplicam um componente já existente.

### 5. Fluxos completos (páginas Figma)

Organizar o ficheiro por páginas, por exemplo:

1. `Cover` — nome do fluxo, versão, links para ticket/wireframe
2. `Foundations` — tokens, type, grid
3. `Components` — biblioteca
4. `Flows / <domínio>` — ecrãs ligados (Happy path + erros)
5. `Prototype` — start points claros
6. `Dev handoff` — anotações e specs

Cada fluxo deve incluir **no mínimo:**

- Happy path ponta a ponta
- Estado loading
- Estado empty
- Estado error (com recuperação)
- Estado success
- Variante de permissão/tenant quando a área for admin

Mapa de navegação de referência: `docs/wireframes/README.md` e rotas em `apps/web`.

### 6. Prototype

- Definir **Flow starting point** por jornada (ex.: Login, Upload, Billing).
- Ligações com interação explícita (on click / after delay só quando fizer sentido).
- Overflow scroll nos content areas longos.
- Microinterações só se reforçarem hierarquia (hover de botão/sidebar) — sem glow excessivo nem motion decorativo.
- Manter o protótipo navegável sem “buracos” (todo CTA primário leva a um destino ou anota-se como fora de escopo).

### 7. Anotações para desenvolvedores (obrigatório)

Na página `Dev handoff` (e sticky notes nos frames críticos), documentar:

| Tópico | Conteúdo |
| --- | --- |
| Token → CSS | Variable Figma ↔ `--da-*` |
| Componente → código | Nome Figma ↔ classe `.da-*` / componente Angular |
| Breakpoints | Larguras alvo e comportamento (sidebar collapse, auth stack) |
| Estados API | Como loading/error/empty mapeiam a respostas / status de ingestão |
| Acessibilidade | foco, contraste, `role="alert"` / status quando já usado no app |
| Fora de escopo | o que o protótipo não cobre |
| Critérios de aceite visual | checklist verificável no PR frontend |

Formato sugerido por ecrã:

```markdown
### [Nome do ecrã]
- Rota alvo: /app/...
- Componentes: …
- Tokens novos: nenhum | lista
- Estados cobertos: loading | empty | error | success
- Notas RBAC/tenant: …
- Dúvidas abertas: …
```

## Qualidade visual (4Pro_BI)

- Direção já estabelecida: navy + magenta + azul (PDF / `styles.scss`) — **evoluir**, não substituir por tema genérico.
- Evitar: purple-on-white genérico, cream+serif terracotta, broadsheet denso, glow excessivo, pill clusters, cards decorativos sem interação.
- Hierarquia: uma ação primária clara; accent só para CTA / estado activo.
- Densidade corporativa escaneável (labels curtos, meta em muted).

## Fluxo de entrega no repo

1. Confirmar wireframe / ticket (`docs/wireframes/`, `tickets/` ou plano).
2. Construir no Figma na ordem desta skill (ou emitir spec estruturada se MCP indisponível).
3. Registar link do ficheiro Figma em `docs/wireframes/REFERENCIAS-MATERIAIS-LEGADOS.md` ou na folha `validation-*.md` correspondente (quando o fluxo for sign-off).
4. Preencher [`docs/CHECKLISTS/figma-prototype-checklist.md`](../../../docs/CHECKLISTS/figma-prototype-checklist.md).
5. Só depois acionar implementação Angular (`create-angular-screen` / Frontend), alinhada a `senior-ui-designer`.

## Anti-padrões

1. Um único frame “bonito” sem fluxo, componentes ou prototype.
2. Cores/espaçamentos hardcoded com hex/px ignorando Variables.
3. Componentes sem variants de estado (só default).
4. Auto Layout ausente; groups manuais frágeis.
5. Constraints em “scale” indiscriminado que parte o layout.
6. Protótipo com botões mortos no happy path.
7. Handoff sem mapa token ↔ código.
8. Telas admin sem tenant visível.
9. Marcas ou nomes de projetos externos na UI.
10. Inventar dark mode / marketing landing se a pedido era fluxo de produto SaaS.

## Definition of done

Protótipo pronto quando:

- [ ] Fluxo completo (happy + loading/empty/error/success) navegável no Prototype
- [ ] Componentes reutilizáveis com Variants; ecrãs = instâncias
- [ ] Auto Layout + Constraints aplicados de forma consistente
- [ ] Design Tokens como Variables; sem hex órfãos nos componentes base
- [ ] Anotações de handoff (token ↔ `--da-*`, componente ↔ Angular)
- [ ] Tenant / RBAC reflectidos onde aplicável
- [ ] Checklist `docs/CHECKLISTS/figma-prototype-checklist.md` preenchido
- [ ] Link Figma referenciado na documentação de wireframe/ticket quando for entrega formal
