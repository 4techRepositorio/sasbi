from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fourpro_contracts.semantic import QueryRequest, QueryResponse
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal
from fourpro_api.limiter import limiter
from fourpro_api.services.query_service import QueryService

router = APIRouter(tags=["query"])


def _svc(db: Annotated[Session, Depends(get_db)]) -> QueryService:
    return QueryService(db)


@router.post("/query", summary="Query agregada sobre modelo semântico (TICKET-016)")
@limiter.limit("60/minute")
def run_query(
    request: Request,
    body: QueryRequest,
    principal: Annotated[Principal, Depends(get_current_principal)],
    svc: Annotated[QueryService, Depends(_svc)],
) -> QueryResponse:
    return svc.execute(principal.tenant_id, body)
