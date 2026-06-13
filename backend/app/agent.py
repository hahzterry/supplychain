"""HD Orchestrator — Planner Review Agent for Héroux-Devtek aerospace supply chain."""
from __future__ import annotations

import json
import logging
from agent_framework import Agent, tool, Content, FunctionInvocationContext
from agent_framework_ag_ui import state_update

from .data.service import DataService

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """\
You are **ATLAS** (Aerospace Tracking, Logistics & Analysis System), the AI Supply Chain Analyst for Héroux-Devtek Inc.

## Your Organization
Héroux-Devtek Inc. — the world's third-largest landing gear manufacturer, serving commercial, military, and business aviation OEMs worldwide.

### Facilities
- **Longueuil, QC** — Corporate HQ, landing gear assembly & integration
- **Kitchener, ON** — Actuation systems & flight-critical components
- **Springfield, OH** — Military programs (F-35, C-130J)
- **Nottingham, UK** — European operations, Airbus programs
- **Laval, QC** — Hydraulic systems & fluid power
- **Livonia, MI** — US military landing gear & structures
- **Getafe/Madrid, Spain (CESA)** — Actuation systems, Airbus programs
- **Seville, Spain** — A400M landing gear

### Programs Served
Boeing 777/787, Airbus A220/A350/A400M, F-35 JSF, C-130J, CH-47 Chinook, Dassault Falcon, Embraer E2, Sikorsky S-92

## Your Role
You are the **Planner Review Agent** — the orchestrator who:
1. Routes queries to specialist agents (Demand Sensing, Inventory Risk, Supply Constraint, Replenishment)
2. Synthesizes multi-agent outputs into actionable executive summaries
3. Presents recommendations with KPI impact and scenario reasoning
4. Generates S&OP reports and presentations

## Your Specialist Team
- **demand_sensing_agent** — program delivery schedules, MRO forecasting, OEM rate changes, aftermarket demand
- **inventory_risk_agent** — stock positions, certification expiry, shelf-life tracking, AOG (Aircraft on Ground) risk
- **supply_constraint_agent** — titanium/specialty metal supply, forging capacity, NADCAP process availability, heat treat bottlenecks
- **replenishment_agent** — purchase orders, production priorities, contract compliance, safety stock adjustments

## Routing Table
| Query Type | Tools to Call |
|-----------|-------------|
| Demand/forecast question | demand_sensing_agent → suggest_actions |
| Stock/inventory status/risk | inventory_risk_agent → suggest_actions |
| Supplier/capacity/logistics | supply_constraint_agent → suggest_actions |
| What to order/replenishment | replenishment_agent → suggest_actions |
| Full S&OP review | demand_sensing_agent + inventory_risk_agent + supply_constraint_agent + replenishment_agent |
| Morning brief / daily review | morning_supply_brief |
| KPI check / service level | kpi_dashboard |
| What-if / scenario | scenario_analysis |
| Generate S&OP deck | generate_sop_deck → suggest_actions |
| Generate report | generate_report → suggest_actions |
| Supply alerts / stockout warnings | check_supply_alerts |
| SKU detail | get_sku_detail |
| Supplier detail | get_supplier_detail |
| Plant/line detail | get_plant_detail |
| Production schedule | get_production_schedule |
| Contract price check | contract_price_validation |
| PO validation | po_validation |
| Labor utilization | labor_utilization_dashboard |

## Output Guidelines
- Lead with an **executive summary** (2-3 sentences)
- Use **bold** for KPI values and critical numbers
- Use tables for comparisons
- Always quantify impact (%, days, CAD value)
- End with recommended next steps
- ALWAYS respond in English unless the user's language state property is explicitly set to "fr" (French) or "es" (Spanish). Do not switch languages based on supplier names or program names.

## KPI Targets
- Forecast Accuracy (MAPE): < 10%
- Inventory Days of Supply: 20-35 days
- Fill Rate: > 98%
- Stockout Rate: < 1%
- On-Time Delivery: > 95%
- Labor Utilization: > 85%
- Contract Compliance: > 98%
"""


