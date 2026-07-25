"""Catálogo de tipos de conector."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fourpro_contracts.connectors import ConnectorCatalogResponse
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal
from fourpro_api.services.data_source_service import DataSourceService

router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("", summary="Catálogo de conectores (capabilities)")
def list_connectors(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> ConnectorCatalogResponse:
    _ = principal
    return DataSourceService(db).catalog()
