"""Deck-level specification schemas for the pptgen pipeline."""
from __future__ import annotations

from pydantic import BaseModel

from .slide_spec import SlideSpec


class DeckMetadata(BaseModel):
    """Metadata for the generated deck."""
    classification: str = "Internal — Confidential"
    generated_by: str = "Rashid AI"


class DeckSpec(BaseModel):
    """Full specification for a PowerPoint deck — matches frontend DeckSpec type."""
    title: str
    subtitle: str = ""
    date: str = ""
    audience: str = "S&OP Committee"
    template: str = "weekly_sop"
    slides: list[SlideSpec] = []
    metadata: DeckMetadata = DeckMetadata()


class DeckRequest(BaseModel):
    """Request parameters for deck generation."""
    template: str = "weekly_sop"
    focus_area: str = ""
    audience: str = "S&OP Committee"
    sections: list[str] | None = None
