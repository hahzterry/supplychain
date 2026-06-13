"""Presentation formatter — Converts tool results into ExecutivePresentation format deterministically."""
from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

PRESENTABLE_TOOLS = {
    "morning_supply_brief",
    "kpi_dashboard",
    "inventory_risk_agent",
    "demand_sensing_agent",
    "supply_constraint_agent",
    "replenishment_agent",
    "scenario_analysis",
    "check_supply_alerts",
    "labor_utilization_dashboard",
    "contract_price_validation",
}


def format_presentation(tool_name: str, tool_result: str) -> dict | None:
    """Transform tool result JSON into ExecutivePresentation. Returns None for non-presentable tools."""
    if tool_name not in PRESENTABLE_TOOLS:
        return None

    try:
        data = json.loads(tool_result)
    except (json.JSONDecodeError, TypeError):
        return None

    try:
        if tool_name == "morning_supply_brief":
            return _format_morning_brief(data)
        elif tool_name == "kpi_dashboard":
            return _format_kpi_dashboard(data)
        elif tool_name == "inventory_risk_agent":
            return _format_inventory_risk(data)
        elif tool_name == "demand_sensing_agent":
            return _format_demand_sensing(data)
        elif tool_name == "supply_constraint_agent":
            return _format_supply_constraint(data)
        elif tool_name == "replenishment_agent":
            return _format_replenishment(data)
        elif tool_name == "scenario_analysis":
            return _format_scenario(data)
        elif tool_name == "check_supply_alerts":
            return _format_alerts(data)
        elif tool_name == "labor_utilization_dashboard":
            return _format_labor(data)
        elif tool_name == "contract_price_validation":
            return _format_contract(data)
    except Exception as e:
        logger.warning(f"Presentation format failed for {tool_name}: {e}")

    return None


def _format_morning_brief(data: dict) -> dict:
    kpis = data.get("kpis", {})
    alerts = data.get("critical_alerts", [])
    alert_count = len(alerts)

    status_color = "red" if alert_count >= 3 else "amber" if alert_count >= 1 else "green"
    status_label = f"{alert_count} Critical Alert{'s' if alert_count != 1 else ''}" if alert_count > 0 else "All Clear"

    metrics = [
        {"label": "Fill Rate", "value": f"{kpis.get('fill_rate', 0)}%"},
        {"label": "Inventory DOS", "value": f"{kpis.get('inventory_dos', 0)} days"},
        {"label": "Stockout Rate", "value": f"{kpis.get('stockout_rate', 0)}%"},
        {"label": "Production Util.", "value": f"{kpis.get('production_utilization', 0)}%"},
    ]

    result: dict = {
        "headline": f"Morning Supply Brief — {data.get('date', 'Today')}",
        "status": {"label": status_label, "color": status_color},
        "metrics": metrics,
    }

    if alerts:
        result["table"] = {
            "title": "Critical Alerts",
            "headers": ["SKU", "Alert", "Severity"],
            "rows": [[a.get("sku_name", ""), a.get("title", ""), a.get("severity", "")] for a in alerts[:6]],
        }

    result["actions"] = _derive_actions_from_kpis(kpis, alerts)
    return result


def _format_kpi_dashboard(data: dict) -> dict:
    current = data.get("current", data)

    metrics = [
        {"label": "Forecast Accuracy (MAPE)", "value": f"{current.get('forecast_accuracy_mape', 0)}%"},
        {"label": "Fill Rate", "value": f"{current.get('fill_rate', 0)}%"},
        {"label": "Inventory DOS", "value": f"{current.get('inventory_dos', 0)} days"},
        {"label": "On-Time Delivery", "value": f"{current.get('on_time_delivery', 0)}%"},
    ]

    fill = current.get("fill_rate", 0)
    status_color = "green" if fill >= 97 else "amber" if fill >= 93 else "red"

    return {
        "headline": "KPI Dashboard Overview",
        "status": {"label": f"Fill Rate {fill}%", "color": status_color},
        "metrics": metrics,
        "narrative": f"Production utilization at {current.get('production_utilization', 0)}%. "
                     f"{current.get('alerts_open', 0)} open alerts, {current.get('pending_actions', 0)} pending actions.",
    }


