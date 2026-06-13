"""ScenarioPlanner — Interprets natural language into structured scenario parameters."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a supply chain scenario planning agent for Héroux-Devtek Inc. (Canadian aerospace).
Given a natural language scenario description and supply chain data context,
produce a structured analysis plan.

IMPORTANT: scenario_type MUST be one of these exact values:
- "demand_spike" — for demand increases, seasonal surges, panic buying, Ramadan, holidays
- "supplier_delay" — for supply disruptions, port delays, shipping issues, supplier problems
- "production_disruption" — for factory issues, equipment failures, capacity reductions
- "promotion" — for planned marketing/promotional campaigns

For complex scenarios involving multiple factors, choose the DOMINANT factor as scenario_type
and include the secondary effects in parameters.

Return JSON:
{
    "scenario_name": "Short descriptive name",
    "scenario_type": "demand_spike|supplier_delay|production_disruption|promotion",
    "parameters": {
        "affected_categories": ["Flour", "Pasta"],
        "spike_pct": 40,
        "delay_days": 14,
        "duration_weeks": 4,
        "trigger": "description of root cause"
    },
    "analysis_angles": [
        "Inventory depletion rate for affected SKUs",
        "Supplier capacity to absorb demand surge",
        "Production line flexibility"
    ],
    "data_needs": ["inventory_positions", "forecasts", "supplier_capacity", "production_lines"],
    "time_horizon_weeks": 8,
    "severity_estimate": "high|medium|low"
}

Parameter guidelines:
- For demand_spike: include "spike_pct" (10-100), "affected_categories"
- For supplier_delay: include "delay_days" (7-60), "affected_categories"
- For production_disruption: include "affected_categories"
- For promotion: include "uplift_pct" (10-50), "affected_categories"

CRITICAL: "affected_categories" MUST be a JSON array where each element is EXACTLY one of:
"Flour", "Pasta", "Cooking Oil", "Animal Feed", "Rice", "Sugar", "Specialty"
Do NOT combine categories into one string (WRONG: "Flour and Sugar"). List separately (CORRECT: ["Flour", "Sugar"]).
Do NOT use synonyms or alternate names (WRONG: "oils and fats", "wheat", "grains"). Use the exact names above.
Always include at least one affected category based on what the scenario describes.
"""


class ScenarioPlanner:
    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key, timeout=60.0,
        )
        self._model = model

    async def plan(self, scenario_text: str, data_service: Any) -> dict[str, Any]:
        kpis = await data_service.get_kpis()
        inventory = await data_service.get_inventory()
        critical_count = sum(1 for p in inventory if p.risk_level.value == "critical")
        warning_count = sum(1 for p in inventory if p.risk_level.value == "warning")

        context = (
            f"Current KPIs: Fill Rate {kpis.fill_rate}%, Stockout Rate {kpis.stockout_rate}%, "
            f"Inventory DOS {kpis.inventory_dos}, Production Util {kpis.production_utilization}%\n"
            f"Inventory: {len(inventory)} positions, {critical_count} critical, {warning_count} warning\n"
            f"Categories: Flour, Pasta, Cooking Oil, Animal Feed, Rice, Sugar, Specialty"
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Scenario: {scenario_text}\n\nContext:\n{context}"},
                ],
                temperature=0.3,
                max_completion_tokens=1500,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception as e:
            logger.error("ScenarioPlanner LLM failed: %s", e)
            return {
                "scenario_name": scenario_text[:60],
                "scenario_type": "demand_spike",
                "parameters": {"spike_pct": 30, "description": scenario_text},
                "analysis_angles": ["Inventory impact", "Supply chain resilience", "KPI impact"],
                "data_needs": ["inventory_positions", "forecasts"],
                "time_horizon_weeks": 8,
                "severity_estimate": "medium",
            }
