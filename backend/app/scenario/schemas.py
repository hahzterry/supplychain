"""Pydantic models for scenario analysis pipeline."""
from __future__ import annotations

from pydantic import BaseModel


class AffectedSku(BaseModel):
    sku_id: str
    sku_name: str
    category: str
    abc_class: str
    baseline_weekly_demand: float
    adjusted_weekly_demand: float
    demand_delta_pct: float
    weeks_until_stockout: float
    current_dos: float
    severity: str  # "critical" | "warning" | "safe"


class TimelineWeek(BaseModel):
    week: int
    label: str
    total_baseline_demand: float
    total_adjusted_demand: float
    total_stock: float
    net_position: float
    skus_below_safety: int
    skus_stockout: int


class DemandImpact(BaseModel):
    affected_skus: list[AffectedSku]
    weekly_timeline: list[TimelineWeek]
    summary_stats: dict


class SkuProjection(BaseModel):
    sku_id: str
    sku_name: str
    current_dos: float
    projected_dos: float
    stockout_week: int | None
    safety_stock_breached: bool
    projected_lost_sales_units: float
    projected_lost_sales_cad: float


class InventoryImpact(BaseModel):
    sku_projections: list[SkuProjection]
    timeline: list[dict]
    aggregate: dict


class SupplierAlternative(BaseModel):
    id: str
    name: str
    available_capacity_units: float
    lead_time_days: int
    reliability: float
    cost_premium_pct: float


class SupplyImpact(BaseModel):
    affected_suppliers: list[dict]
    alternative_suppliers: list[SupplierAlternative]
    in_transit_mitigations: list[dict]
    supply_gap: dict


class ProductionOption(BaseModel):
    option: str
    extra_mt_per_day: float
    duration_days: int
    impact: str


class ProductionImpact(BaseModel):
    affected_lines: list[dict]
    surge_capacity: dict
    production_options: list[ProductionOption]
    feasibility: str  # "full" | "partial" | "infeasible"


class MitigationOption(BaseModel):
    action: str
    cost_cad: float
    fill_rate_recovery: float
    lead_time_days: int
    priority: str


class KPIProjection(BaseModel):
    baseline: dict
    projected: dict
    deltas: dict
    confidence_bands: dict
    target_breaches: list[str]
    mitigation_options: list[MitigationOption]
    risk_summary: str
    recommended_actions: list[str]
