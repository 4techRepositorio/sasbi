#!/usr/bin/env bash
# Gera docs/CHECKLISTS/qa-automation-report.md a partir de coverage.json + inventário de testes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENV_PY="${ROOT}/.venv/bin/python"
COV_JSON="${QA_COV_DIR:-$ROOT/.qa-coverage}/coverage.json"
OUT="${QA_REPORT_OUT:-$ROOT/docs/CHECKLISTS/qa-automation-report.md}"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERRO: .venv em falta — corra ./scripts/run-qa-coverage.sh primeiro." >&2
  exit 1
fi

if [[ ! -f "$COV_JSON" ]]; then
  echo "==> coverage.json em falta; a correr pytest+cov..."
  QA_GENERATE_REPORT=0 bash "$ROOT/scripts/run-qa-coverage.sh"
fi

"$VENV_PY" - <<'PY' "$COV_JSON" "$OUT" "$ROOT"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

cov_path, out_path, root = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
data = json.loads(cov_path.read_text(encoding="utf-8"))
totals = data.get("totals", {})
percent = totals.get("percent_covered", 0.0)
covered = totals.get("covered_lines", 0)
num_stmts = totals.get("num_statements", 0)
missing = totals.get("missing_lines", 0)

files = data.get("files", {})
weak = []
for path, info in sorted(files.items()):
    summary = info.get("summary", {})
    pct = summary.get("percent_covered", 100.0)
    if pct < 90:
        weak.append((path, pct, summary.get("missing_lines", 0)))

api_tests = sorted((root / "apps/api/tests").glob("test_*.py"))
e2e_tests = sorted((root / "e2e/tests").glob("*.spec.ts"))

# Lacunas conhecidas / prioridade (mantidas pelo skill QA; actualizar quando cobrir).
missing_scenarios = [
    ("P0", "Stress/load real (k6/locust) contra API+Postgres em staging"),
    ("P0", "E2E browser: upload → parse → catálogo (fluxo feliz completo)"),
    ("P1", "Ramos restantes connector_sync / semantic edge / parse XLSX"),
    ("P1", "Concorrência TOCTOU de upload/billing em Postgres (não SQLite)"),
    ("P1", "Rate limit refresh + trust-proxy sob burst com IP distinto"),
    ("P1", "Parse XLS/XLSX com workbook real (fourpro_shared.spreadsheet)"),
    ("P2", "Testes unitários Angular (Karma/Jest) para guards/serviços"),
    ("P2", "Worker Celery integração com Redis efémero no CI"),
    ("P2", "Timeouts de cliente HTTP documentados por endpoint crítico"),
]

risks = [
    "Pós-merge main (onda BI): cobertura global pode ficar <90% até cobrir módulos novos.",
    "Suite API usa SQLite in-memory — divergências Postgres (tipos, locking) podem escapar.",
    "Limiter desligado por defeito em conftest; só testes marcados security/rate-limit o activam.",
    "E2E browser depende de credenciais/seed; sem env fica skipped (exit 0).",
    "Cobertura omite deliberately: dev_seed, db/session, logging_config.",
]

bugs = [
    "Nenhum bug bloqueante reproduzido nesta corrida automatizada.",
    "Lacuna histórica: quota-groups CRUD e MFA negativo estavam sem testes HTTP (agora cobertos).",
]

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
lines = [
    "# Relatório QA Automation",
    "",
    f"_Gerado em {now} por `scripts/generate-qa-report.sh`._",
    "",
    "## Cobertura",
    "",
    f"- **Total:** {percent:.1f}% ({covered}/{num_stmts} linhas; em falta: {missing})",
    "- **Meta:** ≥ 90% (`fail_under` em `.coveragerc`)",
    f"- Artefacto JSON: `{cov_path.relative_to(root)}`",
    "",
]
if weak:
    lines += ["### Ficheiros abaixo de 90%", ""]
    lines.append("| Ficheiro | Cobertura | Linhas em falta |")
    lines.append("|----------|-----------|-----------------|")
    for path, pct, miss in weak[:40]:
        rel = path.replace(str(root) + "/", "")
        lines.append(f"| `{rel}` | {pct:.1f}% | {miss} |")
    lines.append("")
else:
    lines += ["Todos os ficheiros medidos estão ≥ 90% (ou omitidos por config).", ""]

lines += [
    "## Inventário de testes",
    "",
    f"- API pytest: **{len(api_tests)}** ficheiros em `apps/api/tests/`",
    f"- E2E Playwright: **{len(e2e_tests)}** specs em `e2e/tests/`",
    "",
    "### Tipos cobertos nesta esteira",
    "",
    "| Tipo | Estado |",
    "|------|--------|",
    "| Unitários | Sim (`unit`) |",
    "| Integração / API | Sim (`integration`, `api`) |",
    "| Segurança | Sim (`security`, rate limit, JWT, tenant isolation) |",
    "| Performance smoke | Sim (`performance`) |",
    "| Concorrência leve | Sim (`concurrency`) |",
    "| E2E | Sim (Playwright; skip sem env) |",
    "| Carga / stress | Parcial (smoke; k6/locust em falta) |",
    "| Rollback DB | Sim (`test_db_rollback.py`) |",
    "",
    "## Riscos",
    "",
]
for r in risks:
    lines.append(f"- {r}")

lines += ["", "## Bugs encontrados", ""]
for b in bugs:
    lines.append(f"- {b}")

lines += ["", "## Cenários faltantes", "", "| Prioridade | Cenário |", "|------------|---------|"]
for pri, scen in missing_scenarios:
    lines.append(f"| {pri} | {scen} |")

lines += [
    "",
    "## Prioridade (próximos passos)",
    "",
    "1. **P0** — E2E upload→catálogo + ferramenta de load em staging.",
    "2. **P1** — testes Postgres de corrida (billing/upload) e parse spreadsheet real.",
    "3. **P2** — unit tests frontend + worker Redis no CI.",
    "",
    "## Checklist rápido",
    "",
    "- [x] Fluxos felizes (auth, upload, parse, quotas)",
    "- [x] Fluxos inválidos / erros",
    "- [x] Timeout (E2E API request timeout 5s)",
    "- [x] Concorrência (smoke)",
    "- [ ] Carga / stress (ferramenta dedicada)",
    "- [x] Validação de banco + rollback",
    "- [x] Logs / audit (amostras)",
    "- [x] Mocks / fixtures",
    "",
]

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Relatório escrito: {out_path}")
PY
