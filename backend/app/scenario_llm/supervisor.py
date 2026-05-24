"""LLM Scenario Supervisor — orchestrates 5 LLM agents for rich scenario analysis."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable
from uuid import uuid4

from .planner import ScenarioPlanner
from .impact_analyzer import ImpactAnalyzer
from .mitigation_designer import MitigationDesigner
from .risk_assessor import RiskAssessor
from .synthesizer import Synthesizer

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, str], Awaitable[None]]


class LLMScenarioSupervisor:
    """Orchestrates 5 LLM agents for comprehensive scenario analysis."""

    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._model = model
        self._endpoint = azure_endpoint
        self._api_key = api_key

    async def run(
        self,
        data_service: Any,
        scenario_text: str,
        on_progress: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        """Run full LLM scenario analysis pipeline."""

        async def _progress(step: str, status: str):
            if on_progress:
                try:
                    await on_progress(step, status)
                except Exception:
                    pass

        await _progress("planner", "running")

        # Step 1: Plan — parse scenario into structured analysis
        planner = ScenarioPlanner(self._model, self._endpoint, self._api_key)
        plan = await planner.plan(scenario_text, data_service)
        await _progress("planner", "done")

        # Step 2: Impact Analysis — quantitative + qualitative
        await _progress("impact_analyzer", "running")
        analyzer = ImpactAnalyzer(self._model, self._endpoint, self._api_key)
        impacts = await analyzer.analyze(plan, data_service)
        await _progress("impact_analyzer", "done")

        # Step 3: Mitigation Design — creative actions
        await _progress("mitigation_designer", "running")
        designer = MitigationDesigner(self._model, self._endpoint, self._api_key)
        mitigations = await designer.design(plan, impacts, data_service)
        await _progress("mitigation_designer", "done")

        # Step 4: Risk Assessment — probability/severity
        await _progress("risk_assessor", "running")
        assessor = RiskAssessor(self._model, self._endpoint, self._api_key)
        risks = await assessor.assess(plan, impacts, mitigations)
        await _progress("risk_assessor", "done")

        # Step 5: Synthesis — executive summary
        await _progress("synthesizer", "running")
        synth = Synthesizer(self._model, self._endpoint, self._api_key)
        synthesis = await synth.synthesize(plan, impacts, mitigations, risks)
        await _progress("synthesizer", "done")

        result = {
            "id": uuid4().hex[:12],
            "name": plan.get("scenario_name", scenario_text[:60]),
            "scenario_type": impacts.get("scenario_type", plan.get("scenario_type", "demand_spike")),
            "parameters": plan.get("parameters", {}),
            "analysis_angles": plan.get("analysis_angles", []),
            "demand_impact": impacts.get("demand_impact", {}),
            "inventory_impact": impacts.get("inventory_impact", {}),
            "supply_impact": impacts.get("supply_impact", {}),
            "production_impact": impacts.get("production_impact", {}),
            "kpi_projection": impacts.get("kpi_projection", {}),
            "baseline_kpis": impacts.get("baseline_kpis", {}),
            "projected_impact": impacts.get("projected_impact", {}),
            "mitigation_options": mitigations.get("mitigation_options", []),
            "recommended_actions": synthesis.get("recommended_actions", []),
            "risk_assessment": risks.get("risk_narrative", ""),
            "risk_matrix": risks.get("risk_matrix", {}),
            "cascading_risks": risks.get("cascading_risks", []),
            "executive_brief": synthesis.get("executive_brief", ""),
            "decision_points": synthesis.get("decision_points", []),
            "confidence_level": synthesis.get("confidence_level", "medium"),
            "affected_skus": [s.get("sku_id", "") for s in impacts.get("demand_impact", {}).get("affected_skus", [])],
            "kpi_impact": impacts.get("kpi_projection", {}).get("deltas", {}),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        return result