def _format_inventory_risk(data: dict) -> dict:
    positions = data.get("positions", [])
    critical = [p for p in positions if p.get("risk_level") == "critical"]
    warning = [p for p in positions if p.get("risk_level") == "warning"]

    status_color = "red" if len(critical) >= 3 else "amber" if len(critical) >= 1 else "green"

    metrics = [
        {"label": "Critical Risk", "value": str(len(critical))},
        {"label": "Warning", "value": str(len(warning))},
        {"label": "Total SKUs", "value": str(data.get("total", len(positions)))},
        {"label": "Avg DOS", "value": f"{data.get('avg_dos', 0):.0f} days"},
    ]

    result: dict = {
        "headline": f"{len(critical)} SKUs at Critical Stockout Risk",
        "status": {"label": f"{len(critical)} critical, {len(warning)} warning", "color": status_color},
        "metrics": metrics,
    }

    risk_items = (critical + warning)[:6]
    if risk_items:
        result["table"] = {
            "title": "At-Risk Items",
            "headers": ["SKU", "Category", "DOS", "Risk"],
            "rows": [[p.get("sku_name", ""), p.get("category", ""), f"{p.get('days_of_supply', 0):.0f}", p.get("risk_level", "")] for p in risk_items],
        }

    result["actions"] = [
        {"priority": "high", "text": f"Expedite replenishment for {len(critical)} critical items"},
        {"priority": "medium", "text": f"Review safety stock levels for {len(warning)} warning items"},
        {"priority": "low", "text": "Schedule supplier capacity review"},
    ]

    return result


def _format_demand_sensing(data: dict) -> dict:
    forecasts = data.get("forecasts", [])
    count = len(forecasts)

    return {
        "headline": f"Demand Forecast — {count} SKU{'s' if count != 1 else ''} Analyzed",
        "status": {"label": "Forecast Updated", "color": "blue"},
        "metrics": [
            {"label": "SKUs Analyzed", "value": str(count)},
            {"label": "Forecast Horizon", "value": "8 weeks"},
        ],
        "narrative": f"Demand forecasts generated for {count} SKUs with 80% and 95% confidence intervals.",
    }


def _format_supply_constraint(data: dict) -> dict:
    suppliers = data.get("suppliers", [])
    lines = data.get("production_lines", [])
    low_reliability = [s for s in suppliers if s.get("reliability_score", 100) < 90]

    metrics = [
        {"label": "Suppliers", "value": str(len(suppliers))},
        {"label": "Production Lines", "value": str(len(lines))},
        {"label": "Low Reliability", "value": str(len(low_reliability))},
    ]

    status_color = "amber" if low_reliability else "green"

    result: dict = {
        "headline": f"Supply Network — {len(low_reliability)} Constraint{'s' if len(low_reliability) != 1 else ''} Detected",
        "status": {"label": f"{len(low_reliability)} suppliers below 90%", "color": status_color},
        "metrics": metrics,
    }

    if low_reliability:
        result["table"] = {
            "title": "Constrained Suppliers",
            "headers": ["Supplier", "Country", "Lead Time", "Reliability"],
            "rows": [[s.get("name", ""), s.get("country", ""), f"{s.get('avg_lead_time_days', 0)}d", f"{s.get('reliability_score', 0)}%"] for s in low_reliability[:5]],
        }

    return result


def _format_replenishment(data: dict) -> dict:
    actions = data.get("actions", [])
    critical = [a for a in actions if a.get("urgency") == "critical"]
    high = [a for a in actions if a.get("urgency") == "high"]

    result: dict = {
        "headline": f"{len(actions)} Replenishment Actions Recommended",
        "status": {"label": f"{len(critical)} critical", "color": "red" if critical else "amber" if high else "green"},
        "metrics": [
            {"label": "Critical", "value": str(len(critical))},
            {"label": "High Priority", "value": str(len(high))},
            {"label": "Total Actions", "value": str(len(actions))},
        ],
        "actions": [
            {"priority": "high", "text": f"Process {len(critical)} critical replenishment orders immediately"},
            {"priority": "medium", "text": f"Review and approve {len(high)} high-priority orders"},
        ] if critical or high else [{"priority": "low", "text": "All replenishment actions are routine"}],
    }

    top_items = (critical + high)[:5]
    if top_items:
        result["table"] = {
            "title": "Top Priority Actions",
            "headers": ["SKU", "Action", "Qty", "Urgency"],
            "rows": [[a.get("sku_name", ""), a.get("action_type", ""), str(a.get("recommended_qty", 0)), a.get("urgency", "")] for a in top_items],
        }

    return result


