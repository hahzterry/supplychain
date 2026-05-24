"""ImpactAnalyzer — Runs deterministic calcs + LLM narrative interpretation."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncAzureOpenAI

from ..scenario.supervisor import ScenarioSupervisor
from .category_normalizer import normalize_categories

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a supply chain impact analysis agent for AGI Food Division.
Given scenario parameters and quantitative data from deterministic models,
provide enhanced qualitative analysis and narrative interpretation.

Return JSON:
{
    "narrative_summary": "2-3 sentence executive interpretation of the quantitative impacts",
    "qualitative_factors": ["factor not captured by numbers", ...],
    "confidence_assessment": "high|medium|low",
    "hidden_risks": ["risk the numbers don't show", ...],
    "opportunity_areas": ["potential upside from this disruption", ...]
}
"""


class ImpactAnalyzer:
    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint, api_key=api_key,
            api_version="2024-12-01-preview", timeout=60.0,
        )
        self._model = model

    async def analyze(self, plan: dict[str, Any], data_service: Any) -> dict[str, Any]:
        supervisor = ScenarioSupervisor()
        raw_type = plan.get("scenario_type", "demand_spike")
        params = plan.get("parameters", {})

        scenario_type = self._map_scenario_type(raw_type)
        if scenario_type is None:
            scenario_type = self._infer_type_from_params(params)

        det_params = self._map_params(scenario_type, params)
        det_result = await supervisor.run(data_service, scenario_type, det_params)

        try:
            qualitative = await self._llm_enhance(plan, det_result)
        except Exception as e:
            logger.warning("ImpactAnalyzer LLM enhancement failed: %s", e)
            qualitative = {
                "narrative_summary": "Quantitative analysis completed. Qualitative enhancement unavailable.",
                "qualitative_factors": [],
                "confidence_assessment": "medium",
                "hidden_risks": [],
                "opportunity_areas": [],
            }

        result = dict(det_result)
        result["qualitative_analysis"] = qualitative
        return result

    def _map_scenario_type(self, llm_type: str) -> str | None:
        """Map LLM scenario type to deterministic engine type."""
        type_map = {
            "demand_spike": "demand_spike",
            "demand_surge": "demand_spike",
            "seasonal_demand": "demand_spike",
            "panic_buying": "demand_spike",
            "supplier_delay": "supplier_delay",
            "supply_disruption": "supplier_delay",
            "supply_chain_disruption": "supplier_delay",
            "port_delay": "supplier_delay",
            "shipping_delay": "supplier_delay",
            "logistics_disruption": "supplier_delay",
            "production_disruption": "capacity_loss",
            "capacity_loss": "capacity_loss",
            "capacity_reduction": "capacity_loss",
            "factory_shutdown": "capacity_loss",
            "equipment_failure": "capacity_loss",
            "promotion": "promotion",
            "marketing_campaign": "promotion",
            "promotional_event": "promotion",
            "cost_increase": "supplier_delay",
        }
        return type_map.get(llm_type.lower().strip())

    def _infer_type_from_params(self, params: dict) -> str:
        """Infer scenario type when LLM type is ambiguous (multi_factor, custom, etc.)."""
        if params.get("delay_days") or params.get("lead_time_increase_days") or params.get("supplier_delay_days"):
            return "supplier_delay"
        if params.get("uplift_pct") or params.get("promotion_uplift_pct"):
            return "promotion"
        if params.get("line_id") or "capacity" in str(params).lower() or "production" in str(params).lower():
            return "capacity_loss"
        return "demand_spike"

    def _map_params(self, scenario_type: str, params: dict) -> dict:
        """Map LLM-planned params to deterministic pipeline format, branched by type."""
        mapped: dict[str, Any] = {}

        # Normalize categories
        raw_cats = params.get("affected_categories", params.get("categories", []))
        if isinstance(raw_cats, str):
            raw_cats = [raw_cats]
        normalized_cats = normalize_categories(raw_cats)
        if normalized_cats:
            mapped["affected_categories"] = normalized_cats
        elif raw_cats:
            # LLM specified categories but none matched — default to Flour+Pasta
            # (most common categories) rather than affecting ALL 50 SKUs
            mapped["affected_categories"] = ["Flour", "Pasta"]

        # Type-specific parameter mapping
        if scenario_type == "demand_spike":
            spike = (
                params.get("spike_pct")
                or params.get("magnitude_pct")
                or params.get("demand_increase_pct")
                or params.get("demand_spike_pct")
                or params.get("increase_pct")
            )
            mapped["spike_pct"] = int(spike) if spike else 30

        elif scenario_type == "supplier_delay":
            delay = (
                params.get("delay_days")
                or params.get("lead_time_increase_days")
                or params.get("supplier_delay_days")
                or params.get("magnitude_pct")
            )
            mapped["delay_days"] = int(delay) if delay else 14

        elif scenario_type == "promotion":
            uplift = (
                params.get("uplift_pct")
                or params.get("promotion_uplift_pct")
                or params.get("magnitude_pct")
            )
            mapped["uplift_pct"] = int(uplift) if uplift else 25

        elif scenario_type == "capacity_loss":
            pass

        # Shared fields
        if "duration_weeks" in params:
            mapped["duration_weeks"] = params["duration_weeks"]
        if "supplier_id" in params:
            mapped["supplier_id"] = params["supplier_id"]
        if "line_id" in params:
            mapped["line_id"] = params["line_id"]

        return mapped

    async def _llm_enhance(self, plan: dict, det_result: dict) -> dict:
        """Add qualitative narrative on top of deterministic results."""
        summary_stats = det_result.get("demand_impact", {}).get("summary_stats", {})
        kpi_deltas = det_result.get("kpi_projection", {}).get("deltas", {})

        user_msg = (
            f"Scenario: {plan.get('scenario_name', '')}\n"
            f"Type: {plan.get('scenario_type', '')}\n"
            f"Parameters: {json.dumps(plan.get('parameters', {}))}\n\n"
            f"Quantitative Results:\n"
            f"- Affected SKUs: {summary_stats.get('total_affected_skus', 'N/A')}\n"
            f"- Critical: {summary_stats.get('critical_skus', 0)}\n"
            f"- Avg Demand Increase: {summary_stats.get('avg_demand_increase_pct', 0)}%\n"
            f"- KPI Deltas: {json.dumps(kpi_deltas)}\n\n"
            "Provide qualitative analysis."
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.4,
            max_completion_tokens=1000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
