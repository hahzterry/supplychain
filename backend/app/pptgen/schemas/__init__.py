"""PPTGen schema re-exports."""

from .slide_spec import (
    ChartData,
    ChartSeries,
    ColumnContent,
    KPICard,
    SlideContent,
    SlideLayout,
    SlideSpec,
    TableContent,
)
from .deck_spec import (
    DeckMetadata,
    DeckRequest,
    DeckSpec,
)
from .critique_spec import (
    CritiqueIssue,
    CritiqueResult,
)

__all__ = [
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
