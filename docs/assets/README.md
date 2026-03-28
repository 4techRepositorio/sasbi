# Imagens e artefactos visuais — como são gerados e onde vivem

Este documento define **tipos de imagem**, **origem** (como são criadas) e **localização**, para evitar ficheiros soltos sem política. Sigilo comercial: exports públicos devem seguir `docs/ARCHITECTURE.md` (sem marcas de terceiros na experiência do cliente).

---

## 1. Diagramas de arquitetura e fluxos (documentação técnica)

| Aspeto | Política |
|--------|----------|
| **Fonte canónica** | Diagramas em **Mermaid** dentro dos próprios `.md` (`docs/plans/`, `docs/ARCHITECTURE.md`, ADRs futuros), para diff em Git e render em GitHub/Cursor. |
| **Export estático opcional** | Se for necessário PNG/SVG para PDF ou apresentações, gerar a partir do bloco Mermaid com ferramenta de linha de comando ou IDE e guardar em `docs/assets/diagrams/exports/` com nome `YYYYMMDD-<tópico>.<ext>`. |
| **Quem gera** | Equipa no PR que altera o fluxo; ou job CI opcional (TICKET-014) se for adoptado. |
| **Binários grandes** | Preferir Mermaid no texto; PNG só se tamanho modesto (ordem de centenas de KB) ou usar Git LFS por decisão de repo. |

Pasta: [`diagrams/`](./diagrams/) contém subpastas `exports/` (raster/vector gerados) e pode conter `sources/` apenas se houver ficheiros de desenho editável não-Mermaid.

---

## 2. Evidências de wireframe e alinhamento UX (sign-off)

| Aspeto | Política |
|--------|----------|
| **Objectivo** | Comprovar que a implementação ou o desenho validado cumpre critérios das folhas `docs/wireframes/validation-*.md`. |
| **Como gerar** | (a) Export PNG/SVG/PDF a partir da **ferramenta de design** aprovada internamente; (b) **captura de ecrã** da app (staging) com viewport definida; (c) futuro: **screenshots automáticos** (ex.: Playwright) numa pasta de artefactos de CI, não obrigatoriamente no Git. |
| **Nomenclatura** | `wireframes/exports/<área>-<tela>-v<versão>-YYYYMMDD.png` (ex.: `workspace-dashboard-editor-v1-20260327.png`). |
| **Referência no texto** | Nos `validation-*.md`, ligar para ficheiros nesta pasta quando existir evidência (markdown: `![descrição](./wireframes/exports/...)`). |

Pasta: [`wireframes/exports/`](./wireframes/exports/).

---

## 3. Imagens geradas pelo produto (runtime)

| Aspeto | Política |
|--------|----------|
| **Exemplos** | Export PNG/PDF de dashboards, relatórios, gráficos (Fase 3 / TICKET-011). |
| **Como geram** | **Servidor ou worker** (bibliotecas de renderização, headless browser, ou motor de relatórios incorporado), por pedido autenticado; ficheiros podem ser **efémeros** (download directo) ou guardados em **object storage** com `tenant_id` no caminho. |
| **Não vão para** | `docs/assets/` — não são documentação estática; são dados de utilizador ou artefactos operacionais. |
| **Retenção** | Definir por política de billing e ADR de governança (TICKET-012); default MVP: só stream ao cliente, sem arquivo longo, salvo feature explícita. |

---

## 4. Imagens Docker (OCI) — não são «imagens de docs»

| Aspeto | Política |
|--------|----------|
| **O que são** | Artefactos `docker build` para API, Web, Worker (`infra/`, Dockerfiles). |
| **Como geram** | Pipeline de build (local ou CI); etiquetas `semver` ou digest; registry privado em produção. |
| **Documentação** | `infra/compose/README.md`, `infra/portainer/README.md` — não duplicar aqui o processo completo. |

---

## 5. Ficheiros de utilizadores (upload / ingestão)

Imagens ou PDFs carregados por clientes **não** são gerados pelo repositório: seguem pipeline TICKET-006+007 (`docs/INGESTION.md`), armazenamento em disco/compatível S3, metadados na BD.

---

## Estrutura de pastas (resumo)

```text
docs/assets/
  README.md              ← este ficheiro
  diagrams/
    exports/             ← PNG/SVG opcionais a partir de Mermaid ou outras fontes
  wireframes/
    exports/             ← evidências de validação / protótipo alinhado à app
```

Ficheiros `.gitkeep` mantêm pastas vazias no Git até à primeira entrega.

---

## Checklist rápido (nova imagem em `docs/assets`)

- [ ] Tipo correcto (1–5 acima)?
- [ ] Nome e pasta conforme convenção?
- [ ] Nenhuma marca ou dado sensível que não deva ser público no repo?
- [ ] Documento de validação ou ADR referencia o ficheiro, se for evidência de sign-off?
