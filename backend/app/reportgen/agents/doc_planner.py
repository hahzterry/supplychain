"""DocPlanner - LLM-based document structure planning agent."""
from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

from openai import AsyncOpenAI

from ..schemas import DocSection, DocSpec

logger = logging.getLogger(__name__)

# ─── Template definitions: section titles per template ────────────────────────

TEMPLATE_SECTIONS: dict[str, list[str]] = {
    "inventory_status": [
        "Executive Overview",
        "Key Performance Indicators",
        "Stock Position by Category",
        "Critical Stockout Risks",
        "Excess & Aging Inventory",
        "In-Transit & Pipeline Summary",
        "Recommendations & Next Steps",
    ],
    "demand_accuracy": [
        "Executive Overview",
        "Forecast Accuracy Metrics",
        "Accuracy by Category & Channel",
        "High-Variance SKUs",
        "Demand Driver Analysis",
        "Improvement Recommendations",
    ],
    "replenishment_plan": [
        "Executive Overview",
        "Key Replenishment Metrics",
        "Urgent Actions Summary",
        "Purchase Order Recommendations",
        "Production Scheduling",
        "Supplier Allocation Strategy",
        "Risk Mitigation Actions",
    ],
    "supplier_scorecard": [
        "Executive Overview",
        "Overall Supplier Performance",
        "Lead Time Analysis",
        "Quality & Reliability Scores",
        "Supplier Risk Assessment",
        "Strategic Recommendations",
    ],
    "executive_sop_summary": [
        "Executive Overview",
        "Performance Highlights",
        "Critical Decisions Required",
        "KPI Summary & Trends",
        "Risk Outlook",
        "Next Steps & Action Items",
    ],
    "inventory_deep_dive": [
        "Executive Summary",
        "Portfolio Health Assessment",
        "Category Analysis",
        "Stockout Exposure & Impact",
        "Obsolescence Risk",
        "Safety Stock Optimization",
        "Recommendations",
    ],
}

SYSTEM_PROMPT = """\
You are a supply chain document planner for Héroux-Devtek Inc. (Canadian aerospace).
Your role is to create a structured outline for a supply chain report.

Given the template type, audience, focus area, and summary data, produce a JSON object
matching the DocSpec schema:
{
    "title": "...",
    "subtitle": "...",
    "date": "YYYY-MM-DD",
    "author": "Atlas AI",
    "executive_summary": "Brief 2-3 sentence overview",
    "sections": [
        {"title": "Section Title", "paragraphs": [], "bullets": [], "table": null}
    ],
    "footer_text": "Héroux-Devtek — Internal Confidential"
}

Rules:
- Use the provided section titles for the template
- executive_summary should be a high-level 2-3 sentence overview based on the KPIs
- Do NOT fill paragraph/bullet content yet (leave as empty lists) — a content writer will do that
- The title should be professional and specific to the template
- The subtitle should reference the audience and/or focus area
- Return ONLY valid JSON, no markdown fences
"""