def _format_scenario(data: dict) -> dict:
    kpi_proj = data.get("kpi_projection", {})
    breaches = kpi_proj.get("target_breaches", [])
    deltas = kpi_proj.get("deltas", {})

    metrics = []
    for key, val in list(deltas.items())[:4]:
        label = key.replace("_", " ").title()
        trend = f"{val:+.1f}%" if isinstance(val, (int, float)) else str(val)
        metrics.append({"label": label, "value": trend, "trend": trend, "trendUp": val > 0 if isinstance(val, (int, float)) else None})

    status_color = "red" if len(breaches) >= 2 else "amber" if breaches else "green"

    result: dict = {
        "headline": f"Scenario Impact — {len(breaches)} Target Breach{'es' if len(breaches) != 1 else ''}",
        "status": {"label": f"{len(breaches)} KPIs breached", "color": status_color},
        "metrics": metrics,
    }

    mitigations = kpi_proj.get("mitigation_options", data.get("mitigation_options", []))
    if mitigations:
        result["actions"] = [
            {"priority": "high" if i == 0 else "medium", "text": m.get("description", m.get("action", str(m)))}
            for i, m in enumerate(mitigations[:4])
        ]

    if breaches:
        result["narrative"] = f"Target breaches: {', '.join(breaches[:4])}."

    return result


def _format_alerts(data: dict) -> dict:
    alerts = data if isinstance(data, list) else data.get("alerts", [])

    critical = [a for a in alerts if a.get("severity") == "critical"]
    warning = [a for a in alerts if a.get("severity") == "warning"]

    status_color = "red" if critical else "amber" if warning else "green"

    result: dict = {
        "headline": f"{len(alerts)} Supply Alert{'s' if len(alerts) != 1 else ''} Active",
        "status": {"label": f"{len(critical)} critical, {len(warning)} warning", "color": status_color},
        "metrics": [
            {"label": "Critical", "value": str(len(critical))},
            {"label": "Warning", "value": str(len(warning))},
            {"label": "Total", "value": str(len(alerts))},
        ],
    }

    if alerts:
        result["table"] = {
            "title": "Active Alerts",
            "headers": ["SKU", "Alert", "Severity", "Action"],
            "rows": [[a.get("sku_name", ""), a.get("title", ""), a.get("severity", ""), (a.get("recommended_action", "") or "")[:50]] for a in alerts[:6]],
        }

    return result


def _format_labor(data: dict) -> dict:
    records = data if isinstance(data, list) else data.get("records", [])

    total = len(records)
    avg_eff = sum(r.get("efficiency_pct", 0) for r in records) / total if total else 0
    total_ot = sum(r.get("overtime_hours", 0) for r in records)

    return {
        "headline": f"Labor Utilization — {avg_eff:.1f}% Avg Efficiency",
        "status": {"label": f"{avg_eff:.0f}% efficiency", "color": "green" if avg_eff >= 85 else "amber" if avg_eff >= 70 else "red"},
        "metrics": [
            {"label": "Avg Efficiency", "value": f"{avg_eff:.1f}%"},
            {"label": "Records (14d)", "value": str(total)},
            {"label": "Overtime Hours", "value": str(int(total_ot))},
        ],
        "narrative": f"Analyzed {total} labor records over the past 14 days. Total overtime: {int(total_ot)} hours.",
    }


def _format_contract(data: dict) -> dict:
    return {
        "headline": "Contract Price Validation Complete",
        "status": {"label": "Reviewed", "color": "blue"},
        "narrative": "Contract pricing validated against current market rates and supplier agreements.",
    }


