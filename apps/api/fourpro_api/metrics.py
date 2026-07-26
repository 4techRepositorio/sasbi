"""Métricas HTTP básicas em texto Prometheus (TICKET-013)."""

from __future__ import annotations

import threading
from collections import defaultdict

_lock = threading.Lock()
_counters: dict[tuple[str, str, str], int] = defaultdict(int)


def observe_http(method: str, path: str, status: int) -> None:
    key = (method.upper(), path, str(status))
    with _lock:
        _counters[key] += 1


def render_prometheus() -> str:
    lines = [
        "# HELP http_requests_total Contagem de pedidos HTTP da API 4Pro_BI.",
        "# TYPE http_requests_total counter",
    ]
    with _lock:
        items = sorted(_counters.items())
    for (method, path, status), value in items:
        safe_path = path.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(
            f'http_requests_total{{method="{method}",path="{safe_path}",status="{status}"}} {value}'
        )
    lines.append("")
    return "\n".join(lines)
