# Plano detalhado — TICKET-013 Observabilidade e enterprise (Marco E)

**Papéis:** Architect · Backend · SRE · Security  
**Status:** planejado  
**Ticket:** `tickets/TICKET-013-observability-enterprise.md`  
**Alinhamento:** Marco **E** em `EXECUCAO-MESTRE.md`; `docs/ROADMAP.md` (auditoria avançada, observabilidade); `.cursor/rules/06-security.mdc` (audit log).

## 1. Objetivo

Endurecer o produto para cenário **enterprise**: tráfego rastreável (`correlation_id` / `request_id`), auditoria de ações críticas persistida, métricas e logs estruturados preparados para agregação (OpenTelemetry ou stack equivalente), alinhado a checklists de segurança.

## 2. Escopo

| Incluído | Excluído |
|----------|----------|
| `correlation_id` propagado API → worker em fluxos ingestão | SOC 24/7 e SIEM dedicado |
| Tabela ou stream `audit_events` (quem, o quê, tenant, timestamp, resultado) | Whitelabel UI completo (pode ser ticket separado) |
| Métricas HTTP básicas + health detalhado (DB, Redis, fila) | Multi-região ativo-ativo |
| Política de retenção de logs documentada | Certificação formal (ISO/SOC2) |

## 3. Eventos de auditoria mínimos (exemplos)

- Login sucesso/falha; MFA; reset password solicitado/concluído.
- Upload; mudança de estado de ingestão; alteração de plano/subscrição (admin).
- CRUD dashboard (TICKET-011) quando existir.

## 4. Subtarefas

1. Middleware FastAPI: gerar/propagar `X-Request-ID`; log JSON com campos standard.
2. Modelo `audit_events` + serviço append-only + API admin filtrada por tenant (super-admin global conforme modelo).
3. Worker: receber `correlation_id` na task e logar em todas as transições.
4. Métricas: endpoint `/metrics` em formato expositor padrão da indústria (operacional, não exposto ao portal do cliente) ou integração documentada em Compose.
5. Atualizar `docs/SECURITY.md` e checklists.

## 5. QA — critérios de aceite

- [ ] Um fluxo upload → worker → processed pesquisável por um único ID de correlação nos logs.
- [ ] Ação crítica gera linha de auditoria; tenant não pode apagar auditoria.
- [ ] Testes mínimos em serviço de auditoria (mock time/user).

## 6. Riscos

| Risco | Mitigação |
|-------|-----------|
| Volume de eventos | TTL/partição; amostragem apenas para não-críticos (documentar) |
| PII em logs | Política explícita; redação de emails em logs de debug |

## 7. Dependências

TICKET-001–008 mínimo; reforço após TICKET-011/012 conforme superfície de risco.

## 8. Próximo passo

Revisão anual de retenção e integração com fornecedor de logs (ADR).