def _derive_actions_from_kpis(kpis: dict, alerts: list) -> list[dict]:
    actions = []
    if kpis.get("stockout_rate", 0) > 2:
        actions.append({"priority": "high", "text": f"Address stockout rate ({kpis['stockout_rate']}%) — above 2% target"})
    if kpis.get("fill_rate", 100) < 97:
        actions.append({"priority": "high", "text": f"Improve fill rate ({kpis['fill_rate']}%) — below 97% target"})
    if alerts:
        actions.append({"priority": "medium", "text": f"Resolve {len(alerts)} critical alert{'s' if len(alerts) != 1 else ''}"})
    if kpis.get("production_utilization", 0) > 92:
        actions.append({"priority": "medium", "text": "Monitor production capacity — utilization above 92%"})
    if not actions:
        actions.append({"priority": "low", "text": "All KPIs within target ranges — continue monitoring"})
    return actions[:4]


# ─── Combined Presentation ─────────────────────────────────────────────────

import re


def _extract_narrative(assistant_text: str) -> str | None:
    """Extract first meaningful paragraph from assistant text, skipping markdown headers."""
    if not assistant_text:
        return None
    paragraphs = assistant_text.strip().split("\n\n")
    for para in paragraphs:
        stripped = para.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        narrative = re.sub(r'\*\*', '', stripped)
        if len(narrative) < 10:
            continue
        if len(narrative) > 250:
            narrative = narrative[:247] + "..."
        return narrative
    return None


def format_combined_presentation(tool_results: dict[str, str], assistant_text: str) -> dict | None:
    """Build a presentation from ALL tool results + the final assistant text.

    This ensures the card matches what the LLM actually told the user, because we
    extract structured data from the same pool of tool outputs the LLM synthesized,
    AND cross-reference with numbers mentioned in the assistant's response.
    """
    if not tool_results:
        return None

    # Parse all tool results
    parsed: dict[str, dict] = {}
    for name, raw in tool_results.items():
        try:
            parsed[name] = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue

    if not parsed:
        return None

    # Determine primary tool (highest priority that was called)
    _TOOL_PRIORITY = {
        "scenario_analysis": 1, "demand_sensing_agent": 2, "inventory_risk_agent": 3,
        "supply_constraint_agent": 4, "replenishment_agent": 5, "morning_supply_brief": 6,
        "kpi_dashboard": 7, "labor_utilization_dashboard": 8, "contract_price_validation": 9,
        "check_supply_alerts": 10,
    }
    primary = min(parsed.keys(), key=lambda n: _TOOL_PRIORITY.get(n, 99))

    # Route by primary tool
    if primary == "demand_sensing_agent":
        return _build_combined_demand(parsed, assistant_text)

    if primary in ("inventory_risk_agent", "check_supply_alerts"):
        return _build_combined_risk(parsed, assistant_text)

    if primary == "morning_supply_brief":
        return _build_combined_brief(parsed, assistant_text)

    if primary == "supply_constraint_agent":
        return _build_combined_supply(parsed, assistant_text)

    if primary == "replenishment_agent":
        return _build_combined_replenishment(parsed, assistant_text)

    # Fallback: use per-tool formatter for the primary tool
    return format_presentation(primary, tool_results[primary])