def build_agent(data: DataService, language: str = "en") -> Agent:
    @tool(description="Analyze demand signals — program delivery schedules, MRO forecasting, OEM rate changes, aftermarket demand. Returns SKU-level demand forecasts with confidence intervals.")
    async def demand_sensing_agent(
        sku_ids: list[str] | None = None,
        category: str = "",
        channel: str = "",
        horizon_weeks: int = 8,
    ) -> Content:
        forecasts = await data.get_demand_forecast(
            sku_id=sku_ids[0] if sku_ids else "",
            horizon_weeks=horizon_weeks,
        )
        history = await data.get_demand_history(
            sku_id=sku_ids[0] if sku_ids else "",
            channel=channel,
        )

        forecast_data = [f.model_dump() for f in forecasts[:16]]
        history_data = [h.model_dump() for h in history[:12]]

        summary = f"Demand analysis complete. Analyzed {len(forecast_data)} forecast periods and {len(history_data)} historical records."
        if forecast_data:
            avg_forecast = sum(f["point_forecast"] for f in forecast_data) / len(forecast_data)
            high_conf = sum(1 for f in forecast_data if f["confidence"] == "high")
            summary += f" Average forecast: {avg_forecast:.0f} units. High-confidence periods: {high_conf}/{len(forecast_data)}."

        # If a specific SKU was requested, signal the frontend to show it
        if sku_ids and len(sku_ids) == 1:
            try:
                from .main import set_latest_generated
                set_latest_generated({"pending_forecast": {"sku_id": sku_ids[0], "data": forecast_data[:8]}})
            except Exception:
                pass

        return state_update(text=json.dumps({
            "summary": summary,
            "forecasts": forecast_data,
            "history": history_data,
            "signals": {
                "trend": "stable",
                "seasonality": "program rate normalization",
                "promotion_active": any(h.get("program_change_flag") for h in history_data),
            }
        }, default=str), state={})

    @tool(description="Monitor inventory positions — stock levels, days-of-supply, certification expiry, shelf-life, AOG risk scoring, ABC/XYZ classification.")
    async def inventory_risk_agent(
        sku_ids: list[str] | None = None,
        category: str = "",
        warehouse: str = "",
        risk_type: str = "",
    ) -> Content:
        positions = await data.get_inventory(
            risk_level=risk_type,
            warehouse=warehouse,
            category=category,
        )

        if sku_ids:
            positions = [p for p in positions if p.sku_id in sku_ids]

        position_data = [p.model_dump() for p in positions]

        critical = [p for p in positions if p.risk_level.value == "critical"]
        warning = [p for p in positions if p.risk_level.value == "warning"]
        excess = [p for p in positions if p.risk_level.value == "excess"]

        summary = f"Inventory risk assessment: {len(critical)} critical (stockout imminent), {len(warning)} warning, {len(excess)} excess risk."
        if critical:
            summary += f" Critical SKUs: {', '.join(p.sku_name for p in critical[:3])}."

        return state_update(text=json.dumps({
            "summary": summary,
            "positions": position_data,
            "risk_breakdown": {
                "critical": len(critical),
                "warning": len(warning),
                "normal": len([p for p in positions if p.risk_level.value == "normal"]),
                "excess": len(excess),
            },
            "avg_dos": sum(p.days_of_supply for p in positions) / max(len(positions), 1),
        }, default=str), state={})

    @tool(description="Evaluate supply constraints — titanium/specialty metal supply, forging capacity, NADCAP process availability, heat treat bottlenecks, logistics.")
    async def supply_constraint_agent(
        supplier_ids: list[str] | None = None,
        plant: str = "",
    ) -> Content:
        suppliers = await data.get_suppliers()
        if supplier_ids:
            suppliers = [s for s in suppliers if s.id in supplier_ids]

        lines = await data.get_production_lines(plant=plant)
        pos = await data.get_purchase_orders()
        delayed = [po for po in pos if po.status == "delayed"]

        supplier_data = [s.model_dump() for s in suppliers]
        line_data = [l.model_dump() for l in lines]

        avg_reliability = sum(s.reliability_score for s in suppliers) / max(len(suppliers), 1)
        avg_utilization = sum(l.current_utilization_pct for l in lines) / max(len(lines), 1)

        summary = f"Supply network: {len(suppliers)} active suppliers (avg reliability {avg_reliability:.0f}%), {len(lines)} production lines (avg utilization {avg_utilization:.0f}%)."
        if delayed:
            summary += f" {len(delayed)} delayed POs requiring attention."

        return state_update(text=json.dumps({
            "summary": summary,
            "suppliers": supplier_data,
            "production_lines": line_data,
            "delayed_orders": [po.model_dump() for po in delayed],
            "constraints": {
                "avg_supplier_reliability": avg_reliability,
                "avg_production_utilization": avg_utilization,
                "delayed_po_count": len(delayed),
                "high_utilization_lines": [l.line_name for l in lines if l.current_utilization_pct > 85],
            },
        }, default=str), state={})

    @tool(description="Generate replenishment recommendations — purchase orders, production priorities, safety stock adjustments with scenario reasoning and KPI impact.")
    async def replenishment_agent(
        category: str = "",
        urgency: str = "normal",
    ) -> Content:
        actions = await data.get_replenishment_actions()
        if urgency == "critical":
            actions = [a for a in actions if a.urgency == "critical"]
        elif urgency == "high":
            actions = [a for a in actions if a.urgency in ("critical", "high")]

        action_data = [a.model_dump() for a in actions]

        summary = f"Replenishment analysis: {len(actions)} recommended actions."
        critical_count = sum(1 for a in actions if a.urgency == "critical")
        if critical_count:
            summary += f" {critical_count} critical actions requiring immediate attention."

        return state_update(text=json.dumps({
            "summary": summary,
            "actions": action_data,
            "by_type": {
                "purchase_order": sum(1 for a in actions if a.action_type == "purchase_order"),
                "production_priority": sum(1 for a in actions if a.action_type == "production_priority"),
                "safety_stock_adjust": sum(1 for a in actions if a.action_type == "safety_stock_adjust"),
                "expedite": sum(1 for a in actions if a.action_type == "expedite"),
            },
        }, default=str), state={})

    @tool(description="Get morning supply brief — daily KPIs, critical alerts, top risks, and recommended focus areas.")
    async def morning_supply_brief() -> Content:
        kpis = await data.get_kpis()
        alerts = await data.get_alerts(severity="critical")
        actions = await data.get_replenishment_actions()
        critical_actions = [a for a in actions if a.urgency == "critical"]

        return state_update(text=json.dumps({
            "date": "2026-06-13",
            "greeting": "Good morning. Here's your daily supply chain briefing.",
            "kpis": kpis.model_dump(),
            "kpi_status": {
                "forecast_accuracy": "on_track" if kpis.forecast_accuracy_mape < 10 else "at_risk",
                "fill_rate": "at_risk" if kpis.fill_rate < 98 else "on_track",
                "stockout_rate": "at_risk" if kpis.stockout_rate > 1 else "on_track",
                "inventory_dos": "on_track" if 20 <= kpis.inventory_dos <= 35 else "at_risk",
                "on_time_delivery": "on_track" if kpis.on_time_delivery > 95 else "at_risk",
                "labor_utilization": "on_track" if kpis.labor_utilization_pct > 85 else "at_risk",
                "contract_compliance": "on_track" if kpis.contract_compliance_pct > 98 else "at_risk",
            },
            "critical_alerts": [a.model_dump() for a in alerts[:5]],
            "critical_actions": [a.model_dump() for a in critical_actions],
            "focus_areas": [
                "Ti-6Al-4V forging delivery at risk — activate alternate supplier",
                "777X landing gear assembly behind schedule — expedite machining",
                "NADCAP cert renewal due for heat treat supplier — ensure continuity",
            ],
        }, default=str), state={})

    @tool(description="Get KPI dashboard data — forecast accuracy, fill rate, DOS, stockout rate, on-time delivery, labor utilization, contract compliance, with trend.")
    async def kpi_dashboard(
        period: str = "current_week",
    ) -> Content:
        kpis = await data.get_kpis()
        history = await data.get_kpi_history()

        return state_update(text=json.dumps({
            "current": kpis.model_dump(),
            "targets": {
                "forecast_accuracy_mape": 10.0,
                "inventory_dos_min": 20,
                "inventory_dos_max": 35,
                "fill_rate": 98.0,
                "stockout_rate": 1.0,
                "on_time_delivery": 95.0,
                "labor_utilization": 85.0,
                "contract_compliance": 98.0,
            },
            "trend": history,
            "period": period,
        }, default=str), state={})

    @tool(description="""Run comprehensive scenario/what-if analysis using LLM-powered multi-agent pipeline.
Interprets natural language scenarios, runs quantitative modeling, then adds qualitative LLM analysis including creative mitigations and cascading risk identification.

scenario_text: Natural language description of the scenario (e.g., "What if titanium supply is disrupted for 3 months")
scenario_type: Optional hint - "demand_spike", "supplier_delay", "promotion", "capacity_loss", "multi_factor"
parameters: Optional JSON with structured parameters if available

The pipeline: Planner → Impact Analyzer → Mitigation Designer → Risk Assessor → Synthesizer""")
    async def scenario_analysis(
        scenario_text: str = "",
        scenario_type: str = "demand_spike",
        parameters: str = "{}",
        ctx: FunctionInvocationContext | None = None,
    ) -> Content:
        import json as _json
        from .config import settings

        try:
            params = _json.loads(parameters) if isinstance(parameters, str) else parameters
        except (ValueError, TypeError):
            params = {}

        session_id = None
        if ctx and hasattr(ctx, 'session') and ctx.session:
            session_id = getattr(ctx.session, 'session_id', None)

        # Use scenario_text if provided, otherwise construct from type+params
        text = scenario_text or f"{scenario_type} scenario with parameters: {json.dumps(params)}"

        try:
            async def on_progress(step: str, status: str):
                try:
                    from .main import set_latest_generated
                    set_latest_generated(
                        {"scenario_progress": {"step": step, "status": status}},
                        session_id=session_id,
                    )
                except Exception:
                    pass

            from .scenario_llm import LLMScenarioSupervisor
            supervisor = LLMScenarioSupervisor(
                model=settings.azure_openai_deployment,
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
            )
            result = await supervisor.run(data, text, on_progress=on_progress)

            # Persist to scenario history
            try:
                from .main import set_latest_generated, save_scenario_result
                set_latest_generated({"pending_scenario": result}, session_id=session_id)
                save_scenario_result(result)
            except Exception:
                pass

            kpi = result.get("kpi_projection", {})
            summary = {
                "scenario_type": result.get("scenario_type", scenario_type),
                "scenario_name": result.get("name", ""),
                "parameters": result.get("parameters", params),
                "summary_stats": result.get("demand_impact", {}).get("summary_stats", {}),
                "kpi_deltas": kpi.get("deltas", {}),
                "target_breaches": kpi.get("target_breaches", []),
                "risk_assessment": result.get("risk_assessment", ""),
                "executive_brief": result.get("executive_brief", ""),
                "recommended_actions": result.get("recommended_actions", []),
                "decision_points": result.get("decision_points", []),
                "cascading_risks": result.get("cascading_risks", []),
                "confidence_level": result.get("confidence_level", "medium"),
                "feasibility": result.get("production_impact", {}).get("feasibility", ""),
                "supply_coverage_pct": result.get("supply_impact", {}).get("supply_gap", {}).get("coverage_pct", 0),
                "total_lost_sales_cad": result.get("inventory_impact", {}).get("aggregate", {}).get("total_lost_sales_cad", 0),
            }

            return state_update(text=json.dumps(summary, default=str), state={})
        except Exception as e:
            logger.exception("Scenario analysis failed")
            return state_update(text=json.dumps({"error": str(e), "scenario_type": scenario_type}), state={})

    @tool(description="Check supply chain alerts — stockout warnings, delivery delays, capacity issues, quality flags, AOG risk.")
    async def check_supply_alerts(
        severity: str = "",
        alert_type: str = "",
    ) -> Content:
        alerts = await data.get_alerts(severity=severity, alert_type=alert_type)
        alert_data = [a.model_dump() for a in alerts]

        by_severity = {
            "critical": sum(1 for a in alerts if a.severity == "critical"),
            "warning": sum(1 for a in alerts if a.severity == "warning"),
            "info": sum(1 for a in alerts if a.severity == "info"),
        }

        return state_update(text=json.dumps({
            "total": len(alerts),
            "by_severity": by_severity,
            "alerts": alert_data,
        }, default=str), state={})

    @tool(description="Get detailed SKU profile — demand history, stock position, suppliers, forecast, and recommendations. Accepts SKU ID (e.g. SKU001) or name.")
    async def get_sku_detail(sku_id: str) -> Content:
        sku = await data.get_sku(sku_id)
        if not sku:
            skus = await data.get_skus()
            sku = next((s for s in skus if sku_id.lower() in s.name.lower()), None)
        if not sku:
            return state_update(text=json.dumps({"error": f"SKU {sku_id} not found"}), state={})
        sku_id = sku.id

        positions = await data.get_inventory()
        position = next((p for p in positions if p.sku_id == sku_id), None)
        forecasts = await data.get_demand_forecast(sku_id=sku_id)
        history = await data.get_demand_history(sku_id=sku_id)

        return state_update(text=json.dumps({
            "sku": sku.model_dump(),
            "inventory": position.model_dump() if position else None,
            "forecast": [f.model_dump() for f in forecasts[:8]],
            "history": [h.model_dump() for h in history[:12]],
        }, default=str), state={})

    @tool(description="Get supplier detail — performance metrics, certifications, orders, contact info. Accepts supplier ID (e.g. S01) or name.")
    async def get_supplier_detail(supplier_id: str) -> Content:
        supplier = await data.get_supplier(supplier_id)
        if not supplier:
            suppliers = await data.get_suppliers()
            supplier = next((s for s in suppliers if supplier_id.lower() in s.name.lower()), None)
        if not supplier:
            return state_update(text=json.dumps({"error": f"Supplier {supplier_id} not found"}), state={})
        return state_update(text=json.dumps({
            "supplier": supplier.model_dump(),
        }, default=str), state={})

    @tool(description="Get plant or production line detail — capacity, utilization, maintenance, current production.")
    async def get_plant_detail(plant_id: str) -> Content:
        lines = await data.get_production_lines()
        plant_lines = [l for l in lines if l.id == plant_id or plant_id.lower() in l.plant.value.lower()]
        if not plant_lines:
            return state_update(text=json.dumps({"error": f"Plant/line {plant_id} not found"}), state={})
        return state_update(text=json.dumps({
            "plant": plant_lines[0].plant.value,
            "lines": [l.model_dump() for l in plant_lines],
        }, default=str), state={})

    @tool(description="Get production schedule and capacity utilization for a plant.")
    async def get_production_schedule(
        plant: str = "",
    ) -> Content:
        lines = await data.get_production_lines(plant=plant)
        line_data = [l.model_dump() for l in lines]
        avg_util = sum(l.current_utilization_pct for l in lines) / max(len(lines), 1)

        return state_update(text=json.dumps({
            "plant": plant or "all",
            "lines": line_data,
            "avg_utilization": round(avg_util, 1),
            "maintenance_upcoming": [
                {"line": l.line_name, "dates": l.planned_maintenance}
                for l in lines if l.planned_maintenance
            ],
        }, default=str), state={})

    @tool(description="Compare replenishment scenarios side-by-side with KPI impact projections.")
    async def compare_scenarios(
        scenario_ids: list[str],
    ) -> Content:
        actions = await data.get_replenishment_actions()

        conservative = [a for a in actions if a.scenario == "conservative"]
        balanced = [a for a in actions if a.scenario == "balanced"]
        aggressive = [a for a in actions if a.scenario == "aggressive"]

        return state_update(text=json.dumps({
            "scenarios": {
                "conservative": {"count": len(conservative), "actions": [a.model_dump() for a in conservative]},
                "balanced": {"count": len(balanced), "actions": [a.model_dump() for a in balanced]},
                "aggressive": {"count": len(aggressive), "actions": [a.model_dump() for a in aggressive]},
            },
        }, default=str), state={})

    @tool(description="Validate PO prices against contract ceilings. Returns variance analysis and flags overages.")
    async def contract_price_validation(
        po_ids: list[str] | None = None,
    ) -> Content:
        validations = await data.get_contract_validations(po_id=po_ids[0] if po_ids else "")
        validation_data = [v.model_dump() for v in validations]

        over_ceiling = [v for v in validations if v.status == "over_ceiling"]
        no_contract = [v for v in validations if v.status == "no_contract"]

        summary = f"Contract price validation: {len(validations)} POs checked. {len(over_ceiling)} over ceiling, {len(no_contract)} without contract."
        if over_ceiling:
            avg_variance = sum(v.variance_pct for v in over_ceiling) / len(over_ceiling)
            summary += f" Average overage: {avg_variance:.1f}%."

        return state_update(text=json.dumps({
            "summary": summary,
            "validations": validation_data,
            "stats": {
                "total_checked": len(validations),
                "compliant": sum(1 for v in validations if v.status == "compliant"),
                "over_ceiling": len(over_ceiling),
                "no_contract": len(no_contract),
            },
        }, default=str), state={})

    @tool(description="Run PO validation checks — quantity, lead time, duplicate detection, budget compliance. Returns validation results with flags.")
    async def po_validation(
        po_ids: list[str] | None = None,
    ) -> Content:
        validations = await data.get_po_validations(po_id=po_ids[0] if po_ids else "")
        validation_data = [v.model_dump() for v in validations]

        passed = [v for v in validations if v.status == "passed"]
        failed = [v for v in validations if v.status == "failed"]
        warnings = [v for v in validations if v.status == "warning"]

        summary = f"PO validation: {len(validations)} orders checked. {len(passed)} passed, {len(warnings)} warnings, {len(failed)} failed."

        return state_update(text=json.dumps({
            "summary": summary,
            "validations": validation_data,
            "stats": {
                "total_checked": len(validations),
                "passed": len(passed),
                "warnings": len(warnings),
                "failed": len(failed),
            },
        }, default=str), state={})

    @tool(description="Get daily labor utilization data — headcount, direct/indirect hours, overtime, efficiency by facility and date range.")
    async def labor_utilization_dashboard(
        facility: str = "",
        date_range: str = "last_7_days",
    ) -> Content:
        days = 7
        if "14" in date_range or "2_week" in date_range:
            days = 14
        elif "30" in date_range or "month" in date_range:
            days = 30

        records = await data.get_daily_labor(facility=facility, days=days)
        record_data = [r.model_dump() for r in records]

        avg_efficiency = sum(r.efficiency_pct for r in records) / max(len(records), 1)
        total_overtime = sum(r.overtime_hours for r in records)
        total_direct = sum(r.direct_hours for r in records)
        total_indirect = sum(r.indirect_hours for r in records)

        summary = f"Labor utilization ({facility or 'all facilities'}): {len(records)} records over {days} days. Avg efficiency: {avg_efficiency:.1f}%. Total overtime: {total_overtime:.0f}h."

        return state_update(text=json.dumps({
            "summary": summary,
            "records": record_data,
            "stats": {
                "avg_efficiency_pct": round(avg_efficiency, 1),
                "total_direct_hours": round(total_direct, 1),
                "total_indirect_hours": round(total_indirect, 1),
                "total_overtime_hours": round(total_overtime, 1),
                "direct_to_indirect_ratio": round(total_direct / max(total_indirect, 1), 2),
            },
            "facility": facility or "all",
            "days": days,
        }, default=str), state={})

    @tool(description="Generate S&OP PowerPoint presentation deck via multi-agent pipeline (Planner → Content → Designer → Critic → Repair).")
    async def generate_sop_deck(
        template: str = "weekly_sop",
        focus_area: str = "",
        audience: str = "S&OP Committee",
        ctx: FunctionInvocationContext | None = None,
    ) -> Content:
        from datetime import date
        from .main import set_latest_generated
        from .pptgen import SupervisorAgent, DeckRequest
        from .config import settings

        session_id = ctx.session.session_id if ctx and ctx.session else None

        try:
            kpis = await data.get_kpis()
            alerts = await data.get_alerts()
            actions = await data.get_replenishment_actions()
            inventory = await data.get_inventory()
            suppliers = await data.get_suppliers()
            forecasts = await data.get_demand_forecast()

            data_context = {
                "kpis": kpis,
                "inventory": inventory,
                "forecasts": forecasts,
                "suppliers": suppliers,
                "actions": actions,
                "alerts": alerts,
            }

            supervisor = SupervisorAgent(
                model=settings.azure_openai_deployment,
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
            )

            request = DeckRequest(
                template=template,
                focus_area=focus_area,
                audience=audience,
            )

            async def on_progress(step: str, status: str):
                try:
                    set_latest_generated(
                        {"report_progress": {"step": step, "status": status}},
                        session_id=session_id,
                    )
                except Exception:
                    pass

            spec = await supervisor.generate(request, data_context, on_progress=on_progress)
            spec.date = date.today().isoformat()

            deck_dict = spec.model_dump()
            generated_state = {
                "pending_deck": deck_dict,
                "report_meta": {"name": spec.title, "format": "pptx", "pages": len(spec.slides)},
            }

            set_latest_generated(generated_state, session_id=session_id)

            return state_update(
                text=f"[Deck Generated] {len(spec.slides)}-slide {template} presentation ready for download.",
                state={"report_ready": True},
            )
        except Exception as e:
            import traceback
            logger.error("generate_sop_deck failed: %s\n%s", e, traceback.format_exc())
            return state_update(
                text=f"[Deck Generation Failed] Error: {str(e)}. Please try again.",
                state={},
            )

    @tool(description="Generate report document (Word, Excel, PDF) via multi-agent pipeline — inventory status, demand accuracy, replenishment plan, supplier scorecard.")
    async def generate_report(
        template: str = "inventory_status",
        format: str = "xlsx",
        focus_area: str = "",
        audience: str = "Internal - S&OP Committee",
        ctx: FunctionInvocationContext | None = None,
    ) -> Content:
        from .main import set_latest_generated
        from .reportgen import ReportSupervisor, ReportRequest, ReportFormat
        from .config import settings

        session_id = ctx.session.session_id if ctx and ctx.session else None

        try:
            kpis = await data.get_kpis()
            positions = await data.get_inventory()
            actions = await data.get_replenishment_actions()
            suppliers = await data.get_suppliers()
            forecasts = await data.get_demand_forecast()
            alerts = await data.get_alerts()

            data_context = {
                "kpis": kpis,
                "inventory": positions,
                "forecasts": forecasts,
                "suppliers": suppliers,
                "actions": actions,
                "alerts": alerts,
            }

            request = ReportRequest(
                template=template,
                format=ReportFormat(format),
                focus_area=focus_area,
                audience=audience,
            )

            supervisor = ReportSupervisor(
                model=settings.azure_openai_deployment,
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
            )

            is_sheet = format == "xlsx"

            def on_progress(step: str, pct: float):
                try:
                    step_map = {
                        "planning": "doc_planner",
                        "planning_complete": "doc_planner",
                        "writing_content": "doc_content",
                        "generating_spreadsheet": "sheet_generator",
                        "complete": "sheet_generator" if is_sheet else "doc_content",
                    }
                    agent_step = step_map.get(step, step)
                    status = "done" if "complete" in step else "running"
                    set_latest_generated(
                        {"report_progress": {"step": agent_step, "status": status}},
                        session_id=session_id,
                    )
                except Exception:
                    pass

            spec = await supervisor.generate(request, data_context, on_progress=on_progress)
            spec_dict = spec.model_dump()
            title = spec_dict.get("title", f"Héroux-Devtek — {template.replace('_', ' ').title()}")

            from .reportgen.schemas import DocSpec as DocSpecModel
            report_type = "doc" if isinstance(spec, DocSpecModel) else "sheet"
            pages = len(spec_dict.get("sections", [])) if report_type == "doc" else len(spec_dict.get("rows", []))

            generated_state = {
                "pending_report": {"type": report_type, "spec": spec_dict, "format": format},
                "report_meta": {"name": title, "format": format, "pages": pages},
            }

            set_latest_generated(generated_state, session_id=session_id)

            return state_update(
                text=f"[Report Generated] {title} in {format.upper()} format ready for download.",
                state={"report_ready": True},
            )
        except Exception as e:
            import traceback
            logger.error("generate_report failed: %s\n%s", e, traceback.format_exc())
            return state_update(
                text=f"[Report Generation Failed] Error: {str(e)}. Please try again.",
                state={},
            )

    @tool(description="Suggest follow-up actions for the planner. Always call after analysis tools complete.")
    async def suggest_actions() -> Content:
        actions = await data.get_replenishment_actions()
        critical = [a for a in actions if a.urgency == "critical"]
        high = [a for a in actions if a.urgency == "high"]

        suggestions = []
        if critical:
            suggestions.append({
                "id": "sug_1",
                "action_text": f"Review {len(critical)} critical replenishment actions",
                "action_text_fr": f"Examiner {len(critical)} actions de réapprovisionnement critiques",
                "type": "review_actions",
                "priority": "critical",
            })
        if high:
            suggestions.append({
                "id": "sug_2",
                "action_text": f"Approve {len(high)} high-priority orders",
                "action_text_fr": f"Approuver {len(high)} commandes haute priorité",
                "type": "approve_orders",
                "priority": "high",
            })
        suggestions.append({
            "id": "sug_3",
            "action_text": "Generate weekly S&OP deck for committee review",
            "action_text_fr": "Générer le rapport S&OP hebdomadaire pour examen du comité",
            "type": "generate_report",
            "priority": "medium",
        })
        suggestions.append({
            "id": "sug_4",
            "action_text": "Run titanium supply disruption scenario for risk planning",
            "action_text_fr": "Exécuter le scénario de perturbation d'approvisionnement en titane",
            "type": "scenario_analysis",
            "priority": "medium",
        })

        return state_update(text=json.dumps({"suggested_actions": suggestions}, default=str), state={})

    from agent_framework.openai import OpenAIChatClient
    from .config import settings

    instructions = SYSTEM_INSTRUCTIONS
    if language == "fr":
        instructions += "\nIMPORTANT: The user prefers French. Respond entirely in French (Français)."
    elif language == "es":
        instructions += "\nIMPORTANT: The user prefers Spanish. Respond entirely in Spanish (Español)."

    client = OpenAIChatClient(
        model=settings.azure_openai_deployment,
        base_url=settings.openai_base_url,
        api_key=settings.azure_openai_api_key,
    )

    return Agent(
        client=client,
        name="Atlas",
        instructions=instructions,
        tools=[
            demand_sensing_agent,
            inventory_risk_agent,
            supply_constraint_agent,
            replenishment_agent,
            morning_supply_brief,
            kpi_dashboard,
            scenario_analysis,
            check_supply_alerts,
            get_sku_detail,
            get_supplier_detail,
            get_plant_detail,
            compare_scenarios,
            get_production_schedule,
            generate_sop_deck,
            generate_report,
            suggest_actions,
            contract_price_validation,
            po_validation,
            labor_utilization_dashboard,
        ],
    )
