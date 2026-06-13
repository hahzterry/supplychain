"""Pydantic models for Héroux-Devtek supply chain domain."""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class Category(str, Enum):
    LANDING_GEAR = "Landing Gear"
    ACTUATION = "Actuation Systems"
    HYDRAULICS = "Hydraulics"
    STRUCTURES = "Structures"
    MRO_PARTS = "MRO Parts"
    RAW_MATERIALS = "Raw Materials"
    FASTENERS_SEALS = "Fasteners & Seals"


class Channel(str, Enum):
    OEM_COMMERCIAL = "OEM Commercial"
    OEM_MILITARY = "OEM Military"
    AFTERMARKET_MRO = "Aftermarket MRO"
    SPARES = "Spares"
    INTERNAL_TRANSFER = "Internal Transfer"


class Region(str, Enum):
    NORTH_AMERICA = "North America"
    EUROPE = "Europe"
    ASIA_PACIFIC = "Asia Pacific"
    MIDDLE_EAST = "Middle East"
    SOUTH_AMERICA = "South America"


class Plant(str, Enum):
    LONGUEUIL_QC = "Longueuil, Quebec"
    KITCHENER_ON = "Kitchener, Ontario"
    SPRINGFIELD_OH = "Springfield, Ohio"
    NOTTINGHAM_UK = "Nottingham, UK"
    LAVAL_QC = "Laval, Quebec"
    LIVONIA_MI = "Livonia, Michigan"
    GETAFE_MADRID = "Getafe/Madrid, Spain (CESA)"
    SEVILLE_SPAIN = "Seville, Spain"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    NORMAL = "normal"
    EXCESS = "excess"


class SKU(BaseModel):
    id: str
    name: str
    name_fr: str
    name_es: str
    category: Category
    part_number: str
    drawing_rev: str
    material_spec: str
    program: str
    uom: str
    unit_cost: float
    inspection_interval_days: int
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
    cert_expiry_remaining_pct: float


class DemandRecord(BaseModel):
    sku_id: str
    week: str
    channel: Channel
    region: Region
    actual_qty: float
    forecast_qty: float
    program_change_flag: bool
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
    name_fr: str
    name_es: str
    country: str
    material_types: list[str]
    avg_lead_time_days: int
    min_lead_time_days: int
    max_lead_time_days: int
    reliability_score: float
    current_orders: int
    total_capacity_units: float
    quality_score: float
    last_delivery_date: str
    payment_terms: str
    certifications: list[str] = []


class ProductionLine(BaseModel):
    id: str
    plant: Plant
    line_name: str
    product_categories: list[Category]
    capacity_units_per_day: float
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
    unit_price: float = 0.0
    currency: str = "CAD"
    contract_id: str | None = None
    order_date: str
    expected_delivery: str
    status: str
    delay_days: int = 0
    validation_status: str = "pending"
    validation_flags: list[str] = []


class Contract(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    part_numbers: list[str]
    negotiated_prices: dict[str, float]
    escalation_pct_annual: float
    effective_date: str
    expiry_date: str
    currency: str = "CAD"
    status: str


class ContractPriceValidation(BaseModel):
    po_id: str
    contract_id: str | None
    part_number: str
    contract_ceiling: float | None
    po_unit_price: float
    variance_pct: float
    status: str


class POValidationResult(BaseModel):
    po_id: str
    status: str
    checks: list[dict]


class DailyLaborRecord(BaseModel):
    id: str
    facility: str
    date: str
    shift: str
    headcount: int
    direct_hours: float
    indirect_hours: float
    overtime_hours: float
    efficiency_pct: float
    skill_category: str
    production_line_id: str | None = None


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
    labor_utilization_pct: float
    contract_compliance_pct: float
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
    cost_cad: float


class QualityTestResult(BaseModel):
    sku_id: str
    batch_id: str
    test_date: str
    dimensional_check: str | None = None
    ndt_result: str | None = None
    material_cert_status: str
    overall_result: str
    inspector: str


class ProductionRun(BaseModel):
    line_id: str
    sku_id: str
    date: str
    planned_qty: float
    actual_qty: float
    yield_pct: float
    scrap_pct: float
    shift: str
