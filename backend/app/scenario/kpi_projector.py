"""KPI projection — aggregates all impacts into final KPI deltas with confidence bands."""
from __future__ import annotations

from ..data.service import DataService
from .schemas import DemandImpact, InventoryImpact, SupplyImpact, ProductionImpact, KPIProjection, MitigationOption


class KPIProjector:
    async def project(
        self,
        data: DataService,
        demand: DemandImpact,
        inventory: InventoryImpact,
        supply: SupplyImpact,
        production: ProductionImpact,
    ) -> KPIProjection:
        kpis = await data.get_kpis()
        all_skus = await data.get_skus()
        total_skus = len(all_skus)

        baseline = {
            "fill_rate": kpis.fill_rate,
            "stockout_rate": kpis.stockout_rate,
            "inventory_dos": kpis.inventory_dos,
            "working_capital_mm": kpis.working_capital_mm,
            "production_utilization": kpis.production_utilization,
            "on_time_delivery": kpis.on_time_delivery,
            "forecast_accuracy_mape": kpis.forecast_accuracy_mape,
        }

        stockout_skus = inventory.aggregate.get("skus_stockout_count", 0)
        safety_breached = inventory.aggregate.get("skus_safety_breached", 0)
        lost_sales_aed = inventory.aggregate.get("total_lost_sales_aed", 0)
        avg_dos_reduction = inventory.aggregate.get("avg_dos_reduction", 0)

        fill_rate_drop = (stockout_skus / max(1, total_skus)) * 15 + (safety_breached / max(1, total_skus)) * 5
        projected_fill_rate = max(85, kpis.fill_rate - fill_rate_drop)

        projected_stockout_rate = min(15, kpis.stockout_rate + (stockout_skus / max(1, total_skus)) * 100)

        projected_dos = max(5, kpis.inventory_dos - avg_dos_reduction)

        expedite_cost_mm = lost_sales_aed * 0.15 / 1_000_000
        projected_wc = kpis.working_capital_mm + expedite_cost_mm

        surge_needed = production.feasibility != "full"
        projected_utilization = min(98, kpis.production_utilization + (5 if surge_needed else 0))

        supply_gap_pct = 100 - supply.supply_gap.get("coverage_pct", 100)
        projected_otd = max(75, kpis.on_time_delivery - supply_gap_pct * 0.3)

        projected = {
            "fill_rate": round(projected_fill_rate, 1),
            "stockout_rate": round(projected_stockout_rate, 1),
            "inventory_dos": round(projected_dos, 1),
            "working_capital_mm": round(projected_wc, 1),
            "production_utilization": round(projected_utilization, 1),
            "on_time_delivery": round(projected_otd, 1),
            "forecast_accuracy_mape": round(kpis.forecast_accuracy_mape + 2.0, 1),
        }

        deltas = {k: round(projected[k] - baseline[k], 1) for k in baseline}

        confidence_bands = {
            "fill_rate": {"best": round(projected_fill_rate + 1.5, 1), "expected": round(projected_fill_rate, 1), "worst": round(projected_fill_rate - 2.5, 1)},
            "stockout_rate": {"best": round(projected_stockout_rate - 0.5, 1), "expected": round(projected_stockout_rate, 1), "worst": round(projected_stockout_rate + 1.5, 1)},
            "inventory_dos": {"best": round(projected_dos + 1, 1), "expected": round(projected_dos, 1), "worst": round(projected_dos - 2, 1)},
        }

        target_breaches = []
        if projected_fill_rate < 97:
            target_breaches.append(f"Fill rate {projected_fill_rate:.1f}% below 97% target")
        if projected_stockout_rate > 2:
            target_breaches.append(f"Stockout rate {projected_stockout_rate:.1f}% above 2% target")
        if projected_dos < 14:
            target_breaches.append(f"Inventory DOS {projected_dos:.1f} below 14-day minimum")

        mitigations = self._build_mitigations(supply, production, demand, inventory)

        risk_summary = self._build_risk_summary(demand, inventory, supply, production, projected, baseline)
        recommended_actions = self._build_recommendations(demand, inventory, supply, production)

        return KPIProjection(
            baseline=baseline,
            projected=projected,
            deltas=deltas,
            confidence_bands=confidence_bands,
            target_breaches=target_breaches,
            mitigation_options=mitigations,
            risk_summary=risk_summary,
            recommended_actions=recommended_actions,
        )

    def _build_mitigations(self, supply: SupplyImpact, production: ProductionImpact, demand: DemandImpact, inventory: InventoryImpact) -> list[MitigationOption]:
        mitigations: list[MitigationOption] = []

        for alt in supply.alternative_suppliers[:3]:
            recovery = min(2.0, alt.available_capacity_mt / 500)
            mitigations.append(MitigationOption(
                action=f"Expedite from {alt.name} ({alt.available_capacity_mt:.0f} MT available)",
                cost_aed=round(alt.available_capacity_mt * alt.cost_premium_pct * 10, 0),
                fill_rate_recovery=round(recovery, 1),
                lead_time_days=alt.lead_time_days,
                priority="high" if alt.reliability > 90 else "medium",
            ))

        for opt in production.production_options[:2]:
            recovery = min(1.5, opt.extra_mt_per_day * opt.duration_days / 500)
            mitigations.append(MitigationOption(
                action=opt.option,
                cost_aed=round(opt.extra_mt_per_day * opt.duration_days * 50, 0),
                fill_rate_recovery=round(recovery, 1),
                lead_time_days=opt.duration_days,
                priority="medium",
            ))

        critical_skus = [s for s in demand.affected_skus if s.severity == "critical"]
        if critical_skus:
            mitigations.append(MitigationOption(
                action=f"Pre-build safety stock for {len(critical_skus)} critical SKUs immediately",
                cost_aed=round(len(critical_skus) * 5000, 0),
                fill_rate_recovery=round(len(critical_skus) * 0.3, 1),
                lead_time_days=3,
                priority="critical",
            ))

        mitigations.sort(key=lambda m: ({"critical": 0, "high": 1, "medium": 2}.get(m.priority, 3), m.lead_time_days))
        return mitigations

    def _build_risk_summary(self, demand, inventory, supply, production, projected, baseline) -> str:
        stats = demand.summary_stats
        agg = inventory.aggregate
        parts = []

        parts.append(f"This scenario affects {stats['total_affected_skus']} SKUs with an average demand increase of {stats['avg_demand_increase_pct']}%.")

        if stats["critical_skus"] > 0:
            parts.append(f"{stats['critical_skus']} SKUs face imminent stockout within 2 weeks.")

        if agg["total_lost_sales_aed"] > 0:
            parts.append(f"Projected lost sales: AED {agg['total_lost_sales_aed']:,.0f} over 8 weeks if no action is taken.")

        fill_drop = baseline["fill_rate"] - projected["fill_rate"]
        if fill_drop > 2:
            parts.append(f"Fill rate would drop by {fill_drop:.1f}pp to {projected['fill_rate']:.1f}% (below 97% target).")

        if production.feasibility == "infeasible":
            parts.append("Production capacity is insufficient to absorb the demand surge without external supply.")
        elif production.feasibility == "partial":
            parts.append("Production can partially cover the gap through overtime/surge, but external supply is also needed.")

        if supply.supply_gap["coverage_pct"] >= 100:
            parts.append(f"Alternative suppliers can cover the supply gap (fastest delivery: {supply.supply_gap['fastest_delivery_days']} days).")

        return " ".join(parts)

    def _build_recommendations(self, demand, inventory, supply, production) -> list[str]:
        actions = []
        critical = [s for s in demand.affected_skus if s.severity == "critical"]

        if critical:
            names = ", ".join(s.sku_name for s in critical[:3])
            actions.append(f"URGENT: Pre-build safety stock for critical SKUs ({names}) — stockout imminent within 2 weeks")

        if supply.alternative_suppliers:
            best = supply.alternative_suppliers[0]
            actions.append(f"Activate alternative supplier {best.name} (reliability {best.reliability}%, lead time {best.lead_time_days} days) for expedited delivery")

        if production.production_options:
            actions.append(production.production_options[0].option)

        warning = [s for s in demand.affected_skus if s.severity == "warning"]
        if warning:
            actions.append(f"Monitor {len(warning)} warning-level SKUs and prepare contingency orders if demand sustains")

        actions.append("Communicate revised ETAs to key accounts (Modern Trade, HoReCa) for affected product lines")
        actions.append("Schedule daily supply review meetings until scenario impact window passes (8 weeks)")

        return actions
