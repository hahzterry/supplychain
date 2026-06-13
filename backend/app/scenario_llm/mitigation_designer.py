"""MitigationDesigner — LLM proposes creative mitigations with cost-benefit."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a supply chain mitigation strategist for Héroux-Devtek Inc. (Canadian aerospace).
Given a scenario and its impacts, propose creative and practical mitigations.

For each mitigation, provide:
- Specific actionable step (not generic advice)
- Estimated cost in CAD
- Expected fill rate recovery percentage
- Implementation lead time in days
- Priority: critical, high, medium, low
- Feasibility score: 1-10

Consider:
- Supplier diversification & expediting
- Production reallocation & overtime
- Inventory redistribution between warehouses
- Demand management (promotions, allocation)
- Commercial actions (price adjustments, contract renegotiation)
- Logistics alternatives (air freight, alternate ports)

Return JSON:
{
    "mitigation_options": [
        {
            "action": "Specific action description",
            "cost_cad": 25000,
            "fill_rate_recovery": 1.5,
            "lead_time_days": 3,
            "priority": "critical",
            "feasibility": 8,
            "rationale": "Why this works"
        }
    ],
    "total_recovery_potential_pct": 4.5,
    "total_estimated_cost_cad": 150000,
    "implementation_sequence": ["Step 1", "Step 2", "Step 3"]
}
"""


class MitigationDesigner:
    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key, timeout=60.0,
        )
        self._model = model

    async def design(self, plan: dict[str, Any], impacts: dict[str, Any], data_service: Any) -> dict[str, Any]:
        suppliers = await data_service.get_suppliers()
        lines = await data_service.get_production_lines()

        supplier_info = ", ".join(f"{s.name} ({s.country}, {s.reliability_score}% reliable)" for s in suppliers[:5])
        line_info = ", ".join(f"{l.line_name} ({l.current_utilization_pct}% util, {l.capacity_units_per_day} units/day)" for l in lines)

        summary_stats = impacts.get("demand_impact", {}).get("summary_stats", {})
        kpi_deltas = impacts.get("kpi_projection", {}).get("deltas", {})
        affected_skus = impacts.get("demand_impact", {}).get("affected_skus", [])[:5]
        sku_names = ", ".join(s.get("sku_name", "") for s in affected_skus)

        user_msg = (
            f"Scenario: {plan.get('scenario_name', '')}\n"
            f"Type: {plan.get('scenario_type', '')}\n"
            f"Affected SKUs: {sku_names}\n"
            f"Critical SKUs: {summary_stats.get('critical_skus', 0)}\n"
            f"KPI Impact: {json.dumps(kpi_deltas)}\n\n"
            f"Available Suppliers: {supplier_info}\n"
            f"Production Lines: {line_info}\n\n"
            "Design 5-8 specific mitigation actions."
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.5,
                max_completion_tokens=2000,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception as e:
            logger.error("MitigationDesigner LLM failed: %s", e)
            return {
                "mitigation_options": impacts.get("kpi_projection", {}).get("mitigation_options", []),
                "total_recovery_potential_pct": 0,
                "total_estimated_cost_cad": 0,
                "implementation_sequence": [],
            }
