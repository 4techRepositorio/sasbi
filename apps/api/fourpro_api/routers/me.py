from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fourpro_contracts.billing import MeContextResponse
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal
from fourpro_api.limiter import limiter
from fourpro_api.services.billing_service import BillingService

router = APIRouter(prefix="/me", tags=["me"])


def get_billing_service(db: Session = Depends(get_db)) -> BillingService:
    return BillingService(db)


@router.get(
    "/context",
    summary="Contexto tenant + plano (billing TICKET-010)",
    response_model=MeContextResponse,
)
@limiter.limit("120/minute")
def me_context(
    request: Request,
    principal: Annotated[Principal, Depends(get_current_principal)],
    svc: Annotated[BillingService, Depends(get_billing_service)],
) -> MeContextResponse:
    return svc.build_me_context(principal)
