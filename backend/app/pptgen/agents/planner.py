"""PlannerAgent - Creates slide outline structure using LLM.

Generates a structured slide plan based on the requested template type.
Templates:
  - weekly_sop: 8-12 slides (S&OP weekly review)
  - inventory_review: 6-10 slides (inventory deep-dive)
  - demand_review: 6-8 slides (demand/forecast review)
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from openai import AsyncAzureOpenAI

from ..schemas import (
    DeckMetadata,
    DeckRequest,
    DeckSpec,
    SlideContent,
    SlideLayout,
    SlideSpec,
)

logger = logging.getLogger(__name__)

TEMPLATE_GUIDELINES: dict[str, dict[str, Any]] = {
    "weekly_sop": {
        "slide_range": (8, 12),
        "description": "Weekly S&OP review covering KPIs, inventory health, demand, supply risks, and actions",
        "recommended_structure": [
            {"layout": "title", "purpose": "Title slide with week/period and business unit"},
            {"layout": "kpi_cards", "purpose": "Executive KPI summary (fill rate, stockout, inventory DOS, MAPE, OTD)"},
            {"layout": "bullets_with_kpis", "purpose": "Key highlights and alerts for the week"},
            {"layout": "data_table", "purpose": "Inventory positions by category/warehouse"},
            {"layout": "chart", "purpose": "Demand forecast vs actuals trend"},
            {"layout": "chart_with_bullets", "purpose": "Fill rate / service level trends with commentary"},
            {"layout": "two_column", "purpose": "Supply risks and mitigation actions"},
            {"layout": "data_table", "purpose": "Supplier performance scorecard"},
            {"layout": "bullets", "purpose": "Replenishment actions and recommendations"},
            {"layout": "table_with_bullets", "purpose": "Critical alerts requiring escalation"},
            {"layout": "bullets", "purpose": "Next steps and action items"},
            {"layout": "section_header", "purpose": "Appendix / backup slides marker"},
        ],
    },
    "inventory_review": {
        "slide_range": (6, 10),
        "description": "Inventory deep-dive covering positions, aging, risk levels, and optimization",
        "recommended_structure": [
            {"layout": "title", "purpose": "Title slide"},
            {"layout": "kpi_cards", "purpose": "Inventory KPIs (DOS, stockout rate, excess inventory)"},
            {"layout": "data_table", "purpose": "Inventory positions by SKU/category"},
            {"layout": "chart", "purpose": "Days of supply distribution by category"},
            {"layout": "two_column", "purpose": "At-risk items vs healthy items comparison"},
            {"layout": "chart_with_bullets", "purpose": "Inventory trend and commentary"},
            {"layout": "bullets_with_kpis", "purpose": "Replenishment recommendations with urgency"},
            {"layout": "bullets", "purpose": "Action items and next steps"},
        ],
    },
    "demand_review": {
        "slide_range": (6, 8),
        "description": "Demand and forecast review covering accuracy, trends, and outlook",
        "recommended_structure": [
            {"layout": "title", "purpose": "Title slide"},
            {"layout": "kpi_cards", "purpose": "Forecast accuracy KPIs (MAPE, bias)"},
            {"layout": "chart", "purpose": "Demand forecast vs actuals by category"},
            {"layout": "data_table", "purpose": "SKU-level forecast breakdown"},
            {"layout": "chart_with_bullets", "purpose": "Forecast confidence intervals and risks"},
            {"layout": "two_column", "purpose": "Demand drivers and market factors"},
            {"layout": "bullets", "purpose": "Recommendations and adjustments"},
        ],
    },
}

SYSTEM_PROMPT = """\
You are a supply chain presentation planner for AGI Food Division.
Your job is to create a slide outline (structure only, no content) for a PowerPoint deck.

AGI Food Division includes: Grand Mills (flour milling), Jenan (branded products), Animal Feed, Specialty & Industrial.

Available slide layouts:
- title: Title slide with main title and subtitle
- section_header: Section divider with section name
- bullets: Bullet-point slide (max 6 bullets)
- two_column: Two-column comparison layout
- data_table: Data table (max 8 rows)
- kpi_cards: KPI metric cards (3-5 cards)
- chart: Chart-focused slide (bar, line, pie)
- bullets_with_kpis: Bullet points alongside KPI cards
- chart_with_bullets: Chart with supporting bullet commentary
- table_with_bullets: Table with supporting bullet commentary

Rules:
1. Always start with a title slide
2. Group related content logically
3. Use section_header to separate major sections
4. Never exceed the slide range for the template
5. Each slide must have a clear, distinct purpose
6. Respond ONLY with valid JSON
"""


def _build_user_prompt(request: DeckRequest, data_context: dict[str, Any]) -> str:
    """Build the user prompt for the planner LLM call."""
    template_key = request.template
    template_info = TEMPLATE_GUIDELINES.get(template_key, TEMPLATE_GUIDELINES["weekly_sop"])
    min_slides, max_slides = template_info["slide_range"]

    prompt = f"""Create a slide outline for a "{template_key}" presentation.

