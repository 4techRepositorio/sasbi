"""Contratos de governação / camadas (TICKET-012)."""

from typing import Literal

from pydantic import BaseModel, Field

DataLayer = Literal["bronze", "silver", "gold"]


class PromoteDatasetRequest(BaseModel):
    target_layer: DataLayer
    transform_version: str = Field(default="v1", min_length=1, max_length=64)


class PromoteDatasetResponse(BaseModel):
    id: str
    tenant_id: str
    source_ingestion_id: str
    layer: DataLayer
    transform_version: str
    status: str
