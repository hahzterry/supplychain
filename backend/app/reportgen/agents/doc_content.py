"""DocContentWriter - LLM agent that fills document sections with content."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from ..schemas import DocSection, DocSpec, TableContent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a senior supply chain analyst writing a professional document section
for Héroux-Devtek Inc. (Canadian aerospace landing gear manufacturer).

Given a section title, the full data context, and the report audience, produce
rich professional content for that section.

Return a JSON object:
{
    "paragraphs": ["paragraph1", "paragraph2"],
    "bullets": ["bullet point 1", "bullet point 2"],
    "table": null or {"headers": [...], "rows": [[...], [...]]}
}

Rules:
- Write in executive tone: concise, data-driven, professional
- Use actual numbers from the data provided — do NOT fabricate values
- paragraphs: 1-3 paragraphs of analytical narrative
- bullets: 3-6 key takeaways or action items
- table: include a table ONLY when the section naturally lends itself to tabular data
  (e.g., KPI summaries, top-N lists, comparisons). Otherwise set to null.
- For tables, keep to 5-8 rows maximum for readability
- Reference specific SKUs, suppliers, or categories when relevant
- Return ONLY valid JSON, no markdown fences
"""


class DocContentWriter:
    """
    LLM-based agent that fills each section of a DocSpec with paragraphs,
    bullets, and optional tables using real supply chain data.
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

    async def write(
        self,
        doc_plan: DocSpec,
        data_context: dict[str, Any],
        audience: str,
    ) -> DocSpec:
        """
        Fill all sections of the doc plan with LLM-generated content.

        Args:
            doc_plan: DocSpec skeleton from DocPlanner (sections have titles only).
            data_context: Full supply chain data context.
            audience: Target audience string.

        Returns:
            DocSpec with fully populated sections.
        """
        data_text = self._format_data_context(data_context)
        filled_sections: list[DocSection] = []

        for section in doc_plan.sections:
            try:
                filled = await self._fill_section(section.title, data_text, audience)
                filled_sections.append(filled)
            except Exception as e:
                logger.error(f"[DocContentWriter] Error filling section '{section.title}': {e}")
                # Keep section with minimal fallback content
                filled_sections.append(
                    DocSection(
                        title=section.title,
                        paragraphs=["Content generation unavailable for this section."],
                        bullets=[],
                        table=None,
                    )
                )

        return DocSpec(
            title=doc_plan.title,
            subtitle=doc_plan.subtitle,
            date=doc_plan.date,
            author=doc_plan.author,
            executive_summary=doc_plan.executive_summary,
            sections=filled_sections,
            footer_text=doc_plan.footer_text,
        )

    async def _fill_section(
        self,
        section_title: str,
        data_text: str,
        audience: str,
    ) -> DocSection:
        """Call LLM to generate content for a single section."""
        user_message = (
            f"Section Title: {section_title}\n"
            f"Audience: {audience}\n\n"
            f"Data Context:\n{data_text}\n\n"
            f"Write the content for this section."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.4,
                max_completion_tokens=8000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or ""

            if not content.strip() or content.strip() == "{}":
                logger.warning(f"[DocContentWriter] Empty response for '{section_title}'. Using fallback.")
                return self._fallback_section(section_title, data_text)

            data = json.loads(content)

            # Parse table if present
            table = None
            if data.get("table") and isinstance(data["table"], dict):
                table = TableContent(
                    headers=data["table"].get("headers", []),
                    rows=data["table"].get("rows", []),
                )

            result = DocSection(
                title=section_title,
                paragraphs=data.get("paragraphs", []),
                bullets=data.get("bullets", []),
                table=table,
            )

            if not result.paragraphs and not result.bullets:
                logger.warning(f"[DocContentWriter] No content returned for '{section_title}'. Using fallback.")
                return self._fallback_section(section_title, data_text)

            return result

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"[DocContentWriter] Failed for '{section_title}': {e}. Using fallback.")
            return self._fallback_section(section_title, data_text)

    def _fallback_section(self, section_title: str, data_text: str) -> DocSection:
        """Deterministic fallback when LLM fails to generate content."""
        title_lower = section_title.lower()
        paragraphs: list[str] = []
        bullets: list[str] = []
        table = None

        # Extract key values from data text
        lines = data_text.split("\n")
        kpi_lines = [l.strip() for l in lines if ":" in l and any(k in l for k in ["Fill Rate", "Stockout", "DOS", "MAPE", "Delivery", "Utilization", "Capital", "Alerts"])]

        if "executive" in title_lower or "overview" in title_lower:
            paragraphs.append(
                "This section provides a high-level assessment of current supply chain performance. "
                "Key metrics are summarized below with status indicators against target thresholds."
            )
            for kl in kpi_lines[:6]:
                bullets.append(kl.strip())

        elif "kpi" in title_lower or "performance" in title_lower or "highlight" in title_lower:
            paragraphs.append(
                "The following key performance indicators reflect the current operational state "
                "of the Héroux-Devtek supply chain network."
            )
            if kpi_lines:
                table = TableContent(
                    headers=["Metric", "Value"],
                    rows=[[kl.split(":")[0].strip(), kl.split(":", 1)[1].strip()] for kl in kpi_lines if ":" in kl],
                )

        elif "risk" in title_lower or "alert" in title_lower:
            alert_lines = [l.strip() for l in lines if "CRITICAL" in l.upper() or "WARNING" in l.upper()]
            paragraphs.append(
                "The risk outlook identifies supply chain vulnerabilities requiring immediate attention. "
                "Critical alerts demand escalated response within 24-48 hours."
            )
            for al in alert_lines[:5]:
                bullets.append(al.lstrip("[] "))

        elif "decision" in title_lower:
            paragraphs.append(
                "The following decisions require S&OP Committee review and approval to maintain "
                "service level targets and mitigate identified supply risks."
            )
            bullets.extend([
                "Review titanium allocation response strategy",
                "Approve alternate sourcing for constrained materials",
                "Validate inventory reduction targets against service levels",
            ])

        elif "action" in title_lower or "next step" in title_lower:
            paragraphs.append(
                "The following action items have been identified for immediate and near-term execution."
            )
            bullets.extend([
                "Expedite critical replenishment orders for at-risk SKUs",
                "Complete supplier performance review for low-reliability vendors",
                "Schedule capacity rebalancing assessment across facilities",
                "Update safety stock parameters based on revised demand signals",
            ])

        else:
            paragraphs.append(
                f"This section covers {section_title.lower()} for the current reporting period. "
                "Detailed analysis is based on the latest available supply chain data."
            )
            for kl in kpi_lines[:4]:
                bullets.append(kl.strip())

        if not paragraphs:
            paragraphs.append(f"Analysis for {section_title} based on current supply chain data.")
        if not bullets:
            bullets.append("Refer to detailed data tables for comprehensive breakdown.")

        return DocSection(title=section_title, paragraphs=paragraphs, bullets=bullets, table=table)

    def _format_data_context(self, data_context: dict[str, Any]) -> str:
        """
        Format the supply chain data_context into a structured string
        the LLM can use to write accurate, data-driven content.
        """
        lines: list[str] = []

        # ─── KPIs ─────────────────────────────────────────────────────────
        kpis = data_context.get("kpis")
        if kpis:
            k = kpis.model_dump() if hasattr(kpis, "model_dump") else (kpis if isinstance(kpis, dict) else {})
            lines.append("=== KEY PERFORMANCE INDICATORS ===")
            lines.append(f"Fill Rate: {k.get('fill_rate', 'N/A')}%")
            lines.append(f"Stockout Rate: {k.get('stockout_rate', 'N/A')}%")
            lines.append(f"Inventory Days of Supply: {k.get('inventory_dos', 'N/A')} days")
            lines.append(f"Forecast Accuracy (MAPE): {k.get('forecast_accuracy_mape', 'N/A')}%")
            lines.append(f"On-Time Delivery: {k.get('on_time_delivery', 'N/A')}%")
            lines.append(f"Production Utilization: {k.get('production_utilization', 'N/A')}%")
            lines.append(f"Obsolescence Rate: {k.get('obsolescence_rate', 'N/A')}%")
            lines.append(f"Working Capital: {k.get('working_capital_mm', 'N/A')} MM CAD")
            lines.append(f"Open Alerts: {k.get('alerts_open', 'N/A')}")
            lines.append(f"Pending Actions: {k.get('pending_actions', 'N/A')}")
            lines.append("")

        # ─── Inventory Positions ──────────────────────────────────────────
        inventory = data_context.get("inventory", [])
        if inventory:
            lines.append("=== INVENTORY POSITIONS ===")
            for item in inventory[:20]:  # Cap at 20 for token efficiency
                i = item.model_dump() if hasattr(item, "model_dump") else item
                sku = i.get("sku_name", "Unknown")
                cat = i.get("category", "")
                cat_val = cat.value if hasattr(cat, "value") else str(cat)
                wh = i.get("warehouse", "")
                stock = i.get("available_stock", 0)
                dos = i.get("days_of_supply", 0)
                risk = i.get("risk_level", "")
                risk_val = risk.value if hasattr(risk, "value") else str(risk)
                in_transit = i.get("in_transit", 0)
                lines.append(
                    f"  {sku} | {cat_val} | {wh} | Stock: {stock} | "
                    f"DoS: {dos} | Risk: {risk_val} | In-Transit: {in_transit}"
                )
            if len(inventory) > 20:
                lines.append(f"  ... and {len(inventory) - 20} more positions")
            lines.append("")

        # ─── Demand Forecasts ─────────────────────────────────────────────
        forecasts = data_context.get("forecasts", [])
        if forecasts:
            lines.append("=== DEMAND FORECASTS ===")
            for fc in forecasts[:15]:
                f = fc.model_dump() if hasattr(fc, "model_dump") else fc
                lines.append(
                    f"  SKU {f.get('sku_id', '')} ({f.get('sku_name', '')}) | "
                    f"Week: {f.get('week', '')} | Forecast: {f.get('point_forecast', 0):.0f} | "
                    f"Range: [{f.get('lower_80', 0):.0f} - {f.get('upper_80', 0):.0f}]"
                )
            if len(forecasts) > 15:
                lines.append(f"  ... and {len(forecasts) - 15} more forecast records")
            lines.append("")

        # ─── Suppliers ────────────────────────────────────────────────────
        suppliers = data_context.get("suppliers", [])
        if suppliers:
            lines.append("=== SUPPLIERS ===")
            for sup in suppliers:
                s = sup.model_dump() if hasattr(sup, "model_dump") else sup
                lines.append(
                    f"  {s.get('name', 'Unknown')} | {s.get('country', '')} | "
                    f"Lead Time: {s.get('avg_lead_time_days', 'N/A')} days | "
                    f"Reliability: {s.get('reliability_score', 0):.1%} | "
                    f"Quality: {s.get('quality_score', 0):.2f}"
                )
            lines.append("")

        # ─── Replenishment Actions ────────────────────────────────────────
        actions = data_context.get("actions", [])
        if actions:
            lines.append("=== REPLENISHMENT ACTIONS ===")
            for act in actions[:15]:
                a = act.model_dump() if hasattr(act, "model_dump") else act
                lines.append(
                    f"  {a.get('sku_name', '')} | Type: {a.get('action_type', '')} | "
                    f"Qty: {a.get('recommended_qty', 0):.0f} | "
                    f"Urgency: {a.get('urgency', '')} | "
                    f"Confidence: {a.get('confidence', '')} | "
                    f"Scenario: {a.get('scenario', '')}"
                )
            if len(actions) > 15:
                lines.append(f"  ... and {len(actions) - 15} more actions")
            lines.append("")

        # ─── Supply Alerts ────────────────────────────────────────────────
        alerts = data_context.get("alerts", [])
        if alerts:
            lines.append("=== SUPPLY ALERTS ===")
            for alert in alerts[:10]:
                al = alert.model_dump() if hasattr(alert, "model_dump") else alert
                lines.append(
                    f"  [{al.get('severity', '').upper()}] {al.get('title', '')} — "
                    f"{al.get('description', '')}"
                )
                lines.append(f"    Recommended: {al.get('recommended_action', '')}")
            if len(alerts) > 10:
                lines.append(f"  ... and {len(alerts) - 10} more alerts")
            lines.append("")

        return "\n".join(lines)
