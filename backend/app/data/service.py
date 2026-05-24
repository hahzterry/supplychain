"""Abstract data service with mock implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .models import (
    SKU, InventoryPosition, DemandRecord, DemandForecast, Supplier,
    ProductionLine, PurchaseOrder, ReplenishmentAction, SupplyAlert,
    KPIMetrics, SupplierContact, SupplierPerformanceRecord,
    SupplierCertification, AlternativeSupplier, MaintenanceEvent,
    QualityTestResult, ProductionRun,
)
from .mock_store import (
    SKUS, SKU_MAP, INVENTORY_POSITIONS, DEMAND_HISTORY, DEMAND_FORECASTS,
    SUPPLIERS, SUPPLIER_MAP, PRODUCTION_LINES, PURCHASE_ORDERS,
    REPLENISHMENT_ACTIONS, SUPPLY_ALERTS, CURRENT_KPIS, KPI_HISTORY,
    SUPPLIER_CONTACTS, SUPPLIER_PERFORMANCE, SUPPLIER_CERTIFICATIONS,
    ALTERNATIVE_SUPPLIERS, MAINTENANCE_EVENTS, QUALITY_TEST_RESULTS,
    PRODUCTION_RUNS,
)


class DataService(ABC):
    @abstractmethod
    async def get_skus(self, category: str = "", plant: str = "", abc_class: str = "") -> list[SKU]: ...

    @abstractmethod
    async def get_sku(self, sku_id: str) -> SKU | None: ...

    @abstractmethod
    async def get_inventory(self, risk_level: str = "", warehouse: str = "", category: str = "") -> list[InventoryPosition]: ...

    @abstractmethod
    async def get_demand_history(self, sku_id: str = "", channel: str = "", region: str = "") -> list[DemandRecord]: ...

    @abstractmethod
    async def get_demand_forecast(self, sku_id: str = "", horizon_weeks: int = 8) -> list[DemandForecast]: ...

    @abstractmethod
    async def get_suppliers(self) -> list[Supplier]: ...

    @abstractmethod
    async def get_supplier(self, supplier_id: str) -> Supplier | None: ...

    @abstractmethod
    async def get_production_lines(self, plant: str = "") -> list[ProductionLine]: ...

    @abstractmethod
    async def get_purchase_orders(self, status: str = "") -> list[PurchaseOrder]: ...

    @abstractmethod
    async def get_replenishment_actions(self) -> list[ReplenishmentAction]: ...

    @abstractmethod
    async def approve_action(self, action_id: str) -> bool: ...

    @abstractmethod
    async def dismiss_action(self, action_id: str) -> bool: ...

    @abstractmethod
    async def get_alerts(self, severity: str = "", alert_type: str = "") -> list[SupplyAlert]: ...

    @abstractmethod
    async def mark_alert_read(self, alert_id: str) -> bool: ...

    @abstractmethod
    async def get_kpis(self) -> KPIMetrics: ...

    @abstractmethod
    async def get_kpi_history(self) -> list[dict]: ...

    @abstractmethod
    async def get_supplier_contact(self, supplier_id: str) -> SupplierContact | None: ...

    @abstractmethod
    async def get_supplier_performance(self, supplier_id: str) -> list[SupplierPerformanceRecord]: ...

    @abstractmethod
    async def get_supplier_certifications(self, supplier_id: str) -> list[SupplierCertification]: ...

    @abstractmethod
    async def get_sku_alternatives(self, sku_id: str) -> list[AlternativeSupplier]: ...

    @abstractmethod
    async def get_maintenance_history(self, line_id: str) -> list[MaintenanceEvent]: ...

    @abstractmethod
    async def get_quality_results(self, sku_id: str) -> list[QualityTestResult]: ...

    @abstractmethod
    async def get_production_runs(self, line_id: str) -> list[ProductionRun]: ...


class MockDataService(DataService):
    def __init__(self):
        self._actions = list(REPLENISHMENT_ACTIONS)
        self._alerts = list(SUPPLY_ALERTS)

    async def get_skus(self, category: str = "", plant: str = "", abc_class: str = "") -> list[SKU]:
        results = SKUS
        if category:
            results = [s for s in results if s.category.value.lower() == category.lower()]
        if plant:
            results = [s for s in results if plant.lower() in s.plant.value.lower()]
        if abc_class:
            results = [s for s in results if s.abc_class == abc_class.upper()]
        return results

    async def get_sku(self, sku_id: str) -> SKU | None:
        return SKU_MAP.get(sku_id)

    async def get_inventory(self, risk_level: str = "", warehouse: str = "", category: str = "") -> list[InventoryPosition]:
        results = INVENTORY_POSITIONS
        if risk_level:
            results = [p for p in results if p.risk_level.value == risk_level.lower()]
        if warehouse:
            results = [p for p in results if warehouse.lower() in p.warehouse.lower()]
        if category:
            results = [p for p in results if p.category.value.lower() == category.lower()]
        return results

    async def get_demand_history(self, sku_id: str = "", channel: str = "", region: str = "") -> list[DemandRecord]:
        results = DEMAND_HISTORY
        if sku_id:
            results = [r for r in results if r.sku_id == sku_id]
        if channel:
            results = [r for r in results if channel.lower() in r.channel.value.lower()]
        if region:
            results = [r for r in results if region.lower() in r.region.value.lower()]
        return results

    async def get_demand_forecast(self, sku_id: str = "", horizon_weeks: int = 8) -> list[DemandForecast]:
        results = DEMAND_FORECASTS
        if sku_id:
            results = [f for f in results if f.sku_id == sku_id]
        return results[:horizon_weeks * 20]

    async def get_suppliers(self) -> list[Supplier]:
        return SUPPLIERS

    async def get_supplier(self, supplier_id: str) -> Supplier | None:
        return SUPPLIER_MAP.get(supplier_id)

    async def get_production_lines(self, plant: str = "") -> list[ProductionLine]:
        if plant:
            return [l for l in PRODUCTION_LINES if plant.lower() in l.plant.value.lower()]
        return PRODUCTION_LINES

    async def get_purchase_orders(self, status: str = "") -> list[PurchaseOrder]:
        if status:
            return [po for po in PURCHASE_ORDERS if po.status == status.lower()]
        return PURCHASE_ORDERS

    async def get_replenishment_actions(self) -> list[ReplenishmentAction]:
        return self._actions

    async def approve_action(self, action_id: str) -> bool:
        self._actions = [a for a in self._actions if a.id != action_id]
        return True

    async def dismiss_action(self, action_id: str) -> bool:
        self._actions = [a for a in self._actions if a.id != action_id]
        return True

    async def get_alerts(self, severity: str = "", alert_type: str = "") -> list[SupplyAlert]:
        results = self._alerts
        if severity:
            results = [a for a in results if a.severity == severity.lower()]
        if alert_type:
            results = [a for a in results if a.alert_type == alert_type.lower()]
        return results

    async def mark_alert_read(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.read = True
                return True
        return False

    async def get_kpis(self) -> KPIMetrics:
        return CURRENT_KPIS

    async def get_kpi_history(self) -> list[dict]:
        return KPI_HISTORY

    async def get_supplier_contact(self, supplier_id: str) -> SupplierContact | None:
        return next((c for c in SUPPLIER_CONTACTS if c.supplier_id == supplier_id), None)

    async def get_supplier_performance(self, supplier_id: str) -> list[SupplierPerformanceRecord]:
        return [r for r in SUPPLIER_PERFORMANCE if r.supplier_id == supplier_id]

    async def get_supplier_certifications(self, supplier_id: str) -> list[SupplierCertification]:
        return [c for c in SUPPLIER_CERTIFICATIONS if c.supplier_id == supplier_id]

    async def get_sku_alternatives(self, sku_id: str) -> list[AlternativeSupplier]:
        return [a for a in ALTERNATIVE_SUPPLIERS if a.sku_id == sku_id]

    async def get_maintenance_history(self, line_id: str) -> list[MaintenanceEvent]:
        return [e for e in MAINTENANCE_EVENTS if e.line_id == line_id]

    async def get_quality_results(self, sku_id: str) -> list[QualityTestResult]:
        return [r for r in QUALITY_TEST_RESULTS if r.sku_id == sku_id]

    async def get_production_runs(self, line_id: str) -> list[ProductionRun]:
        return [r for r in PRODUCTION_RUNS if r.line_id == line_id]
