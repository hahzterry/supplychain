"""PPTGen multi-agent pipeline for PowerPoint generation.

Usage:
    from app.pptgen import SupervisorAgent, DeckRequest

    supervisor = SupervisorAgent()
    deck = await supervisor.generate(request, data_context)
"""
from .agents.supervisor import SupervisorAgent
from .schemas import (
    ChartData,
    ChartSeries,
    ColumnContent,
    CritiqueIssue,
    CritiqueResult,
    DeckMetadata,
    DeckRequest,
    DeckSpec,
    KPICard,
    SlideContent,
    SlideLayout,
    SlideSpec,
    TableContent,
)

__all__ = [
    "SupervisorAgent",
    "ChartData",
    "ChartSeries",
    "ColumnContent",
    "CritiqueIssue",
    "CritiqueResult",
    "DeckMetadata",
    "DeckRequest",
    "DeckSpec",
    "KPICard",
    "SlideContent",
    "SlideLayout",
    "SlideSpec",
    "TableContent",
]
