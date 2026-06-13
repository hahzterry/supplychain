"""FastAPI application with AG-UI endpoint for HD ATLAS multi-agent system."""
from __future__ import annotations

import app._patch_message_order  # noqa: F401  # fix CopilotKit message ordering

import contextvars
import json as _json
from pathlib import Path
from datetime import date
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from agent_framework.ag_ui import AgentFrameworkAgent
try:
    from agent_framework.observability import enable_instrumentation
except ImportError:
    enable_instrumentation = None

from .agent import build_agent
from .data.service import MockDataService
from .config import settings
from .storage import BlobStorageService, LOCAL_STORAGE_DIR
from .reports_store import ReportsStore, ReportRecord

current_session_id: contextvars.ContextVar[str] = contextvars.ContextVar("current_session_id", default="default")

if settings.applicationinsights_connection_string and enable_instrumentation:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(connection_string=settings.applicationinsights_connection_string)
        enable_instrumentation(enable_sensitive_data=True)
    except ImportError:
        pass

app = FastAPI(title="HD Atlas Supply Chain API")


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.headers.get("x-session-id", "default")
        token = current_session_id.set(session_id)
        try:
            response = await call_next(request)
        finally:
            current_session_id.reset(token)
        return response


app.add_middleware(SessionMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_service = MockDataService()
blob_service = BlobStorageService()
reports_store = ReportsStore()

agent = build_agent(data_service, language="en")

ag_ui_agent = AgentFrameworkAgent(
    agent=agent,
    name="hd_orchestrator",
    description="HD ATLAS multi-agent system: orchestrator delegates to Demand Sensing, Inventory Risk, Supply Constraint, and Replenishment agents",
)


def _fix_dangling_tool_calls(messages: list[dict]) -> list[dict]:
    """Fix conversations where a previous tool call never returned a result."""
    # Filter reasoning messages (extended thinking from Kimi/o-series models)
    messages = [m for m in messages if m.get("role") != "reasoning"]

    pending_call_ids: set[str] = set()
    result = []

    for msg in messages:
        role = msg.get("role", "")

        if role == "assistant":
            tool_calls = msg.get("toolCalls") or msg.get("tool_calls") or []
            call_ids = set()
            for tc in tool_calls:
                cid = tc.get("id") or tc.get("call_id", "")
                if cid:
                    call_ids.add(cid)
            pending_call_ids = call_ids if call_ids else set()
            result.append(msg)

        elif role == "tool":
            cid = msg.get("tool_call_id") or msg.get("call_id", "")
            pending_call_ids.discard(cid)
            result.append(msg)

        else:
            if pending_call_ids:
                for cid in pending_call_ids:
                    result.append({
                        "role": "tool",
                        "tool_call_id": cid,
                        "content": "Tool execution was interrupted. Please retry if needed.",
                    })
                pending_call_ids = set()
            result.append(msg)

    if pending_call_ids:
        for cid in pending_call_ids:
            result.append({
                "role": "tool",
                "tool_call_id": cid,
                "content": "Tool execution was interrupted. Please retry if needed.",
            })

    return result

import copy
import logging
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint

_agent_logger = logging.getLogger("app.agent_patch")

# Monkey-patch the agent's run method to fix dangling tool calls in messages
_original_run = ag_ui_agent.run

async def _patched_run(input_data, *args, **kwargs):
    messages = input_data.get("messages", [])
    if messages:
        input_data["messages"] = _fix_dangling_tool_calls(messages)
    try:
        async for event in _original_run(input_data, *args, **kwargs):
            yield event
    except Exception as e:
        _agent_logger.exception(f"Error in agent run: {e}")
        raise

ag_ui_agent.run = _patched_run

add_agent_framework_fastapi_endpoint(
    app,
    ag_ui_agent,
    path="/api/agent",
    allow_origins=settings.cors_origins,
    default_state={"language": "en"},
)


from fastapi.staticfiles import StaticFiles

_static_dir = Path(__file__).resolve().parent.parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


# ─── Chat SSE Endpoint ────────────────────────────────────────────────────

import logging as _logging
logger = _logging.getLogger(__name__)

from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from .presentation import format_presentation, PRESENTABLE_TOOLS

_chat_sessions: dict[str, list[dict]] = {}
_MAX_SESSION_MESSAGES = 20

_openai_client = AsyncOpenAI(
    base_url=settings.openai_base_url,
    api_key=settings.azure_openai_api_key,
    timeout=120.0,
)



from .agent import SYSTEM_INSTRUCTIONS

TOOL_DEFS = [
    {"type": "function", "function": {"name": "demand_sensing_agent", "description": "Analyze demand signals — program delivery schedules, MRO forecasting, OEM rate changes.", "parameters": {"type": "object", "properties": {"sku_ids": {"type": "array", "items": {"type": "string"}}, "category": {"type": "string"}, "horizon_weeks": {"type": "integer"}}, "required": []}}},
    {"type": "function", "function": {"name": "inventory_risk_agent", "description": "Monitor inventory positions — stock levels, days-of-supply, certification expiry, AOG risk.", "parameters": {"type": "object", "properties": {"sku_ids": {"type": "array", "items": {"type": "string"}}, "category": {"type": "string"}, "risk_type": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "supply_constraint_agent", "description": "Evaluate supply constraints — titanium/specialty metal supply, forging capacity, NADCAP process availability.", "parameters": {"type": "object", "properties": {"supplier_ids": {"type": "array", "items": {"type": "string"}}, "plant": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "replenishment_agent", "description": "Generate replenishment recommendations — purchase orders, production priorities, safety stock adjustments.", "parameters": {"type": "object", "properties": {"category": {"type": "string"}, "urgency": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "morning_supply_brief", "description": "Get morning supply brief — daily KPIs, critical alerts, top risks, and recommended focus areas.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "kpi_dashboard", "description": "Get KPI dashboard data — forecast accuracy, fill rate, DOS, stockout rate, on-time delivery.", "parameters": {"type": "object", "properties": {"period": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "scenario_analysis", "description": "Run comprehensive scenario/what-if analysis.", "parameters": {"type": "object", "properties": {"scenario_text": {"type": "string"}, "scenario_type": {"type": "string"}}, "required": ["scenario_text"]}}},
    {"type": "function", "function": {"name": "check_supply_alerts", "description": "Check supply chain alerts — stockout warnings, delivery delays, capacity issues.", "parameters": {"type": "object", "properties": {"severity": {"type": "string"}, "alert_type": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "get_sku_detail", "description": "Get detailed SKU profile. Accepts SKU ID or name.", "parameters": {"type": "object", "properties": {"sku_id": {"type": "string"}}, "required": ["sku_id"]}}},
    {"type": "function", "function": {"name": "get_supplier_detail", "description": "Get supplier detail — performance, certifications, orders.", "parameters": {"type": "object", "properties": {"supplier_id": {"type": "string"}}, "required": ["supplier_id"]}}},
    {"type": "function", "function": {"name": "get_plant_detail", "description": "Get plant or production line detail.", "parameters": {"type": "object", "properties": {"plant_id": {"type": "string"}}, "required": ["plant_id"]}}},
    {"type": "function", "function": {"name": "get_production_schedule", "description": "Get production schedule and capacity utilization.", "parameters": {"type": "object", "properties": {"plant": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "generate_sop_deck", "description": "Generate S&OP PowerPoint presentation deck.", "parameters": {"type": "object", "properties": {"template": {"type": "string"}, "focus_area": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "generate_report", "description": "Generate report document (Word, Excel, PDF).", "parameters": {"type": "object", "properties": {"template": {"type": "string"}, "format": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "labor_utilization_dashboard", "description": "Get daily labor utilization data.", "parameters": {"type": "object", "properties": {"facility": {"type": "string"}, "date_range": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "contract_price_validation", "description": "Validate PO prices against contract ceilings.", "parameters": {"type": "object", "properties": {"po_ids": {"type": "array", "items": {"type": "string"}}}, "required": []}}},
]

TOOL_AGENT_NAMES = {
    "demand_sensing_agent": "Demand Sensing",
    "inventory_risk_agent": "Inventory Risk",
    "supply_constraint_agent": "Supply Constraint",
    "replenishment_agent": "Replenishment",
    "morning_supply_brief": "Atlas AI",
    "kpi_dashboard": "Atlas AI",
    "scenario_analysis": "Scenario Planner",
    "check_supply_alerts": "Atlas AI",
    "get_sku_detail": "Atlas AI",
    "get_supplier_detail": "Atlas AI",
    "get_plant_detail": "Atlas AI",
    "get_production_schedule": "Atlas AI",
    "generate_sop_deck": "Deck Generator",
    "generate_report": "Report Generator",
    "labor_utilization_dashboard": "Atlas AI",
    "contract_price_validation": "Atlas AI",
}


import re as _re


def _parse_scenario_text(text: str) -> tuple[str, dict]:
    """Extract scenario_type and params from free-text scenario description."""
    text_lower = text.lower()
    numbers = [float(m) for m in _re.findall(r'(\d+(?:\.\d+)?)', text)]

    if any(w in text_lower for w in ("disrupt", "shortage", "capacity loss", "sanction")):
        pct = next((n for n in numbers if n <= 100), 60)
        return "capacity_loss", {"affected_categories": ["Raw Materials"], "disruption_pct": pct}

    if any(w in text_lower for w in ("delay", "late", "maintenance")):
        days = next((n for n in numbers if n <= 365), 14)
        return "supplier_delay", {"delay_days": int(days), "affected_categories": ["Raw Materials"]}

    if any(w in text_lower for w in ("spike", "surge", "increase", "rate")):
        pct = next((n for n in numbers if n <= 200), 30)
        return "demand_spike", {"spike_pct": pct}

    if any(w in text_lower for w in ("promotion", "campaign")):
        pct = next((n for n in numbers if n <= 100), 25)
        return "promotion", {"uplift_pct": pct}

    pct = next((n for n in numbers if n <= 100), 30)
    return "demand_spike", {"spike_pct": pct}


async def _execute_tool(name: str, args: dict) -> str:
    """Execute a tool and return its result as a string."""
    import json as _j
    ds = data_service

    if name == "demand_sensing_agent":
        forecasts = await ds.get_demand_forecast(sku_id=args.get("sku_ids", [""])[0] if args.get("sku_ids") else "", horizon_weeks=args.get("horizon_weeks", 8))
        history = await ds.get_demand_history(sku_id=args.get("sku_ids", [""])[0] if args.get("sku_ids") else "")
        return _j.dumps({"forecasts": [f.model_dump() for f in forecasts[:12]], "history": [h.model_dump() for h in history[:8]]}, default=str)

    elif name == "inventory_risk_agent":
        # Map LLM-generated risk_type values to valid enum values
        risk_type_raw = args.get("risk_type", "")
        _RISK_MAP = {"stockout": "critical", "high": "critical", "low": "healthy", "at_risk": "critical", "at-risk": "critical"}
        risk_level = _RISK_MAP.get(risk_type_raw.lower(), risk_type_raw) if risk_type_raw else ""
        positions = await ds.get_inventory(risk_level=risk_level, category=args.get("category", ""))
        if args.get("sku_ids"):
            positions = [p for p in positions if p.sku_id in args["sku_ids"]]
        critical = [p for p in positions if p.risk_level.value == "critical"]
        warning = [p for p in positions if p.risk_level.value == "warning"]
        avg_dos = sum(p.days_of_supply for p in positions) / len(positions) if positions else 0
        return _j.dumps({"positions": [p.model_dump() for p in positions], "critical_count": len(critical), "warning_count": len(warning), "total": len(positions), "avg_dos": avg_dos}, default=str)

    elif name == "supply_constraint_agent":
        suppliers = await ds.get_suppliers()
        if args.get("supplier_ids"):
            suppliers = [s for s in suppliers if s.id in args["supplier_ids"]]
        lines = await ds.get_production_lines(plant=args.get("plant", ""))
        return _j.dumps({"suppliers": [s.model_dump() for s in suppliers], "production_lines": [l.model_dump() for l in lines]}, default=str)

    elif name == "replenishment_agent":
        actions = await ds.get_replenishment_actions()
        if args.get("urgency") == "critical":
            actions = [a for a in actions if a.urgency == "critical"]
        return _j.dumps({"actions": [a.model_dump() for a in actions]}, default=str)

    elif name == "morning_supply_brief":
        kpis = await ds.get_kpis()
        alerts = await ds.get_alerts(severity="critical")
        return _j.dumps({"date": "2026-06-13", "kpis": kpis.model_dump(), "critical_alerts": [a.model_dump() for a in alerts[:5]]}, default=str)

    elif name == "kpi_dashboard":
        kpis = await ds.get_kpis()
        return _j.dumps({"current": kpis.model_dump()}, default=str)

    elif name == "scenario_analysis":
        from .scenario.supervisor import ScenarioSupervisor
        from .config import settings as _settings

        session_id = current_session_id.get("default")
        scenario_text = args.get("scenario_text", "")
        scenario_type = args.get("scenario_type", "")

        _VALID_TYPES = {"demand_spike", "supplier_delay", "promotion", "capacity_loss"}
        if scenario_type in _VALID_TYPES:
            sc_params = args.get("parameters", {})
        else:
            scenario_type, sc_params = _parse_scenario_text(scenario_text)

        supervisor = ScenarioSupervisor(
            model=_settings.azure_openai_deployment,
            azure_endpoint=_settings.azure_openai_endpoint,
            api_key=_settings.azure_openai_api_key,
        )

        import asyncio as _aio

        async def _scenario_progress(step: str, status: str):
            set_latest_generated({"scenario_progress": {"step": step, "status": status}}, session_id=session_id)
            await _aio.sleep(0.4)

        result = await supervisor.run(
            data_service, scenario_type, sc_params,
            on_progress=_scenario_progress, scenario_text=scenario_text,
        )

        set_latest_generated({"pending_scenario": result}, session_id=session_id)
        save_scenario_result(result)

        return _j.dumps(result, default=str)

    elif name == "check_supply_alerts":
        alerts = await ds.get_alerts(severity=args.get("severity", ""), alert_type=args.get("alert_type", ""))
        return _j.dumps({"total": len(alerts), "alerts": [a.model_dump() for a in alerts]}, default=str)

    elif name == "get_sku_detail":
        sku = await ds.get_sku(args.get("sku_id", ""))
        if not sku:
            skus = await ds.get_skus()
            sku = next((s for s in skus if args.get("sku_id", "").lower() in s.name.lower()), None)
        if not sku:
            return _j.dumps({"error": f"SKU {args.get('sku_id')} not found"})
        return _j.dumps({"sku": sku.model_dump()}, default=str)

    elif name == "get_supplier_detail":
        supplier = await ds.get_supplier(args.get("supplier_id", ""))
        if not supplier:
            suppliers = await ds.get_suppliers()
            supplier = next((s for s in suppliers if args.get("supplier_id", "").lower() in s.name.lower()), None)
        if not supplier:
            return _j.dumps({"error": f"Supplier {args.get('supplier_id')} not found"})
        return _j.dumps({"supplier": supplier.model_dump()}, default=str)

    elif name == "get_plant_detail":
        lines = await ds.get_production_lines()
        plant_lines = [l for l in lines if l.id == args.get("plant_id") or args.get("plant_id", "").lower() in l.plant.value.lower()]
        return _j.dumps({"lines": [l.model_dump() for l in plant_lines]}, default=str)

    elif name == "get_production_schedule":
        lines = await ds.get_production_lines(plant=args.get("plant", ""))
        return _j.dumps({"lines": [l.model_dump() for l in lines]}, default=str)

    elif name == "generate_sop_deck":
        from .pptgen import SupervisorAgent as DeckSupervisor, DeckRequest
        from .config import settings as _settings
        from datetime import date as _date

        session_id = current_session_id.get("default")
        template = args.get("template", "weekly_sop")
        focus_area = args.get("focus_area", "")
        deck_audience = args.get("audience", "S&OP Committee")

        kpis = await ds.get_kpis()
        alerts = await ds.get_alerts()
        actions_data = await ds.get_replenishment_actions()
        inv_data = await ds.get_inventory()
        suppliers_data = await ds.get_suppliers()
        forecasts_data = await ds.get_demand_forecast()

        data_context = {
            "kpis": kpis, "inventory": inv_data, "forecasts": forecasts_data,
            "suppliers": suppliers_data, "actions": actions_data, "alerts": alerts,
        }

        supervisor = DeckSupervisor(
            model=_settings.azure_openai_deployment,
            azure_endpoint=_settings.azure_openai_endpoint,
            api_key=_settings.azure_openai_api_key,
        )
        request_obj = DeckRequest(template=template, focus_area=focus_area, audience=deck_audience)

        async def _deck_progress(step: str, status: str):
            try:
                set_latest_generated({"report_progress": {"step": step, "status": status}}, session_id=session_id)
            except Exception:
                pass

        spec = await supervisor.generate(request_obj, data_context, on_progress=_deck_progress)
        spec.date = _date.today().isoformat()
        deck_dict = spec.model_dump()

        set_latest_generated({
            "pending_deck": deck_dict,
            "report_meta": {"name": spec.title, "format": "pptx", "pages": len(spec.slides)},
        }, session_id=session_id)

        return _j.dumps({"status": "complete", "title": spec.title, "format": "pptx", "slides": len(spec.slides)})

    elif name == "generate_report":
        from .reportgen import ReportSupervisor, ReportRequest, ReportFormat
        from .config import settings as _settings

        session_id = current_session_id.get("default")
        template = args.get("template", "inventory_status")
        fmt = args.get("format", "xlsx")
        focus_area = args.get("focus_area", "")
        report_audience = args.get("audience", "S&OP Committee")

        kpis = await ds.get_kpis()
        inv_data = await ds.get_inventory()
        actions_data = await ds.get_replenishment_actions()
        suppliers_data = await ds.get_suppliers()
        forecasts_data = await ds.get_demand_forecast()
        alerts_data = await ds.get_alerts()

        data_context = {
            "kpis": kpis, "inventory": inv_data, "forecasts": forecasts_data,
            "suppliers": suppliers_data, "actions": actions_data, "alerts": alerts_data,
        }

        request_obj = ReportRequest(
            template=template, format=ReportFormat(fmt),
            focus_area=focus_area, audience=report_audience,
        )

        supervisor = ReportSupervisor(
            model=_settings.azure_openai_deployment,
            azure_endpoint=_settings.azure_openai_endpoint,
            api_key=_settings.azure_openai_api_key,
        )

        is_sheet = fmt == "xlsx"

        def _report_progress(step: str, pct: float):
            try:
                step_map = {
                    "planning": "doc_planner", "planning_complete": "doc_planner",
                    "writing_content": "doc_content", "generating_spreadsheet": "sheet_generator",
                    "complete": "sheet_generator" if is_sheet else "doc_content",
                }
                agent_step = step_map.get(step, step)
                status = "done" if "complete" in step else "running"
                set_latest_generated({"report_progress": {"step": agent_step, "status": status}}, session_id=session_id)
            except Exception:
                pass

        spec = await supervisor.generate(request_obj, data_context, on_progress=_report_progress)
        spec_dict = spec.model_dump()
        title = spec_dict.get("title", f"Héroux-Devtek — {template.replace('_', ' ').title()}")

        from .reportgen.schemas import DocSpec as _DocSpecModel
        report_type = "doc" if isinstance(spec, _DocSpecModel) else "sheet"
        pages = len(spec_dict.get("sections", [])) if report_type == "doc" else len(spec_dict.get("rows", []))

        set_latest_generated({
            "pending_report": {"type": report_type, "spec": spec_dict, "format": fmt},
            "report_meta": {"name": title, "format": fmt, "pages": pages},
        }, session_id=session_id)

        return _j.dumps({"status": "complete", "title": title, "format": fmt, "pages": pages})

    elif name == "labor_utilization_dashboard":
        records = await ds.get_daily_labor(facility=args.get("facility", ""), days=7)
        return _j.dumps({"records": [r.model_dump() for r in records]}, default=str)

    elif name == "contract_price_validation":
        validations = await ds.get_contract_validations(po_id=args.get("po_ids", [""])[0] if args.get("po_ids") else "")
        return _j.dumps({"validations": [v.model_dump() for v in validations]}, default=str)

    return _j.dumps({"error": f"Unknown tool: {name}"})


@app.post("/api/chat")
async def chat_stream(request: Request):
    body = await request.json()
    message = body.get("message", "")
    session_id = body.get("session_id", "default")
    language = body.get("language", "en")

    # Get or create session history
    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = []

    history = _chat_sessions[session_id]
    history.append({"role": "user", "content": message})

    # Trim to max session length
    if len(history) > _MAX_SESSION_MESSAGES:
        history[:] = history[-_MAX_SESSION_MESSAGES:]

    # Build system instruction
    instructions = SYSTEM_INSTRUCTIONS
    if language == "fr":
        instructions += "\nIMPORTANT: The user prefers French. Respond entirely in French (Français)."
    elif language == "es":
        instructions += "\nIMPORTANT: The user prefers Spanish. Respond entirely in Spanish (Español)."

    messages_for_api = [{"role": "system", "content": instructions}] + history

    async def generate():
        import json as _j
        tools_called = []
        all_tool_results: dict[str, str] = {}

        try:
            # Streaming with tool use loop
            current_messages = list(messages_for_api)
            max_iterations = 5

            for _ in range(max_iterations):
                stream = await _openai_client.chat.completions.create(
                    model=settings.azure_openai_deployment,
                    messages=current_messages,
                    tools=TOOL_DEFS,
                    stream=True,
                    max_completion_tokens=4000,
                )

                tool_calls_in_progress: dict[int, dict] = {}
                assistant_content = ""
                finish_reason = None

                async for chunk in stream:
                    choice = chunk.choices[0] if chunk.choices else None
                    if not choice:
                        continue

                    delta = choice.delta
                    finish_reason = choice.finish_reason

                    # Stream text content
                    if delta and delta.content:
                        assistant_content += delta.content
                        yield f"event: delta\ndata: {_j.dumps({'content': delta.content})}\n\n"

                    # Accumulate tool calls
                    if delta and delta.tool_calls:
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_in_progress:
                                tool_calls_in_progress[idx] = {"id": "", "name": "", "arguments": ""}
                            if tc.id:
                                tool_calls_in_progress[idx]["id"] = tc.id
                            if tc.function and tc.function.name:
                                tool_calls_in_progress[idx]["name"] = tc.function.name
                            if tc.function and tc.function.arguments:
                                tool_calls_in_progress[idx]["arguments"] += tc.function.arguments

                # If no tool calls, we're done
                if finish_reason != "tool_calls" or not tool_calls_in_progress:
                    # Save assistant message to history
                    if assistant_content:
                        history.append({"role": "assistant", "content": assistant_content})
                    break

                # Process tool calls
                tool_call_messages = []
                for idx in sorted(tool_calls_in_progress.keys()):
                    tc = tool_calls_in_progress[idx]
                    tool_name = tc["name"]
                    tools_called.append(tool_name)

                    # Emit planning event
                    agent_name = TOOL_AGENT_NAMES.get(tool_name, "Atlas AI")
                    yield f"event: planning\ndata: {_j.dumps({'agent': agent_name, 'tool': tool_name})}\n\n"

                    # Execute tool
                    try:
                        args = _j.loads(tc["arguments"]) if tc["arguments"] else {}
                    except (ValueError, TypeError):
                        args = {}

                    result = await _execute_tool(tool_name, args)
                    tool_call_messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })

                # Collect all tool results for combined presentation
                for idx_p in sorted(tool_calls_in_progress.keys()):
                    tc_p = tool_calls_in_progress[idx_p]
                    if tc_p["name"] in PRESENTABLE_TOOLS:
                        r_content = next((m["content"] for m in tool_call_messages if m["tool_call_id"] == tc_p["id"]), None)
                        if r_content:
                            all_tool_results[tc_p["name"]] = r_content

                # Add assistant message with tool calls + tool results to messages
                assistant_msg = {"role": "assistant", "content": assistant_content or None, "tool_calls": [
                    {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                    for tc in [tool_calls_in_progress[i] for i in sorted(tool_calls_in_progress.keys())]
                ]}
                current_messages.append(assistant_msg)
                current_messages.extend(tool_call_messages)
                assistant_content = ""

            # Emit executive presentation built from ALL tool results + final response
            if all_tool_results:
                from .presentation import format_combined_presentation
                combined = format_combined_presentation(all_tool_results, assistant_content)
                if combined:
                    yield f"event: presentation\ndata: {_j.dumps(combined)}\n\n"

            # Emit done event with suggestions
            suggestions = _get_follow_up_suggestions(tools_called, language)
            yield f"event: done\ndata: {_j.dumps({'suggestions': suggestions})}\n\n"

        except Exception as e:
            logger.exception("Chat stream error")
            yield f"event: error\ndata: {_j.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


@app.delete("/api/chat/{session_id}")
async def clear_chat_session(session_id: str):
    _chat_sessions.pop(session_id, None)
    return {"cleared": True}


def _get_follow_up_suggestions(tools_called: list[str], language: str) -> list[dict]:
    """Generate contextual follow-up suggestions based on tools that were called."""
    suggestions = []
    if "morning_supply_brief" in tools_called or "kpi_dashboard" in tools_called:
        suggestions = [
            {"title": "Show critical alerts", "message": "Show me all critical supply alerts"},
            {"title": "Inventory risk", "message": "What SKUs are at risk of stockout?"},
            {"title": "Run scenario", "message": "What if titanium supply is disrupted for 2 months?"},
        ]
    elif "inventory_risk_agent" in tools_called:
        suggestions = [
            {"title": "Replenishment plan", "message": "Generate replenishment recommendations for critical items"},
            {"title": "Supplier details", "message": "Show me the suppliers for critical SKUs"},
            {"title": "Run scenario", "message": "What if demand spikes 30% next quarter?"},
        ]
    elif "demand_sensing_agent" in tools_called:
        suggestions = [
            {"title": "Inventory impact", "message": "How does this forecast affect inventory levels?"},
            {"title": "Production schedule", "message": "Show the current production schedule"},
            {"title": "Generate report", "message": "Generate a demand forecast report"},
        ]
    elif "scenario_analysis" in tools_called:
        suggestions = [
            {"title": "Mitigation plan", "message": "What mitigation actions should we take?"},
            {"title": "KPI impact", "message": "Show me the projected KPI impact"},
            {"title": "Another scenario", "message": "What if the disruption lasts 6 months instead?"},
        ]
    else:
        suggestions = [
            {"title": "Morning brief", "message": "Give me the morning supply brief"},
            {"title": "KPI overview", "message": "Show me the current KPI dashboard"},
            {"title": "Critical alerts", "message": "What are the critical supply alerts?"},
        ]
    return suggestions


@app.get("/api/health")
async def health():
    return {"status": "ok", "agent": "atlas", "data_source": settings.data_source_type}


from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    if req.username == settings.app_username and req.password == settings.app_password:
        return {"authenticated": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")


# ─── SKU & Inventory API ───────────────────────────────────────────────────

@app.get("/api/skus")
async def list_skus(category: str = "", plant: str = "", abc_class: str = ""):
    results = await data_service.get_skus(category=category, plant=plant, abc_class=abc_class)
    return [s.model_dump() for s in results]


@app.get("/api/skus/{sku_id}")
async def get_sku(sku_id: str):
    sku = await data_service.get_sku(sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku.model_dump()


@app.get("/api/inventory")
async def list_inventory(risk_level: str = "", warehouse: str = "", category: str = ""):
    results = await data_service.get_inventory(risk_level=risk_level, warehouse=warehouse, category=category)
    return [p.model_dump() for p in results]


@app.get("/api/inventory/risk-matrix")
async def inventory_risk_matrix():
    positions = await data_service.get_inventory()
    matrix = {"critical": 0, "warning": 0, "normal": 0, "excess": 0}
    for p in positions:
        matrix[p.risk_level.value] += 1
    return matrix


# ─── Demand API ────────────────────────────────────────────────────────────

@app.get("/api/demand/history")
async def demand_history(sku_id: str = "", channel: str = "", region: str = ""):
    results = await data_service.get_demand_history(sku_id=sku_id, channel=channel, region=region)
    return [r.model_dump() for r in results]


@app.get("/api/demand/forecast")
async def demand_forecast(sku_id: str = "", horizon_weeks: int = 8):
    results = await data_service.get_demand_forecast(sku_id=sku_id, horizon_weeks=horizon_weeks)
    return [f.model_dump() for f in results]


@app.get("/api/demand/accuracy")
async def demand_accuracy():
    kpis = await data_service.get_kpis()
    return {"mape": kpis.forecast_accuracy_mape, "target": 15.0, "status": "on_track" if kpis.forecast_accuracy_mape < 15 else "at_risk"}


# ─── Supply API ────────────────────────────────────────────────────────────

@app.get("/api/suppliers")
async def list_suppliers():
    results = await data_service.get_suppliers()
    return [s.model_dump() for s in results]


@app.get("/api/suppliers/{supplier_id}")
async def get_supplier(supplier_id: str):
    supplier = await data_service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier.model_dump()


@app.get("/api/purchase-orders")
async def list_purchase_orders(status: str = ""):
    results = await data_service.get_purchase_orders(status=status)
    return [po.model_dump() for po in results]


@app.get("/api/production/schedule")
async def production_schedule(plant: str = ""):
    results = await data_service.get_production_lines(plant=plant)
    return [line.model_dump() for line in results]


@app.get("/api/production/capacity")
async def production_capacity():
    lines = await data_service.get_production_lines()
    return {
        "lines": [{"id": l.id, "name": l.line_name, "plant": l.plant.value, "utilization": l.current_utilization_pct} for l in lines],
        "avg_utilization": sum(l.current_utilization_pct for l in lines) / len(lines),
    }


# ─── Replenishment API ────────────────────────────────────────────────────

@app.get("/api/replenishment/actions")
async def list_replenishment_actions():
    results = await data_service.get_replenishment_actions()
    return [a.model_dump() for a in results]


@app.post("/api/replenishment/actions/{action_id}/approve")
async def approve_action(action_id: str):
    await data_service.approve_action(action_id)
    return {"approved": True}


@app.post("/api/replenishment/actions/{action_id}/dismiss")
async def dismiss_action(action_id: str):
    await data_service.dismiss_action(action_id)
    return {"dismissed": True}


# ─── Scenarios API ─────────────────────────────────────────────────────────

_scenarios: list[dict] = []


@app.get("/api/scenarios")
async def list_scenarios():
    return _scenarios


@app.get("/api/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    found = next((s for s in _scenarios if s.get("id") == scenario_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return found


@app.post("/api/scenarios")
async def create_scenario(request: Request):
    from .scenario.supervisor import ScenarioSupervisor

    body = await request.json()
    scenario_type = body.get("scenario_type", "demand_spike")
    params = body.get("parameters", {})
    scenario_text = body.get("scenario_text", "")

    supervisor = ScenarioSupervisor(
        model=settings.azure_openai_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
    )
    result = await supervisor.run(data_service, scenario_type, params, scenario_text=scenario_text)

    result["id"] = uuid4().hex[:12]
    _scenarios.insert(0, result)
    return result


def save_scenario_result(result: dict):
    """Save a scenario result to history (called from agent tool)."""
    if "id" not in result:
        result["id"] = uuid4().hex[:12]
    _scenarios.insert(0, result)


# ─── Alerts API ────────────────────────────────────────────────────────────

@app.get("/api/alerts")
async def list_alerts(severity: str = "", alert_type: str = ""):
    results = await data_service.get_alerts(severity=severity, alert_type=alert_type)
    return [a.model_dump() for a in results]


@app.patch("/api/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    await data_service.mark_alert_read(alert_id)
    return {"read": True}


# ─── KPIs API ──────────────────────────────────────────────────────────────

@app.get("/api/labor")
async def get_labor(facility: str = "", days: int = 7):
    results = await data_service.get_daily_labor(facility=facility, days=days)
    return [r.model_dump() for r in results]


@app.get("/api/kpis")
async def get_kpis():
    kpis = await data_service.get_kpis()
    return kpis.model_dump()


@app.get("/api/kpis/history")
async def get_kpi_history():
    return await data_service.get_kpi_history()


# ─── Web Search API ───────────────────────────────────────────────────────

@app.get("/api/search/supplier/{supplier_id}")
async def search_supplier_news(supplier_id: str):
    from .web_search import web_search_context
    supplier = await data_service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    query = f"{supplier.name} aerospace supply chain news latest developments {supplier.country}"
    result = await web_search_context(query)
    return {"supplier_id": supplier_id, "supplier_name": supplier.name, "context": result}


@app.get("/api/search/commodity/{commodity}")
async def search_commodity(commodity: str):
    from .web_search import web_search_context
    query = f"{commodity} aerospace material price market North America latest 2026"
    result = await web_search_context(query)
    return {"commodity": commodity, "context": result}


# ─── Detail Endpoints (enriched data for drawers) ─────────────────────────

@app.get("/api/skus/{sku_id}/detail")
async def get_sku_detail_endpoint(sku_id: str):
    sku = await data_service.get_sku(sku_id)
    if not sku:
        skus = await data_service.get_skus()
        sku = next((s for s in skus if sku_id.lower() in s.name.lower()), None)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    sku_id = sku.id
    inventory = await data_service.get_inventory()
    inv_pos = next((p for p in inventory if p.sku_id == sku_id), None)
    forecasts = await data_service.get_demand_forecast(sku_id=sku_id)
    alternatives = await data_service.get_sku_alternatives(sku_id)
    quality = await data_service.get_quality_results(sku_id)
    alerts = await data_service.get_alerts()
    sku_alerts = [a for a in alerts if a.sku_id == sku_id]
    purchase_orders = await data_service.get_purchase_orders()
    sku_pos = [po for po in purchase_orders if po.sku_id == sku_id]
    lines = await data_service.get_production_lines()
    sku_lines = [l for l in lines if sku.category in l.product_categories]
    return {
        "sku": sku.model_dump(),
        "inventory": inv_pos.model_dump() if inv_pos else None,
        "forecasts": [f.model_dump() for f in forecasts[:8]],
        "alternatives": [a.model_dump() for a in alternatives],
        "quality_results": [q.model_dump() for q in quality],
        "alerts": [a.model_dump() for a in sku_alerts],
        "purchase_orders": [po.model_dump() for po in sku_pos],
        "production_lines": [l.model_dump() for l in sku_lines],
    }


@app.get("/api/suppliers/{supplier_id}/detail")
async def get_supplier_detail_endpoint(supplier_id: str):
    supplier = await data_service.get_supplier(supplier_id)
    if not supplier:
        suppliers = await data_service.get_suppliers()
        supplier = next((s for s in suppliers if supplier_id.lower() in s.name.lower()), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier_id = supplier.id
    contact = await data_service.get_supplier_contact(supplier_id)
    performance = await data_service.get_supplier_performance(supplier_id)
    certifications = await data_service.get_supplier_certifications(supplier_id)
    purchase_orders = await data_service.get_purchase_orders()
    supplier_pos = [po for po in purchase_orders if po.supplier_id == supplier_id]
    return {
        "supplier": supplier.model_dump(),
        "contact": contact.model_dump() if contact else None,
        "performance_history": [p.model_dump() for p in performance],
        "certifications": [c.model_dump() for c in certifications],
        "purchase_orders": [po.model_dump() for po in supplier_pos],
    }


@app.get("/api/plants/{plant_id}/detail")
async def get_plant_detail_endpoint(plant_id: str):
    lines = await data_service.get_production_lines()
    plant_lines = [l for l in lines if l.plant.value.lower().replace(" ", "_") == plant_id.lower() or l.id == plant_id]
    if not plant_lines:
        plant_lines = [l for l in lines if plant_id.lower() in l.plant.value.lower()]
    if not plant_lines:
        raise HTTPException(status_code=404, detail="Plant not found")
    line_details = []
    for line in plant_lines:
        maintenance = await data_service.get_maintenance_history(line.id)
        runs = await data_service.get_production_runs(line.id)
        line_details.append({
            "line": line.model_dump(),
            "maintenance_events": [m.model_dump() for m in maintenance],
            "production_runs": [r.model_dump() for r in runs[-5:]],
        })
    plant_name = plant_lines[0].plant.value
    avg_util = sum(l.current_utilization_pct for l in plant_lines) / len(plant_lines)
    total_capacity = sum(l.capacity_units_per_day for l in plant_lines)
    return {
        "plant_name": plant_name,
        "total_capacity_units_per_day": total_capacity,
        "avg_utilization_pct": round(avg_util, 1),
        "line_count": len(plant_lines),
        "lines": line_details,
    }


@app.get("/api/lines/{line_id}/detail")
async def get_line_detail_endpoint(line_id: str):
    lines = await data_service.get_production_lines()
    line = next((l for l in lines if l.id == line_id), None)
    if not line:
        raise HTTPException(status_code=404, detail="Production line not found")
    maintenance = await data_service.get_maintenance_history(line_id)
    runs = await data_service.get_production_runs(line_id)
    skus = await data_service.get_skus()
    line_skus = [s for s in skus if s.category in line.product_categories]
    return {
        "line": line.model_dump(),
        "maintenance_events": [m.model_dump() for m in maintenance],
        "production_runs": [r.model_dump() for r in runs],
        "skus_produced": [s.model_dump() for s in line_skus],
    }


# ─── Reports API ───────────────────────────────────────────────────────────

CONTENT_TYPES = {
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}


@app.get("/api/reports")
async def list_reports():
    records = reports_store.list_recent(20)
    return [
        {
            "id": r.id,
            "name": r.name,
            "template": r.template,
            "format": r.format,
            "date": r.date,
            "pages": r.pages,
            "file_size": r.file_size,
            "download_url": blob_service.get_download_url(r.blob_name) if r.blob_name else None,
            "generated_by": r.generated_by,
        }
        for r in records
    ]


@app.post("/api/reports/upload")
async def upload_report(
    file: UploadFile = File(...),
    name: str = Form(...),
    template: str = Form(...),
    format: str = Form(...),
    pages: int = Form(0),
):
    file_bytes = await file.read()
    blob_name = f"{format}/{template}_{date.today().isoformat()}_{uuid4().hex[:8]}.{format}"
    content_type = CONTENT_TYPES.get(format, "application/octet-stream")

    await blob_service.upload_report(file_bytes, blob_name, content_type)

    record = ReportRecord(
        id=uuid4().hex,
        name=name,
        template=template,
        format=format,
        audience="Internal",
        date=date.today().isoformat(),
        pages=pages,
        blob_name=blob_name,
        file_size=len(file_bytes),
    )
    reports_store.add(record)

    return {"id": record.id, "download_url": blob_service.get_download_url(blob_name)}


_latest_generated: dict[str, dict] = {}


def set_latest_generated(spec: dict, session_id: str | None = None):
    sid = session_id or current_session_id.get("default")
    _latest_generated[sid] = spec
    _latest_generated["__latest__"] = spec


@app.get("/api/reports/latest")
async def get_latest_generated(request: Request):
    session_id = request.headers.get("x-session-id") or current_session_id.get("default")
    result = _latest_generated.get(session_id)
    if result is None:
        result = _latest_generated.get("__latest__")
    return {"result": result}


@app.delete("/api/reports/latest")
async def clear_latest_generated(request: Request):
    session_id = request.headers.get("x-session-id") or current_session_id.get("default")
    _latest_generated.pop(session_id, None)
    _latest_generated.pop("__latest__", None)
    return {"cleared": True}


@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    record = reports_store.get(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")
    if record.blob_name:
        await blob_service.delete_report(record.blob_name)
    reports_store.delete(report_id)
    return {"deleted": True}


@app.get("/api/reports/files/{path:path}")
async def serve_local_file(path: str):
    file_path = LOCAL_STORAGE_DIR / path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    ext = file_path.suffix.lstrip(".")
    content_type = CONTENT_TYPES.get(ext, "application/octet-stream")
    return FileResponse(file_path, media_type=content_type, filename=file_path.name)
