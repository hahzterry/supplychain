"""Supply-side evaluation — supplier alternatives, lead times, coverage gaps."""
from __future__ import annotations

from ..data.service import DataService
from .schemas import SupplyImpact, SupplierAlternative


class SupplyEvaluator:
    async def evaluate(self, data: DataService, scenario_type: str, params: dict) -> SupplyImpact:
        suppliers = await data.get_suppliers()
        purchase_orders = await data.get_purchase_orders(status="")

        affected_suppliers: list[dict] = []
        alternatives: list[SupplierAlternative] = []
        in_transit: list[dict] = []

        if scenario_type == "supplier_delay":
            delay_days = params.get("delay_days", 14)
            supplier_id = params.get("supplier_id", "")

            delayed = None
            for s in suppliers:
                if s.id == supplier_id or (not supplier_id and s.reliability_score < 80):
                    delayed = s
                    break

            if not delayed and suppliers:
                delayed = min(suppliers, key=lambda s: s.reliability_score)

            if delayed:
                affected_suppliers.append({
                    "id": delayed.id,
                    "name": delayed.name,
                    "country": delayed.country,
                    "reliability_score": delayed.reliability_score,
                    "avg_lead_time_days": delayed.avg_lead_time_days,
                    "delay_days": delay_days,
                    "material_types": delayed.material_types,
                    "impact": "primary_delay",
                })

                for s in suppliers:
                    if s.id == delayed.id:
                        continue
                    shared_materials = set(s.material_types) & set(delayed.material_types)
                    if shared_materials or s.reliability_score > 85:
                        available_cap = s.total_capacity_units - s.current_orders
                        alternatives.append(SupplierAlternative(
                            id=s.id,
                            name=s.name,
                            available_capacity_units=round(max(0, available_cap), 0),
                            lead_time_days=s.avg_lead_time_days,
                            reliability=s.reliability_score,
                            cost_premium_pct=round(max(0, (100 - s.reliability_score) * 0.15), 1),
                        ))

            for po in purchase_orders:
                if po.status == "in_transit":
                    in_transit.append({
                        "po_id": po.id,
                        "supplier_id": po.supplier_id,
                        "qty_mt": po.qty,
                        "expected_delivery": str(po.expected_delivery),
                        "mitigates_gap_pct": round(min(100, (po.qty / max(1, delayed.current_orders if delayed else 1)) * 100), 0),
                    })

        else:
            for s in sorted(suppliers, key=lambda x: x.reliability_score, reverse=True)[:5]:
                available_cap = s.total_capacity_units - s.current_orders
                alternatives.append(SupplierAlternative(
                    id=s.id,
                    name=s.name,
                    available_capacity_units=round(max(0, available_cap), 0),
                    lead_time_days=s.avg_lead_time_days,
                    reliability=s.reliability_score,
                    cost_premium_pct=round(max(0, (100 - s.reliability_score) * 0.1), 1),
                ))

            for po in purchase_orders:
                if po.status == "in_transit":
                    in_transit.append({
                        "po_id": po.id,
                        "supplier_id": po.supplier_id,
                        "qty_mt": po.qty,
                        "expected_delivery": str(po.expected_delivery),
                    })

        total_alt_capacity = sum(a.available_capacity_units for a in alternatives)
        needed = params.get("spike_pct", params.get("uplift_pct", 30)) * 10
        fastest = min((a.lead_time_days for a in alternatives), default=0)

        return SupplyImpact(
            affected_suppliers=affected_suppliers,
            alternative_suppliers=alternatives,
            in_transit_mitigations=in_transit[:5],
            supply_gap={
                "total_needed_mt": round(needed, 0),
                "available_mt": round(total_alt_capacity, 0),
                "coverage_pct": round(min(100, (total_alt_capacity / max(1, needed)) * 100), 0),
                "fastest_delivery_days": fastest,
            },
        )
