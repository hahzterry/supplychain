"""ContentAgent - Fills slides with real data using LLM.

Takes the DeckSpec outline from PlannerAgent and populates each slide with
actual supply chain data, formatted appropriately for the layout type.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from ..schemas import (
    ChartData,
    ChartSeries,
    ColumnContent,
    DeckSpec,
    KPICard,
    SlideContent,
    SlideLayout,
    SlideSpec,
    TableContent,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a supply chain content writer for Héroux-Devtek Inc. presentations.
Your job is to fill slide content with real data provided in the context.

Héroux-Devtek Inc. business units:
- Longueuil QC: landing gear assembly & integration
- Kitchener ON: actuation systems & flight-critical components
- Animal Feed: livestock feed production
- Specialty & Industrial: specialty ingredients and industrial products

Guidelines:
1. Use the actual data provided - never invent numbers
2. Keep bullet points concise (max 120 characters each)
3. Maximum 6 bullets per slide
4. Tables should have max 8 rows
5. KPI cards should show 3-5 metrics
6. Format numbers clearly (e.g., "94.2%" not "0.942")
7. Include speaker notes with additional context
8. Use business-appropriate language (executive audience)
9. Highlight risks and action items clearly
10. Respond ONLY with valid JSON matching the specified schema
"""


def _format_data_context(data_context: dict[str, Any]) -> str:
    """Format the data context into a readable string for the LLM."""
    sections: list[str] = []

    if "kpis" in data_context and data_context["kpis"]:
        kpis = data_context["kpis"]
        if hasattr(kpis, "model_dump"):
            kpi_dict = kpis.model_dump()
        elif hasattr(kpis, "__dict__"):
            kpi_dict = {
                "fill_rate": getattr(kpis, "fill_rate", None),
                "stockout_rate": getattr(kpis, "stockout_rate", None),
                "inventory_dos": getattr(kpis, "inventory_dos", None),
                "forecast_accuracy_mape": getattr(kpis, "forecast_accuracy_mape", None),
                "on_time_delivery": getattr(kpis, "on_time_delivery", None),
                "production_utilization": getattr(kpis, "production_utilization", None),
            }
        else:
            kpi_dict = kpis
        sections.append(f"## KPI Metrics\n{json.dumps(kpi_dict, indent=2, default=str)}")

    if "inventory" in data_context and data_context["inventory"]:
        inv_items = data_context["inventory"]
        inv_data = []
        for item in inv_items[:20]:
            if hasattr(item, "model_dump"):
                inv_data.append(item.model_dump())
            elif hasattr(item, "__dict__"):
                inv_data.append({
                    "sku_name": getattr(item, "sku_name", ""),
                    "category": getattr(item, "category", object()).value if hasattr(getattr(item, "category", None), "value") else str(getattr(item, "category", "")),
                    "warehouse": getattr(item, "warehouse", ""),
                    "available_stock": getattr(item, "available_stock", 0),
                    "days_of_supply": getattr(item, "days_of_supply", 0),
                    "risk_level": getattr(item, "risk_level", object()).value if hasattr(getattr(item, "risk_level", None), "value") else str(getattr(item, "risk_level", "")),
                })
            elif isinstance(item, dict):
                inv_data.append(item)
        sections.append(f"## Inventory Positions ({len(inv_items)} total, showing top 20)\n{json.dumps(inv_data, indent=2, default=str)}")

    if "forecasts" in data_context and data_context["forecasts"]:
        fc_items = data_context["forecasts"]
        fc_data = []
        for item in fc_items[:15]:
            if hasattr(item, "model_dump"):
                fc_data.append(item.model_dump())
            elif hasattr(item, "__dict__"):
                fc_data.append({
                    "sku_id": getattr(item, "sku_id", ""),
                    "week": str(getattr(item, "week", "")),
                    "point_forecast": getattr(item, "point_forecast", 0),
                    "lower_80": getattr(item, "lower_80", 0),
                    "upper_80": getattr(item, "upper_80", 0),
                })
            elif isinstance(item, dict):
                fc_data.append(item)
        sections.append(f"## Demand Forecasts ({len(fc_items)} total, showing top 15)\n{json.dumps(fc_data, indent=2, default=str)}")

    if "suppliers" in data_context and data_context["suppliers"]:
        sup_items = data_context["suppliers"]
        sup_data = []
        for item in sup_items[:10]:
            if hasattr(item, "model_dump"):
                sup_data.append(item.model_dump())
            elif hasattr(item, "__dict__"):
                sup_data.append({
                    "name": getattr(item, "name", ""),
                    "country": getattr(item, "country", ""),
                    "avg_lead_time_days": getattr(item, "avg_lead_time_days", 0),
                    "reliability_score": getattr(item, "reliability_score", 0),
                    "quality_score": getattr(item, "quality_score", 0),
                })
            elif isinstance(item, dict):
                sup_data.append(item)
        sections.append(f"## Suppliers ({len(sup_items)} total)\n{json.dumps(sup_data, indent=2, default=str)}")

    if "actions" in data_context and data_context["actions"]:
        act_items = data_context["actions"]
        act_data = []
        for item in act_items[:10]:
            if hasattr(item, "model_dump"):
                act_data.append(item.model_dump())
            elif hasattr(item, "__dict__"):
                act_data.append({
                    "sku_name": getattr(item, "sku_name", ""),
                    "action_type": getattr(item, "action_type", ""),
                    "recommended_qty": getattr(item, "recommended_qty", 0),
                    "urgency": getattr(item, "urgency", ""),
                    "confidence": getattr(item, "confidence", 0),
                })
            elif isinstance(item, dict):
                act_data.append(item)
        sections.append(f"## Replenishment Actions ({len(act_items)} total)\n{json.dumps(act_data, indent=2, default=str)}")

    if "alerts" in data_context and data_context["alerts"]:
        alert_items = data_context["alerts"]
        alert_data = []
        for item in alert_items[:10]:
            if hasattr(item, "model_dump"):
                alert_data.append(item.model_dump())
            elif hasattr(item, "__dict__"):
                alert_data.append({
                    "title": getattr(item, "title", ""),
                    "severity": getattr(item, "severity", ""),
                    "description": getattr(item, "description", ""),
                })
            elif isinstance(item, dict):
                alert_data.append(item)
        sections.append(f"## Supply Alerts ({len(alert_items)} total)\n{json.dumps(alert_data, indent=2, default=str)}")

    return "\n\n".join(sections)


