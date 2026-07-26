"""Middleware de correlation / request ID (TICKET-013)."""

from __future__ import annotations

import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fourpro_api.metrics import observe_http

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)
logger = logging.getLogger("fourpro_api.http")


def get_correlation_id() -> str | None:
    return correlation_id_var.get()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    header_name = "X-Request-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get(self.header_name) or request.headers.get("X-Correlation-ID")
        try:
            cid = str(uuid.UUID(incoming)) if incoming else str(uuid.uuid4())
        except (ValueError, TypeError, AttributeError):
            cid = str(uuid.uuid4())
        token = correlation_id_var.set(cid)
        request.state.correlation_id = cid
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            correlation_id_var.reset(token)
        response.headers[self.header_name] = cid
        duration_ms = (time.perf_counter() - started) * 1000
        path = request.url.path
        observe_http(request.method, path, response.status_code)
        logger.info(
            "http_request",
            extra={
                "correlation_id": cid,
                "method": request.method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response