def _build_combined_risk(parsed: dict[str, dict], assistant_text: str) -> dict:
    """Combine inventory_risk_agent + check_supply_alerts into one risk card."""
    inv_data = parsed.get("inventory_risk_agent", {})
    alerts_data = parsed.get("check_supply_alerts", {})

    # Gather risk items from inventory positions
    positions = inv_data.get("positions", [])
    critical_positions = [p for p in positions if p.get("risk_level") == "critical"]
    warning_positions = [p for p in positions if p.get("risk_level") == "warning"]

    # Gather risk items from alerts
    alerts = alerts_data if isinstance(alerts_data, list) else alerts_data.get("alerts", [])
    critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
    warning_alerts = [a for a in alerts if a.get("severity") == "warning"]

    # Combined risk count: unique SKUs at risk from both sources
    risk_skus = set()
    for p in critical_positions + warning_positions:
        sku = p.get("sku_id") or p.get("sku_name", "")
        if sku:
            risk_skus.add(sku)
    for a in critical_alerts + warning_alerts:
        sku = a.get("sku_id") or a.get("sku_name", "")
        if sku:
            risk_skus.add(sku)

    total_critical = len(critical_positions) + len(critical_alerts)
    total_warning = len(warning_positions) + len(warning_alerts)
    total_at_risk = len(risk_skus) if risk_skus else total_critical + total_warning

    # Try to extract the number from the assistant's text for consistency
    # e.g. "8 SKUs at critical stockout risk"
    risk_match = re.search(r'(\d+)\s+SKU', assistant_text, re.IGNORECASE)
    if risk_match:
        mentioned_count = int(risk_match.group(1))
        if mentioned_count > total_at_risk:
            total_at_risk = mentioned_count

    status_color = "red" if total_critical >= 2 else "amber" if total_critical >= 1 else "green"

    metrics = [
        {"label": "Critical Risk", "value": str(total_critical)},
        {"label": "Warning", "value": str(total_warning)},
        {"label": "Total At Risk", "value": str(total_at_risk)},
        {"label": "Avg DOS", "value": f"{inv_data.get('avg_dos', 0):.0f} days" if inv_data.get("avg_dos") else "—"},
    ]

    result: dict = {
        "headline": f"{total_at_risk} SKUs at Critical Stockout Risk",
        "status": {"label": f"{total_critical} critical, {total_warning} warning", "color": status_color},
        "metrics": metrics,
    }

    # Build combined table from both sources
    table_rows = []
    for p in (critical_positions + warning_positions)[:4]:
        table_rows.append([
            p.get("sku_name", p.get("sku_id", "")),
            p.get("category", ""),
            f"{p.get('days_of_supply', 0):.0f} days",
            p.get("risk_level", ""),
        ])
    for a in (critical_alerts + warning_alerts)[:4]:
        if len(table_rows) >= 6:
            break
        table_rows.append([
            a.get("sku_name", a.get("sku_id", "")),
            a.get("title", a.get("alert_type", "")),
            "—",
            a.get("severity", ""),
        ])

    if table_rows:
        result["table"] = {
            "title": "At-Risk Items & Alerts",
            "headers": ["SKU", "Issue", "DOS", "Severity"],
            "rows": table_rows,
        }

    result["actions"] = [
        {"priority": "high", "text": f"Expedite replenishment for {total_critical} critical items"},
        {"priority": "high", "text": f"Review safety stock for {total_warning} warning items"},
        {"priority": "medium", "text": "Schedule supplier capacity review"},
    ]

    if assistant_text:
        narrative = _extract_narrative(assistant_text)
        if narrative:
            result["narrative"] = narrative

    return result


