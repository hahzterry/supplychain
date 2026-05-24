"""Critique and repair schemas for the pptgen pipeline."""
from __future__ import annotations

from pydantic import BaseModel


class CritiqueIssue(BaseModel):
    slide_id: str = ""
    severity: str = "warning"
    category: str = ""
    description: str = ""
    fix_instruction: str = ""


class CritiqueResult(BaseModel):
    overall_score: int = 5
    pass_threshold: bool = False
    issues: list[CritiqueIssue] = []
    suggestions: list[str] = []
