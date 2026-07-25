from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fourpro_contracts.semantic import (
    PaginatedSemanticModelList,
    SemanticModelCreate,
    SemanticModelItem,
    SemanticModelPatch,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.services.semantic_model_service import SemanticModelService

router = APIRouter(prefix="/semantic-models", tags=["semantic-models"])


def _svc(db: Annotated[Session, Depends(get_db)]) -> SemanticModelService:
    return SemanticModelService(db)


@router.get("", summary="Listar modelos semânticos do tenant (TICKET-016)")
def list_semantic_models(
    principal: Annotated[Principal, Depends(get_current_principal)],
    svc: Annotated[SemanticModelService, Depends(_svc)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PaginatedSemanticModelList:
    return svc.list(principal.tenant_id, limit=limit, offset=offset)


@router.post("", summary="Criar modelo semântico", status_code=status.HTTP_201_CREATED)
def create_semantic_model(
    body: SemanticModelCreate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[SemanticModelService, Depends(_svc)],
) -> SemanticModelItem:
    return svc.create(principal.tenant_id, body)


@router.get("/{model_id}", summary="Detalhe de modelo semântico")
def get_semantic_model(
    model_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    svc: Annotated[SemanticModelService, Depends(_svc)],
) -> SemanticModelItem:
    return svc.get(principal.tenant_id, model_id)


@router.patch("/{model_id}", summary="Actualizar modelo semântico")
def patch_semantic_model(
    model_id: UUID,
    body: SemanticModelPatch,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[SemanticModelService, Depends(_svc)],
) -> SemanticModelItem:
    return svc.patch(principal.tenant_id, model_id, body)


@router.delete(
    "/{model_id}",
    summary="Eliminar modelo semântico",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_semantic_model(
    model_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[SemanticModelService, Depends(_svc)],
) -> Response:
    svc.delete(principal.tenant_id, model_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
