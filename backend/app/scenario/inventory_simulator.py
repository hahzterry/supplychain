"""Inventory simulation — projects week-by-week stock depletion and stockout dates."""
from __future__ import annotations

from ..data.service import DataService
from .schemas import DemandImpact, InventoryImpact, SkuProjection

HORIZON_WEEKS = 8


class InventorySimulator:
    async def simulate(self, data: DataService, demand_impact: DemandImpact, params: dict) -> InventoryImpact:
        inventory = await data.get_inventory()
        purchase_orders = await data.get_purchase_orders()
        skus = await data.get_skus()

        inv_map = {p.sku_id: p for p in inventory}
        sku_map = {s.id: s for s in skus}

        po_by_sku: dict[str, float] = {}
        for po in purchase_orders:
            if po.status in ("open", "in_transit"):
                po_by_sku[po.sku_id] = po_by_sku.get(po.sku_id, 0) + po.qty

        projections: list[SkuProjection] = []
        timeline_data: list[dict] = []

        weekly_totals: dict[int, dict] = {w: {"stock": 0, "demand": 0, "below_safety": 0, "stockout": 0} for w in range(1, HORIZON_WEEKS + 1)}

        for affected in demand_impact.affected_skus:
            inv = inv_map.get(affected.sku_id)
            sku = sku_map.get(affected.sku_id)

            current_stock = inv.available_stock if inv else 0
            in_transit = inv.in_transit if inv else 0
            current_dos = inv.days_of_supply if inv else 0
            unit_cost = sku.unit_cost if sku else 1.0
            safety_days = sku.safety_stock_days if sku else 14

            weekly_demand = affected.adjusted_weekly_demand
            safety_stock = (safety_days / 7) * affected.baseline_weekly_demand

            stock = current_stock + in_transit * 0.5
            stockout_week = None
            safety_breached = False

            for week in range(1, HORIZON_WEEKS + 1):
                stock -= weekly_demand
                if stock <= safety_stock and not safety_breached:
                    safety_breached = True
                if stock <= 0 and stockout_week is None:
                    stockout_week = week

                weekly_totals[week]["stock"] += max(0, stock)
                weekly_totals[week]["demand"] += weekly_demand
                if stock <= safety_stock:
                    weekly_totals[week]["below_safety"] += 1
                if stock <= 0:
                    weekly_totals[week]["stockout"] += 1

            lost_weeks = (HORIZON_WEEKS - stockout_week + 1) if stockout_week else 0
            lost_units = lost_weeks * weekly_demand
            lost_cad = lost_units * unit_cost

            projected_dos = max(0, (current_stock + in_transit * 0.5) / (weekly_demand / 7)) if weekly_demand > 0 else current_dos

            projections.append(SkuProjection(
                sku_id=affected.sku_id,
                sku_name=affected.sku_name,
                current_dos=round(current_dos, 1),
                projected_dos=round(projected_dos, 1),
                stockout_week=stockout_week,
                safety_stock_breached=safety_breached,
                projected_lost_sales_units=round(lost_units, 0),
                projected_lost_sales_cad=round(lost_cad, 0),
            ))

        for week in range(1, HORIZON_WEEKS + 1):
            t = weekly_totals[week]
            timeline_data.append({
                "week": week,
                "label": f"Week {week}",
                "total_stock_mt": round(t["stock"], 0),
                "total_demand_mt": round(t["demand"], 0),
                "net_position": round(t["stock"] - t["demand"], 0),
                "skus_below_safety": t["below_safety"],
                "skus_stockout": t["stockout"],
            })

        total_lost_cad = sum(p.projected_lost_sales_cad for p in projections)
        stockout_count = sum(1 for p in projections if p.stockout_week is not None)
        avg_dos_reduction = (
            sum(p.current_dos - p.projected_dos for p in projections) / max(1, len(projections))
        )

        return InventoryImpact(
            sku_projections=projections,
            timeline=timeline_data,
            aggregate={
                "total_lost_sales_cad": round(total_lost_cad, 0),
                "skus_stockout_count": stockout_count,
                "skus_safety_breached": sum(1 for p in projections if p.safety_stock_breached),
                "avg_dos_reduction": round(avg_dos_reduction, 1),
            },
        )