def _get_schema_hint(layout: SlideLayout) -> str:
    """Return JSON schema hint based on layout type."""
    base = '{"title": "string", "subtitle": "string", "speaker_notes": "string"'

    hints: dict[str, str] = {
        "title": base + "}",
        "section_header": base + "}",
        "bullets": base + ', "bullets": ["string (max 120 chars)", ...max 6]}',
        "two_column": base + ', "left_column": {"heading": "str", "bullets": [...]}, "right_column": {"heading": "str", "bullets": [...]}}',
        "data_table": base + ', "table": {"headers": ["str", ...], "rows": [["str", ...], ...max 8 rows]}}',
        "kpi_cards": base + ', "kpis": [{"label": "str", "value": "str", "trend": "up|down|flat"}, ...3-5 items]}',
        "chart": base + ', "chart_data": {"chart_type": "bar|line|pie|stacked_bar", "labels": ["str", ...], "series": [{"name": "str", "values": [float, ...]}, ...]}}',
        "bullets_with_kpis": base + ', "bullets": ["str", ...], "kpis": [{"label": "str", "value": "str", "trend": "up|down|flat"}, ...]}',
        "chart_with_bullets": base + ', "bullets": ["str", ...], "chart_data": {"chart_type": "str", "labels": [...], "series": [{"name": "str", "values": [...]}]}}',
        "table_with_bullets": base + ', "bullets": ["str", ...], "table": {"headers": [...], "rows": [[...], ...max 8]}}',
    }

    return hints.get(layout.value, base + ', "bullets": ["string", ...]}')


def _build_slide_prompt(slide: SlideSpec) -> str:
    """Build the content generation prompt for a single slide."""
    schema_hint = _get_schema_hint(slide.layout)

    return f"""Fill content for slide "{slide.title}".
Layout: {slide.layout.value}

Respond with JSON matching this schema:
{schema_hint}

Important:
- "title" is required (use or improve the existing title)
- Keep bullets under 120 characters, max 6 bullets
- Tables max 8 rows
- KPI cards: 3-5 items with label, value, and optional trend (up/down/flat)
- Charts need chart_type (bar/line/pie/stacked_bar), labels, and series with numeric values
- Speaker notes should add context not on the slide
"""


