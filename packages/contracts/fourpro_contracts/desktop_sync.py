"""Contratos de publicação Desktop → API (TICKET-017)."""

from typing import Any

from pydantic import BaseModel, Field


class DesktopPublishDatasetRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    layer: str = "gold"


class DesktopPublishDatasetResponse(BaseModel):
    dataset_id: str
    status: str
    layer: str


class DesktopPublishDashboardRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    layout_json: dict[str, Any] = Field(default_factory=dict)
    widgets: list[dict[str, Any]] = Field(default_factory=list)


class DesktopPublishDashboardResponse(BaseModel):
    dashboard_id: str
    status: str = "published"
