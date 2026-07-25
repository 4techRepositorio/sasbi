# Framework de conectores de dados

**ID:** TICKET-015  
**Plano detalhado:** [`docs/plans/TICKET-015-connector-framework-detailed-plan.md`](../docs/plans/TICKET-015-connector-framework-detailed-plan.md)  
**ADR:** [`docs/adr/001-bi-platform-connectors-desktop-web.md`](../docs/adr/001-bi-platform-connectors-desktop-web.md)  
**Plano mestre:** [`docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](../docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md)

## Objetivo

Criar um framework de plugins de conectores (SPI) multitenant, com cofre de credenciais, jobs de extract no worker e primeiros conectores além de ficheiro (PostgreSQL e REST JSON), reutilizando o ciclo de status de ingestão.

## Escopo

- Pacote/contratos do SPI e registry
- Modelos `data_sources` + credenciais encriptadas
- APIs: listar conectores, CRUD fonte, testar, sync, status
- Adaptar upload de ficheiro ao SPI (`file`)
- Conectores O1: `postgres`, `rest_json`
- Testes: isolamento tenant, segredo não vaza, fluxo feliz e erro

## Fora de escopo

- Desktop (TICKET-017)
- Modelo semântico completo (TICKET-016)
- Marketplace público; onda O2/O3 de conectores
- CDC / streaming

## Impacto técnico

Backend Data + Core (vault/audit); worker; contracts; docs `INGESTION.md`; billing (limites de fontes — stub ou regra mínima).

## Subtarefas

Ver plano detalhado.

## Critérios de aceite

- Tenant A não lê/escreve fontes de B.
- `test_connection` e `sync` auditáveis; secrets ausentes das respostas de listagem.
- Sync bem-sucedido produz ingestão/catálogo no mesmo tenant.
- Upload de ficheiro continua a funcionar via conector `file` ou caminho compatível.

## Riscos

Complexidade do SPI; egress inseguro; fuga de credenciais.

## Dependências

TICKET-004, 006–009, 010 (quotas); alinhamento com TICKET-012 para stage/camadas.
