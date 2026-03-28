from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.core.security import decode_access_token
from fourpro_api.db.session import get_db

_scheme = HTTPBearer(auto_error=False)


def get_current_principal(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Principal:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
        )
    p = decode_access_token(creds.credentials)
    if p is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    return p


def require_roles(*roles: str):
    def inner(p: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
        if p.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente",
            )
        return p

    return inner
