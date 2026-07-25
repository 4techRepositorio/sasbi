import json
import logging
import sys
from datetime import UTC, datetime

from fourpro_api.config import get_settings
from fourpro_api.middleware.correlation import get_correlation_id


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None) or get_correlation_id(),
        }
        for key in ("method", "path", "status_code", "duration_ms", "tenant_id", "ingestion_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    # Evita handlers duplicados em reload/testes.
    root.handlers.clear()
    h = logging.StreamHandler(sys.stdout)
    if settings.log_json:
        h.setFormatter(JsonLogFormatter())
    else:
        h.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        )
    root.addHandler(h)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
