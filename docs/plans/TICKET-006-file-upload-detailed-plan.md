# Plano detalhado — TICKET-006 Upload de ficheiros

**Papéis:** Backend Core · Security Reviewer · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-006-file-upload.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-006

## 1. Objetivo

Receber ficheiros `txt`, `csv`, `xls`, `xlsx`, `json` com validação de tipo/tamanho, armazenamento seguro (disco ou object storage) e registo mínimo associado ao tenant — sem confundir “upload concluído” com “ingestão processada” (ver TICKET-007).

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| Limites por extensão e bytes | Parsing pesado (TICKET-008) |
| Validação mágica bytes + MIME | Presigned multipart avançado (fase 2) |

### 2.2 Decisões

1. Rota protegida por auth + tenant + RBAC (analyst/admin).
2. Path/object key inclui `tenant_id` no prefixo.
3. Resposta com id de ingestão ou upload conforme modelo TICKET-007.
4. Quotas de storage podem ser preparadas; enforcement forte em TICKET-010.

## 3. Subtarefas

1. `routers/uploads.py` + schema multipart.
2. `StorageService`: local dev / MinIO configurável.
3. Validação: extensão, tamanho máximo, sniff de conteúdo quando aplicável.
4. Auditoria: quem enviou, quando, hash opcional do ficheiro.
5. Testes: tipo inválido, oversized, tenant isolation no path.

## 4. QA — critérios de aceite

- [ ] Upload válido persiste blob e retorna referência estável.
- [ ] Rejeição clara para tipo/tamanho inválidos.
- [ ] Consumer não consegue upload (403).

## 5. Security

- [ ] Sem path traversal; nomes sanitizados.
- [ ] Rate limit / quota básica anti-abuso.

## 6. Riscos

| Risco | Mitigação |
|-------|-----------|
| MIME spoofing | Validação de conteúdo, não só header |

## 7. Dependências

TICKET-004, TICKET-005.

## 8. Próximo ticket

TICKET-007 (metadata e máquina de estados).