class ContentAgent:
    """Fills slide outlines with actual supply chain data."""

    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key,
            timeout=60.0,
        )
        self._model = model

    async def write(self, deck: DeckSpec, data_context: dict[str, Any]) -> DeckSpec:
        """Fill all slides in the deck with content from data_context.

        Args:
            deck: DeckSpec with outline slides from PlannerAgent.
            data_context: Dict with kpis, inventory, forecasts, suppliers, actions, alerts.

        Returns:
            DeckSpec with fully populated slide content.
        """
        import asyncio

        logger.info("ContentAgent: filling %d slides with data", len(deck.slides))

        formatted_data = _format_data_context(data_context)

        # Process slides concurrently (max 4 at a time to avoid rate limits)
        semaphore = asyncio.Semaphore(4)

        async def fill_with_limit(slide: SlideSpec) -> SlideSpec:
            async with semaphore:
                return await self._fill_single_slide(slide, formatted_data)

        filled_slides = await asyncio.gather(
            *(fill_with_limit(slide) for slide in deck.slides)
        )

        deck.slides = list(filled_slides)
        logger.info("ContentAgent: completed %d slides", len(filled_slides))
        return deck

    async def _fill_single_slide(
        self,
        slide: SlideSpec,
        formatted_data: str,
    ) -> SlideSpec:
        """Fill a single slide with content."""
        user_prompt = _build_slide_prompt(slide)
        user_prompt += f"\n\nAvailable data:\n{formatted_data}"

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
                max_completion_tokens=8000,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content or "{}"
            if not raw.strip() or raw.strip() == "{}":
                logger.warning("ContentAgent: empty response for slide '%s'", slide.title)
                return slide
            data = json.loads(raw)

            # Handle nested response formats
            if "content" in data and isinstance(data["content"], dict):
                data = data["content"]

            slide = self._parse_slide_response(data, slide)

        except Exception as e:
            logger.error("ContentAgent: failed to fill slide %s: %s", slide.id, e)
            slide.content = SlideContent(
                bullets=["Content generation failed - please retry"],
            )
            slide.speaker_notes = "Error occurred during content generation."

        return slide

    def _parse_slide_response(self, data: dict[str, Any], slide: SlideSpec) -> SlideSpec:
        """Parse LLM JSON response into the slide."""
        # Update title/subtitle if provided
        if data.get("title"):
            slide.title = data["title"]
        if data.get("subtitle"):
            slide.subtitle = data["subtitle"]
        if data.get("speaker_notes"):
            slide.speaker_notes = data["speaker_notes"]

        slide.content = self._parse_content(data, slide.layout)
        return slide

    def _parse_content(self, data: dict[str, Any], layout: SlideLayout) -> SlideContent:
        """Parse LLM JSON response into SlideContent."""
        bullets = data.get("bullets", [])
        # Enforce limits
        bullets = bullets[:6]
        bullets = [b[:120] if len(b) > 120 else b for b in bullets]

        left_column = None
        right_column = None
        table = None
        kpis: list[KPICard] = []
        chart_data = None

        if "left_column" in data and data["left_column"]:
            lc = data["left_column"]
            left_column = ColumnContent(
                heading=lc.get("heading", ""),
                bullets=lc.get("bullets", [])[:6],
            )

        if "right_column" in data and data["right_column"]:
            rc = data["right_column"]
            right_column = ColumnContent(
                heading=rc.get("heading", ""),
                bullets=rc.get("bullets", [])[:6],
            )

        if "table" in data and data["table"]:
            t = data["table"]
            rows = [[str(cell) for cell in row] for row in t.get("rows", [])]
            table = TableContent(
                headers=t.get("headers", []),
                rows=rows[:8],
            )

        if "kpis" in data and data["kpis"]:
            for card in data["kpis"][:5]:
                kpis.append(
                    KPICard(
                        label=card.get("label", ""),
                        value=str(card.get("value", "")),
                        trend=card.get("trend", ""),
                    )
                )

        if "chart_data" in data and data["chart_data"]:
            cd = data["chart_data"]
            series: list[ChartSeries] = []
            for s in cd.get("series", []):
                values = []
                for v in s.get("values", []):
                    try:
                        values.append(float(v))
                    except (ValueError, TypeError):
                        values.append(0.0)
                series.append(
                    ChartSeries(
                        name=s.get("name", ""),
                        values=values,
                    )
                )
            chart_data = ChartData(
                chart_type=cd.get("chart_type", "bar"),
                labels=cd.get("labels", []),
                series=series,
            )

        return SlideContent(
            bullets=bullets,
            left_column=left_column,
            right_column=right_column,
            table=table,
            kpis=kpis,
            chart_data=chart_data,
        )
