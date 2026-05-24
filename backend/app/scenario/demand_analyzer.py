"""Demand impact analysis — identifies affected SKUs and computes demand deltas."""
from __future__ import annotations

from ..data.service import DataService
from .schemas import AffectedSku, DemandImpact, TimelineWeek


ABC_WEIGHT = {"A": 1.0, "B": 0.7, "C": 0.4}
HORIZON_WEEKS = 8


class DemandAnalyzer:
    async def analyze(self, data: DataService, scenario_type: str, params: dict) -> DemandImpact:
        skus = await data.get_skus()
        forecasts = await data.get_demand_forecast()
        inventory = await data.get_inventory()

        inv_map = {p.sku_id: p for p in inventory}
        forecast_map: dict[str, float] = {}
        for f in forecasts:
            forecast_map.setdefault(f.sku_id, 0)
            forecast_map[f.sku_id] += f.point_forecast
        forecast_count = max(1, len(set(f.week for f in forecasts)))

        affected_skus: list[AffectedSku] = []

        for sku in skus:
            total_forecast = forecast_map.get(sku.id, 0)
            baseline_weekly = total_forecast / forecast_count if total_forecast > 0 else 50.0
            multiplier = self._compute_multiplier(scenario_type, params, sku)

            if multiplier <= 1.0:
                continue

            adjusted_weekly = baseline_weekly * multiplier
            delta_pct = (multiplier - 1.0) * 100

            inv = inv_map.get(sku.id)
            current_stock = inv.available_stock if inv else 0
            current_dos = inv.days_of_supply if inv else 0
            weeks_to_stockout = current_stock / adjusted_weekly if adjusted_weekly > 0 else 99

            severity = "critical" if weeks_to_stockout < 2 else "warning" if weeks_to_stockout < 4 else "safe"

            affected_skus.append(AffectedSku(
                sku_id=sku.id,
                sku_name=sku.name,
                category=sku.category.value,
                abc_class=sku.abc_class,
                baseline_weekly_demand=round(baseline_weekly, 1),
                adjusted_weekly_demand=round(adjusted_weekly, 1),
                demand_delta_pct=round(delta_pct, 1),
                weeks_until_stockout=round(weeks_to_stockout, 1),
                current_dos=round(current_dos, 1),
                severity=severity,
            ))

        affected_skus.sort(key=lambda s: s.weeks_until_stockout)

        timeline = self._build_timeline(affected_skus, inv_map)

        critical = sum(1 for s in affected_skus if s.severity == "critical")
        warning = sum(1 for s in affected_skus if s.severity == "warning")
        safe = sum(1 for s in affected_skus if s.severity == "safe")

        return DemandImpact(
            affected_skus=affected_skus,
            weekly_timeline=timeline,
            summary_stats={
                "total_affected_skus": len(affected_skus),
                "critical_skus": critical,
                "warning_skus": warning,
                "safe_skus": safe,
                "avg_demand_increase_pct": round(
                    sum(s.demand_delta_pct for s in affected_skus) / max(1, len(affected_skus)), 1
                ),
            },
        )

    def _compute_multiplier(self, scenario_type: str, params: dict, sku) -> float:
        abc_weight = ABC_WEIGHT.get(sku.abc_class, 0.5)
        categories = params.get("affected_categories", [])

        if scenario_type == "demand_spike":
            spike_pct = params.get("spike_pct", params.get("spike_percent", 30))
            if categories and sku.category.value.lower() not in [c.lower() for c in categories]:
                return 1.0
            return 1.0 + (spike_pct / 100) * abc_weight

        elif scenario_type == "supplier_delay":
            delay_days = params.get("delay_days", 14)
            if categories and sku.category.value.lower() not in [c.lower() for c in categories]:
                return 1.0
            urgency = min(1.0, delay_days / 21)
            return 1.0 + 0.15 * abc_weight * urgency

        elif scenario_type == "promotion":
            uplift_pct = params.get("uplift_pct", params.get("uplift_percent", 25))
            promoted = params.get("promoted_skus", categories)
            if promoted:
                match = sku.id in promoted or sku.category.value.lower() in [c.lower() for c in promoted]
                if not match:
                    return 1.0
            return 1.0 + (uplift_pct / 100) * abc_weight

        elif scenario_type == "capacity_loss":
            if categories and sku.category.value.lower() not in [c.lower() for c in categories]:
                return 1.0
            return 1.0 + 0.2 * abc_weight

        return 1.0

    def _build_timeline(self, affected_skus: list[AffectedSku], inv_map) -> list[TimelineWeek]:
        timeline = []
        for week in range(1, HORIZON_WEEKS + 1):
            total_baseline = sum(s.baseline_weekly_demand for s in affected_skus)
            total_adjusted = sum(s.adjusted_weekly_demand for s in affected_skus)

            running_stock = 0
            below_safety = 0
            stockout = 0
            for s in affected_skus:
                inv = inv_map.get(s.sku_id)
                initial_stock = inv.available_stock if inv else 0
                remaining = initial_stock - (s.adjusted_weekly_demand * week)
                running_stock += max(0, remaining)
                if remaining < s.baseline_weekly_demand * 2:
                    below_safety += 1
                if remaining <= 0:
                    stockout += 1

            timeline.append(TimelineWeek(
                week=week,
                label=f"Week {week}",
                total_baseline_demand=round(total_baseline, 0),
                total_adjusted_demand=round(total_adjusted, 0),
                total_stock=round(running_stock, 0),
                net_position=round(running_stock - total_adjusted, 0),
                skus_below_safety=below_safety,
                skus_stockout=stockout,
            ))
        return timeline
