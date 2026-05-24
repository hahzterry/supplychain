"""Scenario analysis supervisor — orchestrates 5-step pipeline with progress callbacks."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from ..data.service import DataService
from .demand_analyzer import DemandAnalyzer
from .inventory_simulator import InventorySimulator
from .supply_evaluator import SupplyEvaluator
from .production_checker import ProductionChecker
from .kpi_projector import KPIProjector

ProgressCallback = Callable[[str, str], Awaitable[None]]


class ScenarioSupervisor:
    def __init__(self):
        self.demand = DemandAnalyzer()
        self.inventory = InventorySimulator()
        self.supply = SupplyEvaluator()
        self.production = ProductionChecker()
        self.kpi = KPIProjector()

    async def run(
        self,
        data: DataService,
        scenario_type: str,
        params: dict[str, Any],
        on_progress: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        async def _progress(step: str, status: str):
            if on_progress:
                await on_progress(step, status)

        await _progress("demand_analysis", "running")
        demand = await self.demand.analyze(data, scenario_type, params)
        await _progress("demand_analysis", "done")

        await _progress("inventory_simulation", "running")
        inventory = await self.inventory.simulate(data, demand, params)
        await _progress("inventory_simulation", "done")

        await _progress("supply_evaluation", "running")
        supply = await self.supply.evaluate(data, scenario_type, params)
        await _progress("supply_evaluation", "done")

        await _progress("production_check", "running")
        categories = list(set(s.category for s in demand.affected_skus))
        production = await self.production.check(data, scenario_type, params, categories)
        await _progress("production_check", "done")

        await _progress("kpi_projection", "running")
        kpi = await self.kpi.project(data, demand, inventory, supply, production)
        await _progress("kpi_projection", "done")

        return {
            "scenario_type": scenario_type,
            "parameters": params,
            "demand_impact": demand.model_dump(),
            "inventory_impact": inventory.model_dump(),
            "supply_impact": supply.model_dump(),
            "production_impact": production.model_dump(),
            "kpi_projection": kpi.model_dump(),
            "baseline_kpis": kpi.baseline,
            "projected_impact": kpi.projected,
            "kpi_deltas": kpi.deltas,
            "risk_assessment": kpi.risk_summary,
            "recommended_actions": kpi.recommended_actions,
            "affected_skus": [s.model_dump() for s in demand.affected_skus],
            "timeline": inventory.timeline,
            "mitigation_options": [m.model_dump() for m in kpi.mitigation_options],
        }
