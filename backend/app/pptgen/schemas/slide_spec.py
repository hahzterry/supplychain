"""Slide-level specification schemas for the pptgen pipeline."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SlideLayout(str, Enum):
    """Available slide layout types — must match frontend renderer."""
    TITLE = "title"
    SECTION_HEADER = "section_header"
    BULLETS = "bullets"
    TWO_COLUMN = "two_column"
    DATA_TABLE = "data_table"
    KPI_CARDS = "kpi_cards"
    CHART = "chart"
    BULLETS_WITH_KPIS = "bullets_with_kpis"
    CHART_WITH_BULLETS = "chart_with_bullets"
    TABLE_WITH_BULLETS = "table_with_bullets"


class ColumnContent(BaseModel):
    heading: str = ""
    bullets: list[str] = []


class TableContent(BaseModel):
    headers: list[str] = []
    rows: list[list[str]] = []


class KPICard(BaseModel):
    label: str
    value: str
    trend: str = ""


class ChartSeries(BaseModel):
    name: str
    values: list[float]


class ChartData(BaseModel):
    chart_type: str = "bar"
    labels: list[str] = []
    series: list[ChartSeries] = []


class SlideContent(BaseModel):
    """Content payload — matches frontend SlideContent interface."""
    bullets: list[str] = []
    left_column: Optional[ColumnContent] = None
    right_column: Optional[ColumnContent] = None
    table: Optional[TableContent] = None
    kpis: list[KPICard] = []
    chart_data: Optional[ChartData] = None
    columns: list[ColumnContent] = []


class SlideSpec(BaseModel):
    """Full specification for a single slide — matches frontend SlideSpec interface."""
    id: str
    title: str
    subtitle: str = ""
    layout: SlideLayout = SlideLayout.BULLETS
    content: SlideContent = SlideContent()
    speaker_notes: str = ""
    emphasis: str = "neutral"
