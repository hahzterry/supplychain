"""DesignerAgent - Assigns layout and emphasis to each slide.

Analyzes slide content to determine the best layout, ensures visual variety,
and validates that assigned layouts match available content.
Uses LLM for nuanced decisions with rules-based fallback.
"""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from ..schemas import DeckSpec, SlideLayout, SlideSpec

logger = logging.getLogger(__name__)

# Emphasis defaults per layout type
EMPHASIS_RULES: dict[str, str] = {
    "title": "bold",
    "section_header": "bold",
    "bullets": "neutral",
    "two_column": "neutral",
    "data_table": "neutral",
    "kpi_cards": "highlight",
    "chart": "highlight",
    "bullets_with_kpis": "highlight",
    "chart_with_bullets": "highlight",
    "table_with_bullets": "neutral",
}

SYSTEM_PROMPT = """\
You are a presentation designer for Héroux-Devtek Inc.'s supply chain team.
Your job is to review slides and assign the best layout and emphasis for each one.

Available layouts:
- title: Title slide with main title and subtitle
- section_header: Section divider
- bullets: Bullet-point slide
- two_column: Two-column comparison
- data_table: Data table
- kpi_cards: KPI metric cards
- chart: Chart-focused slide
- bullets_with_kpis: Bullets with KPI cards
- chart_with_bullets: Chart with commentary
- table_with_bullets: Table with commentary

Emphasis options: "bold", "highlight", "neutral", "subtle"

Design rules:
1. Layout must match available content (e.g., don't assign "chart" if no chart_data exists)
2. No same layout 3 times in a row (visual variety)
3. Title slides should be "bold" emphasis
4. KPI and chart slides should be "highlight" emphasis
5. Supporting/detail slides should be "neutral" or "subtle"
6. Ensure narrative flow — build from overview to detail to action

Respond with JSON: {"slides": [{"id": "slide-xxx", "layout": "...", "emphasis": "..."}, ...]}
"""


def _content_supports_layout(slide: SlideSpec, layout: SlideLayout) -> bool:
    """Check if slide content has the data needed for a given layout."""
    content = slide.content

    if layout == SlideLayout.TWO_COLUMN:
        return content.left_column is not None and content.right_column is not None
    elif layout == SlideLayout.DATA_TABLE:
        return content.table is not None
    elif layout == SlideLayout.KPI_CARDS:
        return len(content.kpis) > 0
    elif layout == SlideLayout.CHART:
        return content.chart_data is not None
    elif layout == SlideLayout.BULLETS_WITH_KPIS:
        return len(content.kpis) > 0 and len(content.bullets) > 0
    elif layout == SlideLayout.CHART_WITH_BULLETS:
        return content.chart_data is not None and len(content.bullets) > 0
    elif layout == SlideLayout.TABLE_WITH_BULLETS:
        return content.table is not None and len(content.bullets) > 0
    elif layout in (SlideLayout.TITLE, SlideLayout.SECTION_HEADER, SlideLayout.BULLETS):
        return True
    return True


def _ensure_variety(slides: list[SlideSpec]) -> list[SlideSpec]:
    """Ensure no layout repeats 3+ times in a row."""
    for i in range(2, len(slides)):
        if (
            slides[i].layout == slides[i - 1].layout == slides[i - 2].layout
            and slides[i].layout not in (SlideLayout.TITLE, SlideLayout.SECTION_HEADER)
        ):
            # Change emphasis to break monotony at minimum
            if slides[i].emphasis == "neutral":
                slides[i].emphasis = "subtle"
            # Try to swap to bullets if the content supports it
            if slides[i].layout != SlideLayout.BULLETS and len(slides[i].content.bullets) > 0:
                slides[i].layout = SlideLayout.BULLETS
    return slides


def _rules_based_design(slides: list[SlideSpec]) -> list[SlideSpec]:
    """Apply rules-based layout validation and emphasis assignment."""
    for slide in slides:
        # Validate that current layout is supported by content
        if not _content_supports_layout(slide, slide.layout):
            slide.layout = SlideLayout.BULLETS

        # Assign emphasis based on layout
        slide.emphasis = EMPHASIS_RULES.get(slide.layout.value, "neutral")

    return _ensure_variety(slides)


class DesignerAgent:
    """Assigns visual layout and emphasis to slides."""

    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key,
            timeout=60.0,
        )
        self._model = model

    async def design(self, deck: DeckSpec) -> DeckSpec:
        """Assign layout and emphasis to each slide in the deck.

        Uses LLM for contextual design decisions, with rules-based fallback.

        Args:
            deck: DeckSpec with populated slides from ContentAgent.

        Returns:
            DeckSpec with layout and emphasis finalized.
        """
        logger.info("DesignerAgent: designing %d slides", len(deck.slides))

        # Try LLM-based design first
        try:
            deck.slides = await self._llm_design(deck.slides)
        except Exception as e:
            logger.warning("DesignerAgent: LLM design failed, using rules fallback: %s", e)
            deck.slides = _rules_based_design(deck.slides)

        # Always validate with rules as a safety net
        for slide in deck.slides:
            if not _content_supports_layout(slide, slide.layout):
                slide.layout = SlideLayout.BULLETS
                slide.emphasis = "neutral"

        deck.slides = _ensure_variety(deck.slides)

        logger.info("DesignerAgent: design complete")
        return deck

    async def _llm_design(self, slides: list[SlideSpec]) -> list[SlideSpec]:
        """Use LLM to assign layout and emphasis."""
        slides_summary = []
        for slide in slides:
            content = slide.content
            slides_summary.append({
                "id": slide.id,
                "title": slide.title,
                "current_layout": slide.layout.value,
                "has_bullets": len(content.bullets) > 0,
                "bullet_count": len(content.bullets),
                "has_left_column": content.left_column is not None,
                "has_right_column": content.right_column is not None,
                "has_table": content.table is not None,
                "has_kpis": len(content.kpis) > 0,
                "kpi_count": len(content.kpis),
                "has_chart_data": content.chart_data is not None,
            })

        user_prompt = f"""Review these slides and assign the optimal layout and emphasis for each:

{json.dumps(slides_summary, indent=2)}

Remember:
- Layout must match available content
- No same layout 3 times in a row
- Vary emphasis for visual interest
- Build narrative: overview -> detail -> action

Respond with JSON: {{"slides": [{{"id": "...", "layout": "...", "emphasis": "..."}}]}}
"""

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_completion_tokens=8000,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        if not raw.strip() or raw.strip() == "{}":
            logger.warning("DesignerAgent: empty response, returning deck unchanged")
            return deck

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("DesignerAgent: invalid JSON, returning deck unchanged")
            return deck

        design_list = parsed.get("slides", [])
        valid_layouts = {layout.value for layout in SlideLayout}
        valid_emphasis = {"bold", "highlight", "neutral", "subtle"}

        # Build lookup by id
        design_map: dict[str, dict[str, str]] = {}
        for item in design_list:
            slide_id = item.get("id", "")
            if slide_id:
                design_map[slide_id] = item

        # Apply LLM decisions
        for slide in slides:
            if slide.id in design_map:
                design = design_map[slide.id]
                new_layout = design.get("layout", slide.layout.value)
                new_emphasis = design.get("emphasis", "neutral")

                if new_layout in valid_layouts:
                    slide.layout = SlideLayout(new_layout)
                if new_emphasis in valid_emphasis:
                    slide.emphasis = new_emphasis

        return slides
