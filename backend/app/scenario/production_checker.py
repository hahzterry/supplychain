"""Production capacity check — spare capacity, surge options, maintenance conflicts."""
from __future__ import annotations

from ..data.service import DataService
from .schemas import ProductionImpact, ProductionOption


class ProductionChecker:
    async def check(self, data: DataService, scenario_type: str, params: dict, affected_categories: list[str]) -> ProductionImpact:
        lines = await data.get_production_lines()

        affected_lines: list[dict] = []
        total_spare = 0.0
        maintenance_conflicts: list[str] = []
        options: list[ProductionOption] = []

        cat_set = set(c.lower() for c in affected_categories)

        for line in lines:
            line_cats = set(c.value.lower() if hasattr(c, 'value') else c.lower() for c in line.product_categories)
            overlap = line_cats & cat_set

            if not overlap and affected_categories:
                continue

            spare = line.capacity_units_per_day * (1 - line.current_utilization_pct / 100)
            total_spare += spare

            affected_lines.append({
                "id": line.id,
                "name": line.line_name,
                "plant": line.plant.value,
                "current_utilization": line.current_utilization_pct,
                "spare_capacity_units_day": round(spare, 1),
                "categories": [c.value if hasattr(c, 'value') else c for c in line.product_categories],
            })

            if line.planned_maintenance:
                for maint in line.planned_maintenance:
                    maintenance_conflicts.append(f"{line.line_name} maintenance: {maint}")

            if spare > 5:
                options.append(ProductionOption(
                    option=f"Increase {line.line_name} utilization to {min(95, line.current_utilization_pct + 10)}%",
                    extra_mt_per_day=round(spare * 0.8, 1),
                    duration_days=params.get("duration_days", 14),
                    impact=f"Overtime costs for {line.plant.value} plant",
                ))

        if scenario_type == "capacity_loss":
            line_id = params.get("line_id", "")
            lost_line = next((l for l in lines if l.id == line_id), None)
            if lost_line:
                lost_capacity = lost_line.capacity_units_per_day * (lost_line.current_utilization_pct / 100)
                other_lines = [l for l in affected_lines if l["id"] != line_id]
                redistributable = sum(l["spare_capacity_units_day"] for l in other_lines)
                options.append(ProductionOption(
                    option=f"Redistribute {lost_line.line_name} production to other lines",
                    extra_mt_per_day=round(min(redistributable, lost_capacity), 1),
                    duration_days=params.get("duration_days", 7),
                    impact=f"Covers {round(min(100, redistributable / max(1, lost_capacity) * 100))}% of lost capacity",
                ))

        demand_gap_mt_day = params.get("spike_pct", params.get("uplift_pct", 30)) * 0.5
        days_needed = demand_gap_mt_day * 7 / max(1, total_spare) if total_spare > 0 else 99

        if total_spare >= demand_gap_mt_day:
            feasibility = "full"
        elif total_spare >= demand_gap_mt_day * 0.5:
            feasibility = "partial"
        else:
            feasibility = "infeasible"

        return ProductionImpact(
            affected_lines=affected_lines,
            surge_capacity={
                "total_spare_mt_per_day": round(total_spare, 1),
                "days_needed_for_gap": round(days_needed, 1),
                "maintenance_conflicts": maintenance_conflicts,
            },
            production_options=options,
            feasibility=feasibility,
        )
