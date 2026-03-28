# Validação de wireframe — Dados: upload, ingestão e catálogo

**Versão:** 0.2  
**Tickets relacionados:** TICKET-006, 007, 008, 009.

## 0. Evidências visuais (exports)

| Sugestão de ficheiro | Conteúdo |
|----------------------|----------|
| `pipeline-upload-v1-YYYYMMDD.png` | `/app/upload` |
| `pipeline-ingestions-v1-YYYYMMDD.png` | `/app/ingestions` (badges de estado) |
| `pipeline-datasets-v1-YYYYMMDD.png` | `/app/datasets` (catálogo) |

## 0.1 Mapeamento — implementação atual (`apps/web`)

| Bloco | Rota / componente | Cobertura MVP |
|-------|-------------------|---------------|
| Upload U1–U5 | `/app/upload` → `UploadComponent` | Sim; U3 progresso depende de API (multipart/stream) |
| Ingestão I1–I4 | `/app/ingestions` → `IngestionsComponent` | I1–I3 sim; I4 reprocessamento **a confirmar** na API/UI |
| Catálogo C1–C3 | `/app/datasets` → `DatasetsComponent` | C1 sim; C2 filtros **parciais** (listagem paginada na API; UI pode não expor todos) |
| Dashboard resumo | `/app/dashboard` → `DashboardComponent` | Visão agregada KPI + barras; não substitui critérios C1–C3 |

## 1. Objetivo

Validar que a UI comunica corretamente que **upload ≠ ingestão concluída**, exibe **status** (`uploaded`, `validating`, `parsing`, `processed`, `failed`) e permite ações seguras por tenant (listar, detalhar, eventual reprocessamento).

## 2. Telas / blocos

### 2.1 Upload (TICKET-006)

| # | Elemento | Critério |
|---|----------|----------|
| U1 | Seleção de arquivo | Tipos permitidos: txt, csv, xls, xlsx, json |
| U2 | Limite de tamanho | Feedback antes do envio e após erro de servidor |
| U3 | Progresso | Barra ou percentual quando disponível |
| U4 | Sucesso imediato | Mensagem: “Arquivo recebido”; não afirmar “processado” |
| U5 | Erro | Tipo/tamanho inválido; mensagem amigável + opcional código de suporte |

### 2.2 Fila / detalhe de ingestão (TICKET-007, 008)

| # | Elemento | Critério |
|---|----------|----------|
| I1 | Linha no histórico | Nome arquivo, tipo, tamanho, tenant implícito (filtro backend) |
| I2 | Status | Badge coerente com enum de ingestão |
| I3 | Falha | Mensagem amigável + acessar “detalhes técnicos” (collapse) para suporte |
| I4 | Reprocessamento | Se previsto: botão apenas para perfil autorizado; confirmação |

### 2.3 Catálogo de datasets (TICKET-009)

| # | Elemento | Critério |
|---|----------|----------|
| C1 | Listagem | Apenas datasets do tenant; estado vazio explicado |
| C2 | Filtros básicos | Por status, data, nome (acordo com API) |
| C3 | Detalhe | Metadados, versão se existir, link para workspace/visualização futura |

## 3. Consistência com regras de dados

- Separar visualmente: **arquivo bruto** → **em processamento** → **dataset catálogo**.  
- Logs técnicos não devem ser o texto principal da tela para usuário final.

## 4. Sign-off

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| Backend Data | | | |
| UX/CS | | | |
| QA | | | |