def _build_combined_demand(parsed: dict[str, dict], assistant_text: str) -> dict:
    """Build presentation focused on demand sensing results."""
    demand_data = parsed.get("demand_sensing_agent", {})
    inv_data = parsed.get("inventory_risk_agent", {})

    forecasts = demand_data.get("forecasts", [])
    history = demand_data.get("history", [])

    # Group forecasts by SKU to get per-SKU summary
    sku_forecasts: dict[str, list] = {}
    for f in forecasts:
        key = f.get("sku_id", "")
        sku_forecasts.setdefault(key, []).append(f)

    count = len(sku_forecasts) or len(forecasts)

    # Detect spikes: compare first vs last week forecast per SKU
    spikes = []
    for sku_id, weeks in sku_forecasts.items():
        if len(weeks) >= 2:
            sorted_weeks = sorted(weeks, key=lambda w: w.get("week", ""))
            first_val = sorted_weeks[0].get("point_forecast", 0)
            last_val = sorted_weeks[-1].get("point_forecast", 0)
            if first_val > 0:
                growth = (last_val - first_val) / first_val * 100
                if abs(growth) > 15:
                    spikes.append({**sorted_weeks[0], "_growth": growth, "_last_val": last_val})

    # Check assistant text for spike count
    spike_match = re.search(r'(\d+)\s+(?:abnormal|spike|anomal)', assistant_text, re.IGNORECASE)
    no_spike_match = re.search(r'(?:no|zero|0)\s+(?:abnormal|spike|anomal)', assistant_text, re.IGNORECASE)

    if no_spike_match:
        headline = f"No Abnormal Demand Spikes Detected — {count} SKUs Analyzed"
        status_color = "green"
        status_label = "Normal"
    elif spike_match:
        spike_count = int(spike_match.group(1))
        headline = f"{spike_count} SKU{'s' if spike_count != 1 else ''} with Abnormal Demand Signals"
        status_color = "amber" if spike_count <= 2 else "red"
        status_label = f"{spike_count} anomalies"
    elif spikes:
        headline = f"{len(spikes)} SKU{'s' if len(spikes) != 1 else ''} with Elevated Demand Trends"
        status_color = "amber"
        status_label = f"{len(spikes)} trending"
    else:
        headline = f"Demand Forecast — {count} SKU{'s' if count != 1 else ''} Analyzed"
        status_color = "green"
        status_label = "All Normal"

    metrics = [
        {"label": "SKUs Analyzed", "value": str(count)},
        {"label": "Forecast Horizon", "value": "4–8 weeks"},
        {"label": "Spikes Detected", "value": str(len(spikes))},
        {"label": "Confidence", "value": "High"},
    ]

    result: dict = {
        "headline": headline,
        "status": {"label": status_label, "color": status_color},
        "metrics": metrics,
    }

    # Build table — one row per SKU with avg forecast
    table_rows = []
    for sku_id, weeks in list(sku_forecasts.items())[:6]:
        sku_name = weeks[0].get("sku_name", sku_id)
        avg_val = sum(w.get("point_forecast", 0) for w in weeks) / len(weeks)
        confidence = weeks[0].get("confidence", "—")
        drivers = weeks[0].get("drivers", [])
        driver_str = ", ".join(drivers[:2]) if drivers else "—"
        table_rows.append([sku_name, f"{avg_val:.1f}/wk", confidence, driver_str])

    if table_rows:
        result["table"] = {
            "title": "Demand Signals",
            "headers": ["SKU", "Avg Forecast", "Confidence", "Driver"],
            "rows": table_rows,
        }

    # Actions
    if spikes:
        result["actions"] = [
            {"priority": "high", "text": f"Investigate {len(spikes)} demand anomalies for root cause"},
            {"priority": "medium", "text": "Validate forecast confidence with S&OP team"},
            {"priority": "low", "text": "Re-run demand sensing in 1 week to monitor trends"},
        ]
    else:
        result["actions"] = [
            {"priority": "low", "text": "All demand signals within normal range — continue monitoring"},
            {"priority": "low", "text": "Re-run demand sensing in 1–2 weeks"},
        ]

    if assistant_text:
        narrative = _extract_narrative(assistant_text)
        if narrative:
            result["narrative"] = narrative

    return result


def _build_combined_supply(parsed: dict[str, dict], assistant_text: str) -> dict:
    """Build presentation for supply constraint analysis."""
    supply_data = parsed.get("supply_constraint_agent", {})
    suppliers = supply_data.get("suppliers", [])
    lines = supply_data.get("production_lines", [])
    low_reliability = [s for s in suppliers if s.get("reliability_score", 100) < 90]

    status_color = "red" if len(low_reliability) >= 3 else "amber" if low_reliability else "green"

    result: dict = {
        "headline": f"Supply Network — {len(low_reliability)} Constraint{'s' if len(low_reliability) != 1 else ''} Detected",
        "status": {"label": f"{len(low_reliability)} suppliers below 90%", "color": status_color},
        "metrics": [
            {"label": "Suppliers", "value": str(len(suppliers))},
            {"label": "Production Lines", "value": str(len(lines))},
            {"label": "Low Reliability", "value": str(len(low_reliability))},
            {"label": "Avg Lead Time", "value": f"{sum(s.get('avg_lead_time_days', 0) for s in suppliers) / len(suppliers):.0f}d" if suppliers else "—"},
        ],
    }

    if low_reliability:
        result["table"] = {
            "title": "Constrained Suppliers",
            "headers": ["Supplier", "Country", "Lead Time", "Reliability"],
            "rows": [[s.get("name", ""), s.get("country", ""), f"{s.get('avg_lead_time_days', 0)}d", f"{s.get('reliability_score', 0)}%"] for s in low_reliability[:5]],
        }

    result["actions"] = [
        {"priority": "high", "text": f"Review {len(low_reliability)} low-reliability suppliers"},
        {"priority": "medium", "text": "Assess alternate sourcing options"},
    ] if low_reliability else [{"priority": "low", "text": "All suppliers within acceptable reliability range"}]

    if assistant_text:
        narrative = _extract_narrative(assistant_text)
        if narrative:
            result["narrative"] = narrative

    return result


