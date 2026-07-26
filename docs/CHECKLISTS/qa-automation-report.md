# Relatório QA Automation

_Gerado em 2026-07-26 00:29 UTC por `scripts/generate-qa-report.sh`._

## Cobertura

- **Total:** 94.8% (2039/2107 linhas; em falta: 68)
- **Meta:** ≥ 90% (`fail_under` em `.coveragerc`)
- Artefacto JSON: `.qa-coverage/coverage.json`

### Ficheiros abaixo de 90%

| Ficheiro | Cobertura | Linhas em falta |
|----------|-----------|-----------------|
| `apps/api/fourpro_api/jobs/connector_sync.py` | 88.2% | 5 |
| `apps/api/fourpro_api/jobs/ingestion_parse.py` | 77.6% | 20 |
| `apps/api/fourpro_api/repositories/mfa_repository.py` | 75.6% | 5 |
| `apps/api/fourpro_api/routers/semantic.py` | 89.4% | 8 |
| `apps/api/fourpro_api/services/auth_service.py` | 88.6% | 7 |
| `apps/api/fourpro_api/services/billing_service.py` | 89.7% | 4 |

## Inventário de testes

- API pytest: **43** ficheiros em `apps/api/tests/`
- E2E Playwright: **6** specs em `e2e/tests/`

### Tipos cobertos nesta esteira

| Tipo | Estado |
|------|--------|
| Unitários | Sim (`unit`) |
| Integração / API | Sim (`integration`, `api`) |
| Segurança | Sim (`security`, rate limit, JWT, tenant isolation) |
| Performance smoke | Sim (`performance`) |
| Concorrência leve | Sim (`concurrency`) |
| E2E | Sim (Playwright; skip sem env) |
| Carga / stress | Parcial (smoke; k6/locust em falta) |
| Rollback DB | Sim (`test_db_rollback.py`) |

## Riscos

- Pós-merge main (onda BI): cobertura global pode ficar <90% até cobrir módulos novos.
- Suite API usa SQLite in-memory — divergências Postgres (tipos, locking) podem escapar.
- Limiter desligado por defeito em conftest; só testes marcados security/rate-limit o activam.
- E2E browser depende de credenciais/seed; sem env fica skipped (exit 0).
- Cobertura omite deliberately: dev_seed, db/session, logging_config.

## Bugs encontrados

- Nenhum bug bloqueante reproduzido nesta corrida automatizada.
- Lacuna histórica: quota-groups CRUD e MFA negativo estavam sem testes HTTP (agora cobertos).

## Cenários faltantes

| Prioridade | Cenário |
|------------|---------|
| P1 | Ramos restantes connector_sync / semantic edge / parse XLSX |
| P0 | Stress/load real (k6/locust) contra API+Postgres em staging |
| P0 | E2E browser: upload → parse → catálogo (fluxo feliz completo) |
| P1 | Concorrência TOCTOU de upload/billing em Postgres (não SQLite) |
| P1 | Rate limit refresh + trust-proxy sob burst com IP distinto |
| P1 | Parse XLS/XLSX com workbook real (fourpro_shared.spreadsheet) |
| P2 | Testes unitários Angular (Karma/Jest) para guards/serviços |
| P2 | Worker Celery integração com Redis efémero no CI |
| P2 | Timeouts de cliente HTTP documentados por endpoint crítico |

## Prioridade (próximos passos)

1. **P0** — E2E upload→catálogo + ferramenta de load em staging.
2. **P1** — testes Postgres de corrida (billing/upload) e parse spreadsheet real.
3. **P2** — unit tests frontend + worker Redis no CI.

## Checklist rápido

- [x] Fluxos felizes (auth, upload, parse, quotas)
- [x] Fluxos inválidos / erros
- [x] Timeout (E2E API request timeout 5s)
- [x] Concorrência (smoke)
- [ ] Carga / stress (ferramenta dedicada)
- [x] Validação de banco + rollback
- [x] Logs / audit (amostras)
- [x] Mocks / fixtures

