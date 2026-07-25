"""Contratos de dashboards / workspace (TICKET-011)."""

from typing import Any, Literal

from pydantic import BaseModel, Field

WidgetType = Literal["kpi", "bar_chart", "line_chart", "table", "text"]
DashboardStatus = Literal["draft", "published", "archived"]


class WidgetQueryRef(BaseModel):
    semantic_model_id: str | None = None
    measures: list[dict[str, Any]] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    limit: int = 100


class DashboardWidget(BaseModel):
    id: str
    type: WidgetType
    title: str = ""
    x: int = 0
    y: int = 0
    w: int = 4
    h: int = 3
    query: WidgetQueryRef | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class DashboardLayout(BaseModel):
    version: int = 1
    columns: int = 12
    widgets: list[DashboardWidget] = Field(default_factory=list)


class DashboardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    layout: DashboardLayout = Field(default_factory=DashboardLayout)


class DashboardPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    layout: DashboardLayout | None = None
    status: DashboardStatus | None = None


class DashboardItem(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    status: DashboardStatus
    layout: DashboardLayout
    version: int
    created_by_user_id: str | None = None
    created_at: str
    updated_at: str
    published_at: str | None = None


class PaginatedDashboardList(BaseModel):
    items: list[DashboardItem]
    total: int
    limit: int
    offset: int


class DashboardPublishResponse(BaseModel):
    id: str
    status: Literal["published"]
    version: int
    published_at: str