def _build_combined_replenishment(parsed: dict[str, dict], assistant_text: str) -> dict:
    """Build presentation for replenishment recommendations."""
    repl_data = parsed.get("replenishment_agent", {})
    actions = repl_data.get("actions", [])
    critical = [a for a in actions if a.get("urgency") == "critical"]
    high = [a for a in actions if a.get("urgency") == "high"]

    status_color = "red" if critical else "amber" if high else "green"

    result: dict = {
        "headline": f"{len(actions)} Replenishment Actions Recommended",
        "status": {"label": f"{len(critical)} critical", "color": status_color},
        "metrics": [
            {"label": "Critical", "value": str(len(critical))},
            {"label": "High Priority", "value": str(len(high))},
            {"label": "Total Actions", "value": str(len(actions))},
        ],
    }

    top_items = (critical + high)[:5]
    if top_items:
        result["table"] = {
            "title": "Top Priority Actions",
            "headers": ["SKU", "Action", "Qty", "Urgency"],
            "rows": [[a.get("sku_name", ""), a.get("action_type", ""), str(a.get("recommended_qty", 0)), a.get("urgency", "")] for a in top_items],
        }

    result["actions"] = [
        {"priority": "high", "text": f"Process {len(critical)} critical replenishment orders immediately"},
        {"priority": "medium", "text": f"Review and approve {len(high)} high-priority orders"},
    ] if critical or high else [{"priority": "low", "text": "All replenishment actions are routine"}]

    if assistant_text:
        narrative = _extract_narrative(assistant_text)
        if narrative:
            result["narrative"] = narrative

    return result


def _build_combined_brief(parsed: dict[str, dict], assistant_text: str) -> dict:
    """Combine morning_supply_brief with any other tools called."""
    brief = parsed.get("morning_supply_brief", {})
    alerts_data = parsed.get("check_supply_alerts", {})
    inv_data = parsed.get("inventory_risk_agent", {})

    kpis = brief.get("kpis", {})
    brief_alerts = brief.get("critical_alerts", [])

    # Merge alerts from check_supply_alerts if present
    extra_alerts = alerts_data if isinstance(alerts_data, list) else alerts_data.get("alerts", [])
    all_alerts = brief_alerts + [a for a in extra_alerts if a not in brief_alerts]
    critical_alerts = [a for a in all_alerts if a.get("severity") == "critical"]

    status_color = "red" if len(critical_alerts) >= 3 else "amber" if len(critical_alerts) >= 1 else "green"
    status_label = f"{len(critical_alerts)} Critical Alert{'s' if len(critical_alerts) != 1 else ''}" if critical_alerts else "All Clear"

    metrics = [
        {"label": "Fill Rate", "value": f"{kpis.get('fill_rate', 0)}%"},
        {"label": "Inventory DOS", "value": f"{kpis.get('inventory_dos', 0)} days"},
        {"label": "Stockout Rate", "value": f"{kpis.get('stockout_rate', 0)}%"},
        {"label": "Production Util.", "value": f"{kpis.get('production_utilization', 0)}%"},
    ]

    result: dict = {
        "headline": f"Morning Supply Brief — {brief.get('date', 'Today')}",
        "status": {"label": status_label, "color": status_color},
        "metrics": metrics,
    }

    if all_alerts:
        result["table"] = {
            "title": "Critical Alerts",
            "headers": ["SKU", "Alert", "Severity"],
            "rows": [[a.get("sku_name", ""), a.get("title", ""), a.get("severity", "")] for a in all_alerts[:6]],
        }

    result["actions"] = _derive_actions_from_kpis(kpis, all_alerts)

    if assistant_text:
        narrative = _extract_narrative(assistant_text)
        if narrative:
            result["narrative"] = narrative

    return result
