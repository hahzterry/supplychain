"""Schemas for report generation pipeline."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Enums ───────────────────────────────────────────────────────────────────

class ReportFormat(str, Enum):
    PPTX = "pptx"
    DOCX = "docx"
    XLSX = "xlsx"
    PDF = "pdf"


# ─── Document (DOCX/PDF) Schemas ─────────────────────────────────────────────

class TableContent(BaseModel):
    """A simple table embedded within a document section."""
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)


class DocSection(BaseModel):
    """A single section of a document report."""
    title: str
    paragraphs: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    table: Optional[TableContent] = None


class DocSpec(BaseModel):
    """Complete specification for a DOCX/PDF report."""
    title: str
    subtitle: str = ""
    date: str = ""
    author: str = "Atlas AI"
    executive_summary: str = ""
    sections: list[DocSection] = Field(default_factory=list)
    footer_text: str = "Héroux-Devtek — Internal Confidential"


# ─── Spreadsheet (XLSX) Schemas ──────────────────────────────────────────────

class SheetColumn(BaseModel):
    """Column definition for a spreadsheet."""
    header: str
    width: int = 20
    data_type: str = "string"  # string, number, percent, date


class SheetRow(BaseModel):
    """A single data row with optional highlight."""
    values: list[str] = Field(default_factory=list)
    highlight: str = "none"  # none, red, yellow, green


class SheetSpec(BaseModel):
    """Complete specification for an XLSX report."""
    title: str
    sheet_name: str = "Sheet1"
    columns: list[SheetColumn] = Field(default_factory=list)
    rows: list[SheetRow] = Field(default_factory=list)
    summary_row: Optional[list[str]] = None
    notes: list[str] = Field(default_factory=list)


# ─── Request Schema ──────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    """Incoming request to generate a report."""
    template: str = "inventory_status"
    format: ReportFormat = ReportFormat.DOCX
    focus_area: str = ""
    audience: str = "Internal - S&OP Committee"
