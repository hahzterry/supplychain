"""FastAPI application with AG-UI endpoint for RASHID multi-agent system."""
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

app = FastAPI(title="RASHID Supply Chain API")


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
    name="rashid_orchestrator",
    description="RASHID multi-agent system: orchestrator delegates to Demand Sensing, Inventory Risk, Supply Constraint, and Replenishment agents",
)


def _fix_dangling_tool_calls(messages: list[dict]) -> list[dict]:
    """Fix conversations where a previous tool call never returned a result."""
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


@app.get("/api/health")
async def health():
    return {"status": "ok", "agent": "rashid", "data_source": settings.data_source_type}


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

    supervisor = ScenarioSupervisor()
    result = await supervisor.run(data_service, scenario_type, params)

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
    query = f"{supplier.name} food supply chain news latest developments {supplier.country}"
    result = await web_search_context(query)
    return {"supplier_id": supplier_id, "supplier_name": supplier.name, "context": result}


@app.get("/api/search/commodity/{commodity}")
async def search_commodity(commodity: str):
    from .web_search import web_search_context
    query = f"{commodity} commodity price market UAE Middle East latest 2026"
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
    total_capacity = sum(l.capacity_mt_per_day for l in plant_lines)
    return {
        "plant_name": plant_name,
        "total_capacity_mt_per_day": total_capacity,
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
