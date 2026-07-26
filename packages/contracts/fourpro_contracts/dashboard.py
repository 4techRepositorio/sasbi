"""Contratos de dashboards (TICKET-011)."""

from typing import Any, Literal

from pydantic import BaseModel, Field

WidgetType = Literal["kpi", "table", "chart"]


class DashboardWidgetIn(BaseModel):
    widget_type: WidgetType
    title: str = Field(min_length=1, max_length=200)
    dataset_id: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    position: dict[str, Any] = Field(default_factory=dict)


class DashboardWidgetOut(DashboardWidgetIn):
    id: str
    dataset_available: bool = True


class DashboardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    layout_json: dict[str, Any] = Field(default_factory=dict)
    widgets: list[DashboardWidgetIn] = Field(default_factory=list)


class DashboardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    layout_json: dict[str, Any] | None = None
    widgets: list[DashboardWidgetIn] | None = None


class DashboardSummary(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: str | None = None
    updated_at: str
    widget_count: int


class DashboardDetail(DashboardSummary):
    layout_json: dict[str, Any]
    widgets: list[DashboardWidgetOut]
    created_at: str
    created_by_user_id: str | None = None


class PaginatedDashboardList(BaseModel):
    items: list[DashboardSummary]
    total: int
    limit: int
    offset: int


class DashboardExportPackage(BaseModel):
    """Snapshot exportável (MVP — JSON, não PNG/PDF)."""

    dashboard: DashboardDetail
    exported_at: str
    format: Literal["json_snapshot"] = "json_snapshot"
