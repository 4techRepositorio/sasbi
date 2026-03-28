from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.core.security import decode_access_token
from fourpro_api.db.session import get_db
from fourpro_api.repositories.membership_repository import MembershipRepository
from fourpro_api.repositories.user_repository import UserRepository

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
    claims = decode_access_token(creds.credentials)
    if claims is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    members = MembershipRepository(db)
    role = members.get_role(claims.user_id, claims.tenant_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso ao tenant revogado ou sessão inválida",
        )
    users = UserRepository(db)
    user = users.get_by_id(claims.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador inválido ou inativo",
        )
    return Principal(user_id=claims.user_id, tenant_id=claims.tenant_id, role=role)


def require_roles(*roles: str):
    def inner(p: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
        if p.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente",
            )
        return p

    return inner
