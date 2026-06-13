"""ScenarioAnalyst — LLM-driven risk assessment and recommendations.

Takes the quantitative pipeline results and generates context-specific
narrative analysis tailored to the actual scenario.
"""
from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a senior supply chain risk analyst at Héroux-Devtek Inc., a Tier-1 aerospace \
manufacturer specializing in landing gear systems, actuation, and hydraulic components.

Business units: Longueuil QC (landing gear assembly & integration), Kitchener ON \
(actuation systems & flight-critical components), Springfield OH (military programs), \
Nottingham UK (European ops), Laval QC (hydraulics), Livonia MI (repair station).

Key programs: Airbus A220/A320/A330/A350, Boeing 737/777/787, Lockheed Martin F-35, \
Bombardier Global/Challenger, Embraer E2, Sikorsky helicopters.

Materials: titanium forgings, specialty alloys (Inconel, 300M steel), aluminum billets, \
NADCAP-certified surface treatments, hydraulic fluids, seals & fasteners.

You receive quantitative scenario analysis data and must produce:
1. A risk_assessment paragraph (3-5 sentences) that is SPECIFIC to this scenario — \
reference actual affected parts, programs, suppliers, and plants by name.
2. Recommended actions (4-6 items) that a VP Supply Chain would act on immediately — \
be specific about what to do, who to contact, and what timeline.
3. Improved mitigation option descriptions that reference actual scenario context.

IMPORTANT: Never use generic food/consumer goods terminology. This is aerospace/defense.
Frame everything in terms of: AOG risk, program delivery schedules, NADCAP processes, \
airworthiness requirements, customer contractual penalties, OEM rate changes.

Respond with JSON:
{
  "risk_assessment": "string (3-5 sentences)",
  "recommended_actions": ["action 1", "action 2", ...],
  "mitigation_actions": ["improved action text for each mitigation option"]
}
"""


class ScenarioAnalyst:
    """LLM-based scenario risk analyst."""

    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key,
            timeout=60.0,
        )
        self._model = model

    async def analyze(
        self,
        scenario_text: str,
        scenario_type: str,
        params: dict,
        pipeline_result: dict,
    ) -> dict:
        """Generate dynamic risk assessment and recommendations.

        Returns dict with keys: risk_assessment, recommended_actions, mitigation_actions.
        Falls back to empty dict if LLM fails (caller keeps deterministic defaults).
        """
        context = self._build_context(scenario_text, scenario_type, params, pipeline_result)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
                temperature=0.4,
                max_completion_tokens=8000,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content or "{}"
            if not raw.strip() or raw.strip() == "{}":
                logger.warning("ScenarioAnalyst: empty LLM response, using fallback")
                return {}

            data = json.loads(raw)
            result = {}

            if data.get("risk_assessment") and len(data["risk_assessment"]) > 20:
                result["risk_assessment"] = data["risk_assessment"]

            if data.get("recommended_actions") and len(data["recommended_actions"]) >= 3:
                result["recommended_actions"] = data["recommended_actions"][:8]

            if data.get("mitigation_actions") and len(data["mitigation_actions"]) >= 1:
                result["mitigation_actions"] = data["mitigation_actions"]

            return result

        except Exception as e:
            logger.warning("ScenarioAnalyst: LLM call failed (%s), using fallback", e)
            return {}

    def _build_context(self, scenario_text: str, scenario_type: str, params: dict, result: dict) -> str:
        """Build the analysis context prompt from pipeline results."""
        parts = [f"## Scenario\n\"{scenario_text}\"\nType: {scenario_type} | Params: {json.dumps(params)}"]

        demand = result.get("demand_impact", {})
        if demand:
            stats = demand.get("summary_stats", {})
            skus = demand.get("affected_skus", [])
            sku_names = [s.get("sku_name", s.get("sku_id", "")) for s in skus[:8]]
            parts.append(
                f"## Demand Impact\n"
                f"Total affected: {stats.get('total_affected_skus', 0)} SKUs | "
                f"Critical: {stats.get('critical_skus', 0)} | "
                f"Warning: {stats.get('warning_skus', 0)}\n"
                f"Avg demand increase: {stats.get('avg_demand_increase_pct', 0)}%\n"
                f"Affected SKUs: {', '.join(sku_names)}"
            )

        inv = result.get("inventory_impact", {})
        if inv:
            agg = inv.get("aggregate", {})
            projs = inv.get("sku_projections", [])
            stockout_skus = [p.get("sku_name", "") for p in projs if p.get("stockout_week")]
            parts.append(
                f"## Inventory Impact\n"
                f"SKUs hitting stockout: {agg.get('skus_stockout_count', 0)} | "
                f"Safety stock breached: {agg.get('skus_safety_breached', 0)}\n"
                f"Projected lost sales: CAD {agg.get('total_lost_sales_cad', 0):,.0f}\n"
                f"Stockout SKUs: {', '.join(stockout_skus[:5])}"
            )

        supply = result.get("supply_impact", {})
        if supply:
            gap = supply.get("supply_gap", {})
            alts = supply.get("alternative_suppliers", [])
            alt_names = [a.get("name", "") for a in alts[:5]]
            parts.append(
                f"## Supply Impact\n"
                f"Supply gap coverage: {gap.get('coverage_pct', 0)}% | "
                f"Needed: {gap.get('total_needed_mt', 0)} units | "
                f"Available: {gap.get('available_mt', 0)} units\n"
                f"Fastest delivery: {gap.get('fastest_delivery_days', 0)} days\n"
                f"Alternative suppliers: {', '.join(alt_names)}"
            )

        prod = result.get("production_impact", {})
        if prod:
            lines = prod.get("affected_lines", [])
            line_info = [f"{l.get('name', '')} ({l.get('plant', '')})" for l in lines[:4]]
            parts.append(
                f"## Production Impact\n"
                f"Feasibility: {prod.get('feasibility', 'unknown')}\n"
                f"Affected lines: {', '.join(line_info)}\n"
                f"Options: {len(prod.get('production_options', []))}"
            )

        kpi = result.get("kpi_projection", {})
        if kpi:
            breaches = kpi.get("target_breaches", [])
            deltas = kpi.get("deltas", {})
            delta_str = ", ".join(f"{k}: {v:+.1f}" for k, v in list(deltas.items())[:5])
            parts.append(
                f"## KPI Projection\n"
                f"Target breaches: {'; '.join(breaches) if breaches else 'None'}\n"
                f"Deltas: {delta_str}"
            )

        mits = result.get("mitigation_options", [])
        if mits:
            mit_list = [f"- {m.get('action', '')} (CAD {m.get('cost_cad', 0):,.0f}, +{m.get('fill_rate_recovery', 0)}% fill rate)" for m in mits[:5]]
            parts.append(f"## Current Mitigation Options\n" + "\n".join(mit_list))

        parts.append(
            "\n## Your Task\n"
            "Generate a risk_assessment, recommended_actions, and improved mitigation_actions "
            "that are SPECIFIC to this scenario. Reference actual part names, programs, "
            "suppliers, and plants. Frame in aerospace/defense supply chain terms."
        )

        return "\n\n".join(parts)
