"""Pydantic models for RASHID supply chain domain."""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class Category(str, Enum):
    FLOUR = "Flour"
    PASTA = "Pasta"
    COOKING_OIL = "Cooking Oil"
    ANIMAL_FEED = "Animal Feed"
    RICE = "Rice"
    SUGAR = "Sugar"
    SPECIALTY = "Specialty"


class Channel(str, Enum):
    MODERN_TRADE = "Modern Trade"
    TRADITIONAL_TRADE = "Traditional Trade"
    HORECA = "HoReCa"
    EXPORT = "Export"
    INDUSTRIAL = "Industrial"
    ONLINE = "Online"


class Region(str, Enum):
    DUBAI = "Dubai"
    ABU_DHABI = "Abu Dhabi"
    SHARJAH_NE = "Sharjah/Northern Emirates"
    AL_AIN = "Al Ain"
    KSA_EXPORT = "KSA Export"
    OMAN_EXPORT = "Oman Export"


class Plant(str, Enum):
    GRAND_MILLS_DUBAI = "Grand Mills Dubai"
    GRAND_MILLS_ABUDHABI = "Grand Mills Abu Dhabi"
    AGHURAIR_JEBELALI = "Al Ghurair Foods Jebel Ali"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    NORMAL = "normal"
    EXCESS = "excess"


class SKU(BaseModel):
    id: str
    name: str
    name_ar: str
    category: Category
    brand: str
    uom: str
    unit_cost: float
    shelf_life_days: int
    abc_class: str
    xyz_class: str
    min_order_qty: float
    lead_time_days: int
    safety_stock_days: int
    plant: Plant
    active: bool = True


class InventoryPosition(BaseModel):
    sku_id: str
    sku_name: str
    category: Category
    warehouse: str
    current_stock: float
    allocated_stock: float
    available_stock: float
    in_transit: float
    days_of_supply: float
    risk_level: RiskLevel
    last_receipt_date: str
    next_expected_receipt: str | None = None
    batch_age_days: int
    shelf_life_remaining_pct: float


class DemandRecord(BaseModel):
    sku_id: str
    week: str
    channel: Channel
    region: Region
    actual_qty: float
    forecast_qty: float
    promotion_flag: bool
    event_flag: str


class DemandForecast(BaseModel):
    sku_id: str
    sku_name: str
    week: str
    channel: Channel
    region: Region
    point_forecast: float
    lower_80: float
    upper_80: float
    lower_95: float
    upper_95: float
    confidence: str
    drivers: list[str]


class Supplier(BaseModel):
    id: str
    name: str
    name_ar: str
    country: str
    material_types: list[str]
    avg_lead_time_days: int
    min_lead_time_days: int
    max_lead_time_days: int
    reliability_score: float
    current_orders: int
    total_capacity_mt: float
    quality_score: float
    last_delivery_date: str
    payment_terms: str


class ProductionLine(BaseModel):
    id: str
    plant: Plant
    line_name: str
    product_categories: list[Category]
    capacity_mt_per_day: float
    current_utilization_pct: float
    planned_maintenance: list[str]
    current_sku: str | None = None
    shift_pattern: str


class PurchaseOrder(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    sku_id: str
    sku_name: str
    qty: float
    order_date: str
    expected_delivery: str
    status: str
    delay_days: int = 0


class ReplenishmentAction(BaseModel):
    id: str
    action_type: str
    sku_id: str
    sku_name: str
    recommended_qty: float
    supplier_id: str | None = None
    plant: Plant | None = None
    urgency: str
    rationale: str
    kpi_impact: dict
    confidence: str
    scenario: str


class SupplyAlert(BaseModel):
    id: str
    sku_id: str | None = None
    sku_name: str
    alert_type: str
    severity: str
    title: str
    description: str
    date: str
    plant: str
    recommended_action: str
    read: bool = False


class KPIMetrics(BaseModel):
    forecast_accuracy_mape: float
    inventory_dos: float
    fill_rate: float
    stockout_rate: float
    obsolescence_rate: float
    working_capital_mm: float
    production_utilization: float
    on_time_delivery: float
    alerts_open: int
    pending_actions: int


class ScenarioResult(BaseModel):
    id: str
    name: str
    scenario_type: str
    parameters: dict
    kpi_impact: dict
    affected_skus: list[str]
    recommended_actions: list[ReplenishmentAction]
    risk_assessment: str
    created_at: str


class SupplierContact(BaseModel):
    supplier_id: str
    name: str
    role: str
    email: str
    phone: str


class SupplierPerformanceRecord(BaseModel):
    supplier_id: str
    month: str
    on_time_delivery_pct: float
    quality_pass_rate: float
    avg_lead_time_days: int
    incidents: int


class SupplierCertification(BaseModel):
    supplier_id: str
    name: str
    status: str
    expiry_date: str
    issuing_body: str


class AlternativeSupplier(BaseModel):
    sku_id: str
    supplier_id: str
    supplier_name: str
    lead_time_days: int
    unit_cost_premium_pct: float
    min_order_qty: float
    notes: str


class MaintenanceEvent(BaseModel):
    line_id: str
    date: str
    duration_hours: float
    type: str
    root_cause: str
    cost_aed: float


class QualityTestResult(BaseModel):
    sku_id: str
    batch_id: str
    test_date: str
    moisture_pct: float | None = None
    protein_pct: float | None = None
    contaminant_level: str
    overall_result: str
    inspector: str


class ProductionRun(BaseModel):
    line_id: str
    sku_id: str
    date: str
    planned_qty: float
    actual_qty: float
    yield_pct: float
    waste_pct: float
    shift: str