Template description: {template_info["description"]}
Slide count: {min_slides} to {max_slides} slides

Recommended structure (use as guidance, adapt as needed):
{json.dumps(template_info["recommended_structure"], indent=2)}
"""

    if request.focus_area:
        prompt += f"\nFocus area: {request.focus_area}"
    if request.audience:
        prompt += f"\nAudience: {request.audience}"
    if request.sections:
        prompt += f"\nRequested sections: {', '.join(request.sections)}"

    # Summarize available data so planner knows what content is available
    data_summary_parts: list[str] = []
    if "kpis" in data_context and data_context["kpis"]:
        kpis = data_context["kpis"]
        if hasattr(kpis, "fill_rate"):
            data_summary_parts.append(
                f"KPIs available: fill_rate={kpis.fill_rate}, stockout_rate={kpis.stockout_rate}, "
                f"inventory_dos={kpis.inventory_dos}, forecast_accuracy_mape={kpis.forecast_accuracy_mape}, "
                f"on_time_delivery={kpis.on_time_delivery}, production_utilization={kpis.production_utilization}"
            )
    if "inventory" in data_context and data_context["inventory"]:
        data_summary_parts.append(f"Inventory items: {len(data_context['inventory'])} SKUs")
    if "forecasts" in data_context and data_context["forecasts"]:
        data_summary_parts.append(f"Forecasts: {len(data_context['forecasts'])} records")
    if "suppliers" in data_context and data_context["suppliers"]:
        data_summary_parts.append(f"Suppliers: {len(data_context['suppliers'])} suppliers")
    if "actions" in data_context and data_context["actions"]:
        data_summary_parts.append(f"Actions: {len(data_context['actions'])} replenishment actions")
    if "alerts" in data_context and data_context["alerts"]:
        data_summary_parts.append(f"Alerts: {len(data_context['alerts'])} active alerts")

    if data_summary_parts:
        prompt += "\n\nAvailable data for the deck:\n" + "\n".join(f"- {p}" for p in data_summary_parts)

    prompt += """

Respond with a JSON object containing a "slides" array of objects, each with:
- "title": slide title text
- "subtitle": optional subtitle text
- "layout": one of the available layouts (string value)
- "purpose": brief description of what this slide covers

Example:
{"slides": [
  {"title": "Weekly S&OP Review", "subtitle": "Week 20 — May 2026", "layout": "title", "purpose": "Title slide"},
  {"title": "Executive KPI Summary", "subtitle": "", "layout": "kpi_cards", "purpose": "Key performance metrics"}
]}
"""
    return prompt


class PlannerAgent:
    """Creates the slide outline structure for a deck."""

    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-12-01-preview",
            timeout=60.0,
        )
        self._model = model

    async def plan(self, request: DeckRequest, data_context: dict[str, Any]) -> DeckSpec:
        """Generate slide outline from request and data context.

        Args:
            request: DeckRequest with template and optional parameters.
            data_context: Dict with kpis, inventory, forecasts, suppliers, actions, alerts.

        Returns:
            DeckSpec with SlideSpec list (id, title, subtitle, layout, empty content).
        """
        logger.info("PlannerAgent: generating outline for template=%s", request.template)

        user_prompt = _build_user_prompt(request, data_context)

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)

        # Handle both {"slides": [...]} and [...] formats
        if isinstance(parsed, dict):
            outline = parsed.get("slides", parsed.get("outline", []))
        else:
            outline = parsed

        # Validate layouts and build SlideSpec objects
        valid_layouts = {layout.value for layout in SlideLayout}
        slides: list[SlideSpec] = []

        for item in outline:
            layout_str = item.get("layout", "bullets")
            if layout_str not in valid_layouts:
                layout_str = "bullets"

            slide = SlideSpec(
                id=f"slide-{uuid.uuid4().hex[:8]}",
                title=item.get("title", item.get("purpose", "Untitled")),
                subtitle=item.get("subtitle", ""),
                layout=SlideLayout(layout_str),
                content=SlideContent(),
                speaker_notes="",
            )
            slides.append(slide)

        # Enforce slide count limits
        template_info = TEMPLATE_GUIDELINES.get(request.template, TEMPLATE_GUIDELINES["weekly_sop"])
        min_slides, max_slides = template_info["slide_range"]

        if len(slides) < min_slides:
            logger.warning(
                "PlannerAgent: outline has %d slides, minimum is %d. Using as-is.",
                len(slides),
                min_slides,
            )
        elif len(slides) > max_slides:
            logger.warning(
                "PlannerAgent: outline has %d slides, truncating to %d.",
                len(slides),
                max_slides,
            )
            slides = slides[:max_slides]

        logger.info("PlannerAgent: generated %d-slide outline", len(slides))

        # Build the DeckSpec
        deck = DeckSpec(
            title=request.template.replace("_", " ").title(),
            subtitle=f"Audience: {request.audience}",
            date="",
            audience=request.audience,
            template=request.template,
            slides=slides,
            metadata=DeckMetadata(),
        )

        return deck
