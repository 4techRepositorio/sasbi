"""Chave slowapi por cliente: IP ou X-Forwarded-For (proxy de confiança)."""

from fastapi import Request
from slowapi.util import get_remote_address

from fourpro_api.config import get_settings


def client_key_for_rate_limit(request: Request) -> str:
    """
    Com RATE_LIMIT_TRUST_PROXY=true, usa o endereço mais à esquerda de X-Forwarded-For
    (cliente original quando cada proxy acrescenta o seu).
    Só activar se o edge da rede **substituir** ou **validar** X-Forwarded-For.
    """
    if get_settings().rate_limit_trust_proxy:
        xf = request.headers.get("x-forwarded-for")
        if xf:
            left = xf.split(",")[0].strip()
            if left:
                return left
    return get_remote_address(request)