class DocPlanner:
    """
    LLM-based agent that plans document structure.

    Given a template and data context, produces a DocSpec skeleton
    (with section titles but empty content) for the DocContentWriter to fill.
    """

    def __init__(
        self,
        model: str,
        azure_endpoint: str,
        api_key: str,
    ) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key,
            timeout=60.0,
        )

    async def plan(
        self,
        template: str,
        focus_area: str,
        audience: str,
        data_context: dict[str, Any],
    ) -> DocSpec:
        """
        Plan a document structure using LLM.

        Returns a DocSpec with section titles and executive summary,
        but empty paragraph/bullet content.
        """
        section_titles = TEMPLATE_SECTIONS.get(template, TEMPLATE_SECTIONS["inventory_status"])

        # Build a compact data summary for the LLM
        data_summary = self._summarize_data(data_context)

        user_message = (
            f"Template: {template}\n"
            f"Audience: {audience}\n"
            f"Focus Area: {focus_area or 'General overview'}\n"
            f"Date: {date.today().isoformat()}\n"
            f"Section Titles: {json.dumps(section_titles)}\n\n"
            f"Data Summary:\n{data_summary}\n\n"
            f"Generate the DocSpec JSON now."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_completion_tokens=8000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or ""
            finish_reason = response.choices[0].finish_reason

            if not content.strip() or finish_reason == "length":
                logger.warning(f"[DocPlanner] Empty/truncated response (finish_reason={finish_reason}). Using fallback.")
                return self._fallback_plan(template, section_titles, audience, focus_area)

            spec_data = json.loads(content)

            # Ensure sections match template
            if "sections" not in spec_data or not spec_data["sections"]:
                spec_data["sections"] = [
                    {"title": t, "paragraphs": [], "bullets": [], "table": None}
                    for t in section_titles
                ]

            return DocSpec(**spec_data)

        except json.JSONDecodeError as e:
            logger.error(f"[DocPlanner] JSON parse failed: {e}. Using fallback plan.")
            return self._fallback_plan(template, section_titles, audience, focus_area)
        except Exception as e:
            logger.error(f"[DocPlanner] LLM call failed: {e}. Using fallback plan.")
            return self._fallback_plan(template, section_titles, audience, focus_area)

    def _summarize_data(self, data_context: dict[str, Any]) -> str:
        """Create a compact text summary of the data context for the LLM."""
        lines: list[str] = []

        # KPIs
        kpis = data_context.get("kpis")
        if kpis:
            k = kpis if isinstance(kpis, dict) else kpis.model_dump() if hasattr(kpis, "model_dump") else {}
            lines.append("KPIs:")
            lines.append(f"  Fill Rate: {k.get('fill_rate', 'N/A')}%")
            lines.append(f"  Stockout Rate: {k.get('stockout_rate', 'N/A')}%")
            lines.append(f"  Inventory Days of Supply: {k.get('inventory_dos', 'N/A')}")
            lines.append(f"  Forecast Accuracy (MAPE): {k.get('forecast_accuracy_mape', 'N/A')}%")
            lines.append(f"  On-Time Delivery: {k.get('on_time_delivery', 'N/A')}%")
            lines.append(f"  Production Utilization: {k.get('production_utilization', 'N/A')}%")

        # Inventory summary
        inventory = data_context.get("inventory", [])
        if inventory:
            count = len(inventory)
            critical = sum(1 for p in inventory if _get_risk(p) == "critical")
            warning = sum(1 for p in inventory if _get_risk(p) == "warning")
            lines.append(f"\nInventory: {count} positions, {critical} critical, {warning} warning")

        # Forecasts summary
        forecasts = data_context.get("forecasts", [])
        if forecasts:
            lines.append(f"Forecasts: {len(forecasts)} records")

        # Suppliers summary
        suppliers = data_context.get("suppliers", [])
        if suppliers:
            lines.append(f"Suppliers: {len(suppliers)} active")

        # Actions summary
        actions = data_context.get("actions", [])
        if actions:
            urgent = sum(1 for a in actions if _get_urgency(a) in ("critical", "high"))
            lines.append(f"Actions: {len(actions)} total, {urgent} urgent")

        # Alerts summary
        alerts = data_context.get("alerts", [])
        if alerts:
            lines.append(f"Alerts: {len(alerts)} open")

        return "\n".join(lines)

    def _fallback_plan(
        self,
        template: str,
        section_titles: list[str],
        audience: str,
        focus_area: str,
    ) -> DocSpec:
        """Deterministic fallback if LLM fails."""
        title_map = {
            "inventory_status": "Inventory Status Report",
            "demand_accuracy": "Demand Forecast Accuracy Report",
            "replenishment_plan": "Replenishment Action Plan",
            "supplier_scorecard": "Supplier Performance Scorecard",
            "executive_sop_summary": "Executive S&OP Summary",
            "inventory_deep_dive": "Inventory Deep-Dive Analysis",
        }

        return DocSpec(
            title=title_map.get(template, "Supply Chain Report"),
            subtitle=f"Prepared for {audience}" + (f" | Focus: {focus_area}" if focus_area else ""),
            date=date.today().isoformat(),
            author="Atlas AI",
            executive_summary="This report provides a comprehensive overview of the current supply chain status.",
            sections=[
                DocSection(title=t, paragraphs=[], bullets=[], table=None)
                for t in section_titles
            ],
            footer_text="Héroux-Devtek — Internal Confidential",
        )


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_risk(item: Any) -> str:
    """Safely extract risk_level string from an inventory item."""
    if isinstance(item, dict):
        rl = item.get("risk_level", "")
        return rl.value if hasattr(rl, "value") else str(rl).lower()
    if hasattr(item, "risk_level"):
        rl = item.risk_level
        return rl.value if hasattr(rl, "value") else str(rl).lower()
    return ""


def _get_urgency(item: Any) -> str:
    """Safely extract urgency string from an action item."""
    if isinstance(item, dict):
        return str(item.get("urgency", "")).lower()
    if hasattr(item, "urgency"):
        return str(item.urgency).lower()
    return ""
