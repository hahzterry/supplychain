"""Synthetic data store for RASHID — 50+ SKUs, suppliers, demand history, inventory."""
from __future__ import annotations

import math
import random
from datetime import date, timedelta

from .models import (
    SKU, InventoryPosition, DemandRecord, DemandForecast, Supplier,
    ProductionLine, PurchaseOrder, ReplenishmentAction, SupplyAlert,
    KPIMetrics, Category, Channel, Region, Plant, RiskLevel,
    SupplierContact, SupplierPerformanceRecord, SupplierCertification,
    AlternativeSupplier, MaintenanceEvent, QualityTestResult, ProductionRun,
)

random.seed(42)

# ─── SKU Master (50 items) ─────────────────────────────────────────────────

SKUS: list[SKU] = [
    # Flour (10)
    SKU(id="FL001", name="Jenan All-Purpose Flour 1kg", name_ar="جنان دقيق متعدد الاستخدامات 1كغ", category=Category.FLOUR, brand="Jenan", uom="Cartons", unit_cost=1.2, shelf_life_days=365, abc_class="A", xyz_class="X", min_order_qty=500, lead_time_days=21, safety_stock_days=14, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="FL002", name="Grand Mills Chakki Atta 10kg", name_ar="جراند ميلز شكي عطا 10كغ", category=Category.FLOUR, brand="Grand Mills", uom="Bags", unit_cost=8.5, shelf_life_days=270, abc_class="A", xyz_class="X", min_order_qty=200, lead_time_days=21, safety_stock_days=14, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="FL003", name="Bread Flour 50kg", name_ar="دقيق خبز 50كغ", category=Category.FLOUR, brand="Grand Mills", uom="Bags 50kg", unit_cost=45.0, shelf_life_days=180, abc_class="A", xyz_class="X", min_order_qty=100, lead_time_days=21, safety_stock_days=10, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="FL004", name="Pastry Flour 25kg", name_ar="دقيق معجنات 25كغ", category=Category.FLOUR, brand="Grand Mills", uom="Bags 25kg", unit_cost=28.0, shelf_life_days=180, abc_class="B", xyz_class="Y", min_order_qty=80, lead_time_days=21, safety_stock_days=12, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="FL005", name="Jenan Whole Wheat Flour 2kg", name_ar="جنان دقيق قمح كامل 2كغ", category=Category.FLOUR, brand="Jenan", uom="Cartons", unit_cost=3.5, shelf_life_days=240, abc_class="B", xyz_class="Y", min_order_qty=300, lead_time_days=21, safety_stock_days=14, plant=Plant.GRAND_MILLS_ABUDHABI),
    SKU(id="FL006", name="Maida Fine Flour 50kg", name_ar="دقيق ميدا ناعم 50كغ", category=Category.FLOUR, brand="Grand Mills", uom="Bags 50kg", unit_cost=42.0, shelf_life_days=180, abc_class="A", xyz_class="X", min_order_qty=100, lead_time_days=21, safety_stock_days=10, plant=Plant.GRAND_MILLS_ABUDHABI),
    SKU(id="FL007", name="Self-Rising Flour 2kg", name_ar="دقيق ذاتي الارتفاع 2كغ", category=Category.FLOUR, brand="Jenan", uom="Cartons", unit_cost=3.8, shelf_life_days=180, abc_class="C", xyz_class="Z", min_order_qty=200, lead_time_days=21, safety_stock_days=14, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="FL008", name="Semolina Fine 25kg", name_ar="سميد ناعم 25كغ", category=Category.FLOUR, brand="Grand Mills", uom="Bags 25kg", unit_cost=32.0, shelf_life_days=270, abc_class="A", xyz_class="X", min_order_qty=100, lead_time_days=25, safety_stock_days=14, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="FL009", name="Industrial Flour 50kg", name_ar="دقيق صناعي 50كغ", category=Category.FLOUR, brand="Grand Mills", uom="Bags 50kg", unit_cost=38.0, shelf_life_days=180, abc_class="A", xyz_class="X", min_order_qty=200, lead_time_days=21, safety_stock_days=10, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="FL010", name="Organic Wheat Flour 1kg", name_ar="دقيق قمح عضوي 1كغ", category=Category.FLOUR, brand="Jenan", uom="Cartons", unit_cost=5.2, shelf_life_days=180, abc_class="C", xyz_class="Z", min_order_qty=100, lead_time_days=28, safety_stock_days=14, plant=Plant.GRAND_MILLS_DUBAI),
    # Pasta (8)
    SKU(id="PA001", name="Jenan Spaghetti 500g", name_ar="جنان سباغيتي 500غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=1.8, shelf_life_days=730, abc_class="A", xyz_class="X", min_order_qty=400, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="PA002", name="Jenan Penne 500g", name_ar="جنان بيني 500غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=1.8, shelf_life_days=730, abc_class="A", xyz_class="X", min_order_qty=300, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="PA003", name="Jenan Macaroni 400g", name_ar="جنان معكرونة 400غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=1.5, shelf_life_days=730, abc_class="A", xyz_class="X", min_order_qty=400, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="PA004", name="Lasagne Sheets 500g", name_ar="رقائق لازانيا 500غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=3.2, shelf_life_days=730, abc_class="B", xyz_class="Y", min_order_qty=150, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="PA005", name="Fusilli 500g", name_ar="فوسيلي 500غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=1.9, shelf_life_days=730, abc_class="B", xyz_class="Y", min_order_qty=250, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="PA006", name="Vermicelli 400g", name_ar="شعيرية 400غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=1.4, shelf_life_days=730, abc_class="B", xyz_class="X", min_order_qty=300, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="PA007", name="Angel Hair 500g", name_ar="شعر الملاك 500غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=2.0, shelf_life_days=730, abc_class="C", xyz_class="Y", min_order_qty=150, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="PA008", name="Couscous 500g", name_ar="كسكس 500غ", category=Category.PASTA, brand="Jenan", uom="Cartons", unit_cost=2.5, shelf_life_days=545, abc_class="B", xyz_class="Y", min_order_qty=200, lead_time_days=25, safety_stock_days=18, plant=Plant.AGHURAIR_JEBELALI),
    # Cooking Oil (6)
    SKU(id="OL001", name="Jenan Sunflower Oil 1.5L", name_ar="جنان زيت دوار الشمس 1.5ل", category=Category.COOKING_OIL, brand="Jenan", uom="Cartons", unit_cost=4.5, shelf_life_days=545, abc_class="A", xyz_class="X", min_order_qty=300, lead_time_days=35, safety_stock_days=21, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="OL002", name="Jenan Corn Oil 1.8L", name_ar="جنان زيت ذرة 1.8ل", category=Category.COOKING_OIL, brand="Jenan", uom="Cartons", unit_cost=5.8, shelf_life_days=545, abc_class="A", xyz_class="X", min_order_qty=250, lead_time_days=35, safety_stock_days=21, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="OL003", name="Jenan Vegetable Oil 5L", name_ar="جنان زيت نباتي 5ل", category=Category.COOKING_OIL, brand="Jenan", uom="Cartons", unit_cost=12.0, shelf_life_days=545, abc_class="A", xyz_class="X", min_order_qty=150, lead_time_days=35, safety_stock_days=21, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="OL004", name="Olive Oil Blend 500ml", name_ar="مزيج زيت زيتون 500مل", category=Category.COOKING_OIL, brand="Jenan", uom="Cartons", unit_cost=8.5, shelf_life_days=365, abc_class="B", xyz_class="Y", min_order_qty=100, lead_time_days=35, safety_stock_days=21, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="OL005", name="Coconut Oil 1L", name_ar="زيت جوز الهند 1ل", category=Category.COOKING_OIL, brand="Jenan", uom="Cartons", unit_cost=9.0, shelf_life_days=365, abc_class="C", xyz_class="Z", min_order_qty=80, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="OL006", name="Industrial Frying Oil 20L", name_ar="زيت قلي صناعي 20ل", category=Category.COOKING_OIL, brand="Grand Mills", uom="Drums", unit_cost=35.0, shelf_life_days=365, abc_class="A", xyz_class="X", min_order_qty=50, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    # Animal Feed (5)
    SKU(id="AF001", name="Poultry Layer Feed 50kg", name_ar="علف دواجن بياض 50كغ", category=Category.ANIMAL_FEED, brand="Grand Mills", uom="Bags 50kg", unit_cost=22.0, shelf_life_days=90, abc_class="A", xyz_class="X", min_order_qty=200, lead_time_days=14, safety_stock_days=7, plant=Plant.GRAND_MILLS_ABUDHABI),
    SKU(id="AF002", name="Broiler Starter 25kg", name_ar="علف تسمين بادئ 25كغ", category=Category.ANIMAL_FEED, brand="Grand Mills", uom="Bags 25kg", unit_cost=18.0, shelf_life_days=90, abc_class="A", xyz_class="X", min_order_qty=150, lead_time_days=14, safety_stock_days=7, plant=Plant.GRAND_MILLS_ABUDHABI),
    SKU(id="AF003", name="Dairy Cattle Feed 50kg", name_ar="علف أبقار حلوب 50كغ", category=Category.ANIMAL_FEED, brand="Grand Mills", uom="Bags 50kg", unit_cost=25.0, shelf_life_days=90, abc_class="B", xyz_class="Y", min_order_qty=100, lead_time_days=14, safety_stock_days=7, plant=Plant.GRAND_MILLS_ABUDHABI),
    SKU(id="AF004", name="Fish Feed Premium 25kg", name_ar="علف أسماك ممتاز 25كغ", category=Category.ANIMAL_FEED, brand="Grand Mills", uom="Bags 25kg", unit_cost=35.0, shelf_life_days=120, abc_class="B", xyz_class="Y", min_order_qty=80, lead_time_days=21, safety_stock_days=10, plant=Plant.GRAND_MILLS_ABUDHABI),
    SKU(id="AF005", name="Camel Feed 50kg", name_ar="علف إبل 50كغ", category=Category.ANIMAL_FEED, brand="Grand Mills", uom="Bags 50kg", unit_cost=20.0, shelf_life_days=90, abc_class="C", xyz_class="Z", min_order_qty=80, lead_time_days=14, safety_stock_days=7, plant=Plant.GRAND_MILLS_ABUDHABI),
    # Rice (5)
    SKU(id="RI001", name="Jenan Basmati Rice 5kg", name_ar="جنان أرز بسمتي 5كغ", category=Category.RICE, brand="Jenan", uom="Bags", unit_cost=15.0, shelf_life_days=730, abc_class="A", xyz_class="X", min_order_qty=200, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="RI002", name="Jenan Sella Rice 10kg", name_ar="جنان أرز سيلا 10كغ", category=Category.RICE, brand="Jenan", uom="Bags", unit_cost=22.0, shelf_life_days=730, abc_class="A", xyz_class="X", min_order_qty=150, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="RI003", name="Egyptian Rice 5kg", name_ar="أرز مصري 5كغ", category=Category.RICE, brand="Jenan", uom="Bags", unit_cost=12.0, shelf_life_days=730, abc_class="B", xyz_class="Y", min_order_qty=150, lead_time_days=22, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="RI004", name="Short Grain Rice 2kg", name_ar="أرز قصير الحبة 2كغ", category=Category.RICE, brand="Jenan", uom="Cartons", unit_cost=6.0, shelf_life_days=730, abc_class="C", xyz_class="Y", min_order_qty=100, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="RI005", name="Biryani Special Rice 5kg", name_ar="أرز برياني خاص 5كغ", category=Category.RICE, brand="Jenan", uom="Bags", unit_cost=18.0, shelf_life_days=730, abc_class="B", xyz_class="Y", min_order_qty=120, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    # Sugar (4)
    SKU(id="SU001", name="White Granulated Sugar 50kg", name_ar="سكر أبيض حبيبي 50كغ", category=Category.SUGAR, brand="Grand Mills", uom="Bags 50kg", unit_cost=35.0, shelf_life_days=730, abc_class="A", xyz_class="X", min_order_qty=200, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SU002", name="Icing Sugar 1kg", name_ar="سكر بودرة 1كغ", category=Category.SUGAR, brand="Jenan", uom="Cartons", unit_cost=3.0, shelf_life_days=545, abc_class="B", xyz_class="Y", min_order_qty=200, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SU003", name="Brown Sugar 2kg", name_ar="سكر بني 2كغ", category=Category.SUGAR, brand="Jenan", uom="Cartons", unit_cost=5.5, shelf_life_days=545, abc_class="C", xyz_class="Z", min_order_qty=100, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SU004", name="Industrial Sugar 50kg", name_ar="سكر صناعي 50كغ", category=Category.SUGAR, brand="Grand Mills", uom="Bags 50kg", unit_cost=32.0, shelf_life_days=730, abc_class="A", xyz_class="X", min_order_qty=150, lead_time_days=18, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    # Specialty (12)
    SKU(id="SP001", name="Baking Powder 500g", name_ar="بيكنج باودر 500غ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=2.5, shelf_life_days=365, abc_class="B", xyz_class="Y", min_order_qty=200, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SP002", name="Instant Yeast 500g", name_ar="خميرة فورية 500غ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=4.0, shelf_life_days=365, abc_class="B", xyz_class="Y", min_order_qty=150, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SP003", name="Cornstarch 500g", name_ar="نشا ذرة 500غ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=2.0, shelf_life_days=545, abc_class="B", xyz_class="X", min_order_qty=200, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SP004", name="Breadcrumbs 1kg", name_ar="فتات الخبز 1كغ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=3.5, shelf_life_days=180, abc_class="C", xyz_class="Y", min_order_qty=100, lead_time_days=7, safety_stock_days=10, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SP005", name="Tortilla Mix 25kg", name_ar="خليط تورتيلا 25كغ", category=Category.SPECIALTY, brand="Grand Mills", uom="Bags 25kg", unit_cost=28.0, shelf_life_days=180, abc_class="B", xyz_class="Y", min_order_qty=50, lead_time_days=14, safety_stock_days=10, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="SP006", name="Pizza Base Mix 25kg", name_ar="خليط قاعدة بيتزا 25كغ", category=Category.SPECIALTY, brand="Grand Mills", uom="Bags 25kg", unit_cost=30.0, shelf_life_days=180, abc_class="B", xyz_class="Y", min_order_qty=50, lead_time_days=14, safety_stock_days=10, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="SP007", name="Pancake Mix 1kg", name_ar="خليط بانكيك 1كغ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=4.5, shelf_life_days=270, abc_class="C", xyz_class="Z", min_order_qty=100, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SP008", name="Falafel Mix 500g", name_ar="خليط فلافل 500غ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=3.0, shelf_life_days=365, abc_class="B", xyz_class="Y", min_order_qty=150, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SP009", name="Shawarma Seasoning 1kg", name_ar="بهارات شاورما 1كغ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=8.0, shelf_life_days=365, abc_class="C", xyz_class="Z", min_order_qty=80, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
    SKU(id="SP010", name="Arabic Bread Premix 50kg", name_ar="خليط خبز عربي جاهز 50كغ", category=Category.SPECIALTY, brand="Grand Mills", uom="Bags 50kg", unit_cost=40.0, shelf_life_days=180, abc_class="A", xyz_class="X", min_order_qty=80, lead_time_days=14, safety_stock_days=10, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="SP011", name="Croissant Premix 25kg", name_ar="خليط كرواسون 25كغ", category=Category.SPECIALTY, brand="Grand Mills", uom="Bags 25kg", unit_cost=45.0, shelf_life_days=180, abc_class="B", xyz_class="Y", min_order_qty=40, lead_time_days=14, safety_stock_days=10, plant=Plant.GRAND_MILLS_DUBAI),
    SKU(id="SP012", name="Maamoul Mix 2kg", name_ar="خليط معمول 2كغ", category=Category.SPECIALTY, brand="Jenan", uom="Cartons", unit_cost=7.0, shelf_life_days=270, abc_class="B", xyz_class="Z", min_order_qty=100, lead_time_days=14, safety_stock_days=14, plant=Plant.AGHURAIR_JEBELALI),
]

SKU_MAP: dict[str, SKU] = {s.id: s for s in SKUS}

# ─── Suppliers (10) ────────────────────────────────────────────────────────

SUPPLIERS: list[Supplier] = [
    Supplier(id="S01", name="Black Sea Grain Corp", name_ar="شركة حبوب البحر الأسود", country="Ukraine", material_types=["Wheat", "Barley"], avg_lead_time_days=28, min_lead_time_days=22, max_lead_time_days=40, reliability_score=72.0, current_orders=3, total_capacity_mt=50000, quality_score=78.0, last_delivery_date="2026-04-28", payment_terms="LC 60 days"),
    Supplier(id="S02", name="Cargill Middle East", name_ar="كارجيل الشرق الأوسط", country="USA", material_types=["Wheat", "Corn", "Soybean"], avg_lead_time_days=21, min_lead_time_days=18, max_lead_time_days=28, reliability_score=95.0, current_orders=5, total_capacity_mt=120000, quality_score=94.0, last_delivery_date="2026-05-10", payment_terms="LC 45 days"),
    Supplier(id="S03", name="Bunge MENA", name_ar="بونج الشرق الأوسط", country="Brazil", material_types=["Soybean Oil", "Corn Oil", "Sunflower Oil"], avg_lead_time_days=35, min_lead_time_days=28, max_lead_time_days=45, reliability_score=88.0, current_orders=2, total_capacity_mt=80000, quality_score=90.0, last_delivery_date="2026-04-15", payment_terms="LC 90 days"),
    Supplier(id="S04", name="Olam Agri", name_ar="أولام أجري", country="Singapore", material_types=["Rice", "Sugar", "Cocoa"], avg_lead_time_days=18, min_lead_time_days=14, max_lead_time_days=25, reliability_score=91.0, current_orders=4, total_capacity_mt=95000, quality_score=88.0, last_delivery_date="2026-05-05", payment_terms="LC 60 days"),
    Supplier(id="S05", name="Louis Dreyfus MENA", name_ar="لويس دريفوس الشرق الأوسط", country="France", material_types=["Wheat", "Sunflower Oil", "Barley"], avg_lead_time_days=25, min_lead_time_days=20, max_lead_time_days=35, reliability_score=85.0, current_orders=3, total_capacity_mt=70000, quality_score=87.0, last_delivery_date="2026-04-22", payment_terms="LC 60 days"),
    Supplier(id="S06", name="Viterra Gulf", name_ar="فيتيرا الخليج", country="Canada", material_types=["Durum Wheat", "Barley", "Canola"], avg_lead_time_days=30, min_lead_time_days=25, max_lead_time_days=38, reliability_score=90.0, current_orders=2, total_capacity_mt=60000, quality_score=92.0, last_delivery_date="2026-05-01", payment_terms="LC 45 days"),
    Supplier(id="S07", name="Wilmar International", name_ar="ويلمار الدولية", country="Malaysia", material_types=["Palm Oil", "Coconut Oil", "Lauric Oils"], avg_lead_time_days=14, min_lead_time_days=10, max_lead_time_days=20, reliability_score=93.0, current_orders=3, total_capacity_mt=150000, quality_score=89.0, last_delivery_date="2026-05-12", payment_terms="TT 30 days"),
    Supplier(id="S08", name="COFCO International", name_ar="كوفكو الدولية", country="China", material_types=["Rice", "Corn", "Sugar"], avg_lead_time_days=22, min_lead_time_days=18, max_lead_time_days=30, reliability_score=82.0, current_orders=2, total_capacity_mt=100000, quality_score=80.0, last_delivery_date="2026-04-18", payment_terms="LC 90 days"),
    Supplier(id="S09", name="GrainCorp MENA", name_ar="جرين كورب الشرق الأوسط", country="Australia", material_types=["Premium Wheat", "Sorghum"], avg_lead_time_days=32, min_lead_time_days=28, max_lead_time_days=40, reliability_score=87.0, current_orders=2, total_capacity_mt=45000, quality_score=95.0, last_delivery_date="2026-04-25", payment_terms="LC 60 days"),
    Supplier(id="S10", name="Local UAE Packaging", name_ar="تغليف الإمارات المحلية", country="UAE", material_types=["Bags", "Cartons", "Films", "Labels"], avg_lead_time_days=5, min_lead_time_days=3, max_lead_time_days=8, reliability_score=96.0, current_orders=8, total_capacity_mt=0, quality_score=91.0, last_delivery_date="2026-05-16", payment_terms="Net 30"),
]

SUPPLIER_MAP: dict[str, Supplier] = {s.id: s for s in SUPPLIERS}

# ─── Production Lines (8) ──────────────────────────────────────────────────

PRODUCTION_LINES: list[ProductionLine] = [
    ProductionLine(id="PL01", plant=Plant.GRAND_MILLS_DUBAI, line_name="Flour Mill Line A", product_categories=[Category.FLOUR], capacity_mt_per_day=450, current_utilization_pct=82, planned_maintenance=["2026-06-01", "2026-06-02"], current_sku="FL003", shift_pattern="3x8"),
    ProductionLine(id="PL02", plant=Plant.GRAND_MILLS_DUBAI, line_name="Flour Mill Line B", product_categories=[Category.FLOUR, Category.SPECIALTY], capacity_mt_per_day=320, current_utilization_pct=75, planned_maintenance=["2026-05-25"], current_sku="FL001", shift_pattern="3x8"),
    ProductionLine(id="PL03", plant=Plant.GRAND_MILLS_DUBAI, line_name="Specialty Premix Line", product_categories=[Category.SPECIALTY], capacity_mt_per_day=80, current_utilization_pct=68, planned_maintenance=[], current_sku="SP010", shift_pattern="2x12"),
    ProductionLine(id="PL04", plant=Plant.GRAND_MILLS_ABUDHABI, line_name="Flour Mill Line C", product_categories=[Category.FLOUR], capacity_mt_per_day=380, current_utilization_pct=88, planned_maintenance=["2026-05-28", "2026-05-29"], current_sku="FL006", shift_pattern="3x8"),
    ProductionLine(id="PL05", plant=Plant.GRAND_MILLS_ABUDHABI, line_name="Feed Mill Line", product_categories=[Category.ANIMAL_FEED], capacity_mt_per_day=200, current_utilization_pct=91, planned_maintenance=[], current_sku="AF001", shift_pattern="3x8"),
    ProductionLine(id="PL06", plant=Plant.AGHURAIR_JEBELALI, line_name="Pasta Line 1", product_categories=[Category.PASTA], capacity_mt_per_day=120, current_utilization_pct=79, planned_maintenance=["2026-06-05"], current_sku="PA001", shift_pattern="2x12"),
    ProductionLine(id="PL07", plant=Plant.AGHURAIR_JEBELALI, line_name="Oil Refinery Line", product_categories=[Category.COOKING_OIL], capacity_mt_per_day=250, current_utilization_pct=85, planned_maintenance=[], current_sku="OL001", shift_pattern="3x8"),
    ProductionLine(id="PL08", plant=Plant.AGHURAIR_JEBELALI, line_name="Packing & Rice Line", product_categories=[Category.RICE, Category.SUGAR], capacity_mt_per_day=180, current_utilization_pct=72, planned_maintenance=["2026-06-10"], current_sku="RI001", shift_pattern="2x12"),
]


# ─── Generate Inventory Positions ──────────────────────────────────────────

def _generate_inventory() -> list[InventoryPosition]:
    positions = []
    today = date(2026, 5, 18)
    for sku in SKUS:
        avg_daily = random.uniform(5, 80) if sku.abc_class == "A" else random.uniform(2, 30)
        dos = random.uniform(3, 45)
        current = dos * avg_daily
        allocated = current * random.uniform(0.1, 0.3)
        in_transit = avg_daily * random.uniform(5, 15)
        batch_age = random.randint(5, min(sku.shelf_life_days - 30, 120))
        shelf_remaining = max(0, (sku.shelf_life_days - batch_age) / sku.shelf_life_days * 100)

        if dos < 7:
            risk = RiskLevel.CRITICAL
        elif dos < 14:
            risk = RiskLevel.WARNING
        elif dos > 35:
            risk = RiskLevel.EXCESS
        else:
            risk = RiskLevel.NORMAL

        receipt_date = today - timedelta(days=random.randint(3, 20))
        next_receipt = today + timedelta(days=random.randint(3, 25)) if random.random() > 0.3 else None

        positions.append(InventoryPosition(
            sku_id=sku.id,
            sku_name=sku.name,
            category=sku.category,
            warehouse=sku.plant.value,
            current_stock=round(current, 1),
            allocated_stock=round(allocated, 1),
            available_stock=round(current - allocated, 1),
            in_transit=round(in_transit, 1),
            days_of_supply=round(dos, 1),
            risk_level=risk,
            last_receipt_date=receipt_date.isoformat(),
            next_expected_receipt=next_receipt.isoformat() if next_receipt else None,
            batch_age_days=batch_age,
            shelf_life_remaining_pct=round(shelf_remaining, 1),
        ))
    return positions


INVENTORY_POSITIONS: list[InventoryPosition] = _generate_inventory()


# ─── Generate Demand History (simplified — last 12 weeks) ──────────────────

SEASONALITY_MULTIPLIERS = {
    "ramadan": {Category.FLOUR: 1.45, Category.COOKING_OIL: 1.35, Category.RICE: 1.40, Category.SUGAR: 1.50, Category.SPECIALTY: 1.60, Category.PASTA: 1.10, Category.ANIMAL_FEED: 1.0},
    "summer": {Category.FLOUR: 0.85, Category.PASTA: 0.80, Category.COOKING_OIL: 0.90, Category.ANIMAL_FEED: 1.05, Category.RICE: 0.90, Category.SUGAR: 0.85, Category.SPECIALTY: 0.85},
    "normal": {c: 1.0 for c in Category},
}


def _generate_demand_history() -> list[DemandRecord]:
    records = []
    base_date = date(2026, 3, 2)
    channels = list(Channel)
    regions = list(Region)

    for sku in SKUS[:20]:  # Generate for top 20 SKUs to keep manageable
        base_demand = random.uniform(50, 500) if sku.abc_class == "A" else random.uniform(10, 100)
        for week_offset in range(12):
            week_date = base_date + timedelta(weeks=week_offset)
            week_str = f"{week_date.isocalendar()[0]}-W{week_date.isocalendar()[1]:02d}"
            season = "ramadan" if 10 <= week_date.isocalendar()[1] <= 13 else "normal"
            multiplier = SEASONALITY_MULTIPLIERS[season].get(sku.category, 1.0)

            channel = random.choice(channels)
            region = random.choice(regions)
            promo = random.random() < 0.15
            promo_lift = 1.25 if promo else 1.0
            noise = random.uniform(0.85, 1.15)

            actual = base_demand * multiplier * promo_lift * noise
            forecast = actual * random.uniform(0.88, 1.12)

            records.append(DemandRecord(
                sku_id=sku.id,
                week=week_str,
                channel=channel,
                region=region,
                actual_qty=round(actual, 1),
                forecast_qty=round(forecast, 1),
                promotion_flag=promo,
                event_flag="ramadan" if season == "ramadan" else "",
            ))
    return records


DEMAND_HISTORY: list[DemandRecord] = _generate_demand_history()


# ─── Generate Demand Forecasts (next 8 weeks) ─────────────────────────────

def _generate_forecasts() -> list[DemandForecast]:
    forecasts = []
    base_date = date(2026, 5, 19)

    for sku in SKUS[:20]:
        base_demand = random.uniform(50, 500) if sku.abc_class == "A" else random.uniform(10, 100)
        for week_offset in range(8):
            week_date = base_date + timedelta(weeks=week_offset)
            week_str = f"{week_date.isocalendar()[0]}-W{week_date.isocalendar()[1]:02d}"

            point = base_demand * random.uniform(0.9, 1.1)
            uncertainty = 0.1 + week_offset * 0.02
            lower_80 = point * (1 - uncertainty * 0.8)
            upper_80 = point * (1 + uncertainty * 0.8)
            lower_95 = point * (1 - uncertainty * 1.2)
            upper_95 = point * (1 + uncertainty * 1.2)

            confidence = "high" if week_offset < 3 else ("medium" if week_offset < 6 else "low")
            drivers = ["trend"]
            if random.random() < 0.3:
                drivers.append("seasonality")
            if random.random() < 0.15:
                drivers.append("promotion")

            forecasts.append(DemandForecast(
                sku_id=sku.id,
                sku_name=sku.name,
                week=week_str,
                channel=random.choice(list(Channel)),
                region=random.choice(list(Region)),
                point_forecast=round(point, 1),
                lower_80=round(lower_80, 1),
                upper_80=round(upper_80, 1),
                lower_95=round(lower_95, 1),
                upper_95=round(upper_95, 1),
                confidence=confidence,
                drivers=drivers,
            ))
    return forecasts


DEMAND_FORECASTS: list[DemandForecast] = _generate_forecasts()


# ─── Purchase Orders (15 active) ──────────────────────────────────────────

PURCHASE_ORDERS: list[PurchaseOrder] = [
    PurchaseOrder(id="PO-2026-001", supplier_id="S02", supplier_name="Cargill Middle East", sku_id="FL003", sku_name="Bread Flour 50kg", qty=2000, order_date="2026-04-20", expected_delivery="2026-05-20", status="in_transit", delay_days=0),
    PurchaseOrder(id="PO-2026-002", supplier_id="S06", supplier_name="Viterra Gulf", sku_id="FL008", sku_name="Semolina Fine 25kg", qty=1500, order_date="2026-04-15", expected_delivery="2026-05-22", status="in_transit", delay_days=3),
    PurchaseOrder(id="PO-2026-003", supplier_id="S03", supplier_name="Bunge MENA", sku_id="OL001", sku_name="Jenan Sunflower Oil 1.5L", qty=800, order_date="2026-04-10", expected_delivery="2026-05-25", status="open", delay_days=0),
    PurchaseOrder(id="PO-2026-004", supplier_id="S07", supplier_name="Wilmar International", sku_id="OL005", sku_name="Coconut Oil 1L", qty=300, order_date="2026-05-01", expected_delivery="2026-05-18", status="received", delay_days=0),
    PurchaseOrder(id="PO-2026-005", supplier_id="S04", supplier_name="Olam Agri", sku_id="RI001", sku_name="Jenan Basmati Rice 5kg", qty=1200, order_date="2026-04-28", expected_delivery="2026-05-20", status="in_transit", delay_days=0),
    PurchaseOrder(id="PO-2026-006", supplier_id="S01", supplier_name="Black Sea Grain Corp", sku_id="FL009", sku_name="Industrial Flour 50kg", qty=3000, order_date="2026-04-18", expected_delivery="2026-05-23", status="delayed", delay_days=7),
    PurchaseOrder(id="PO-2026-007", supplier_id="S04", supplier_name="Olam Agri", sku_id="SU001", sku_name="White Granulated Sugar 50kg", qty=2500, order_date="2026-05-02", expected_delivery="2026-05-24", status="open", delay_days=0),
    PurchaseOrder(id="PO-2026-008", supplier_id="S02", supplier_name="Cargill Middle East", sku_id="AF001", sku_name="Poultry Layer Feed 50kg", qty=800, order_date="2026-05-05", expected_delivery="2026-05-22", status="in_transit", delay_days=0),
    PurchaseOrder(id="PO-2026-009", supplier_id="S10", supplier_name="Local UAE Packaging", sku_id="FL001", sku_name="Jenan All-Purpose Flour 1kg", qty=5000, order_date="2026-05-14", expected_delivery="2026-05-19", status="open", delay_days=0),
    PurchaseOrder(id="PO-2026-010", supplier_id="S05", supplier_name="Louis Dreyfus MENA", sku_id="OL002", sku_name="Jenan Corn Oil 1.8L", qty=600, order_date="2026-04-25", expected_delivery="2026-05-28", status="open", delay_days=0),
    PurchaseOrder(id="PO-2026-011", supplier_id="S09", supplier_name="GrainCorp MENA", sku_id="FL002", sku_name="Grand Mills Chakki Atta 10kg", qty=1800, order_date="2026-04-12", expected_delivery="2026-05-19", status="in_transit", delay_days=2),
    PurchaseOrder(id="PO-2026-012", supplier_id="S08", supplier_name="COFCO International", sku_id="RI002", sku_name="Jenan Sella Rice 10kg", qty=900, order_date="2026-04-30", expected_delivery="2026-05-26", status="open", delay_days=0),
    PurchaseOrder(id="PO-2026-013", supplier_id="S06", supplier_name="Viterra Gulf", sku_id="PA001", sku_name="Jenan Spaghetti 500g", qty=2000, order_date="2026-05-03", expected_delivery="2026-06-02", status="open", delay_days=0),
    PurchaseOrder(id="PO-2026-014", supplier_id="S03", supplier_name="Bunge MENA", sku_id="OL003", sku_name="Jenan Vegetable Oil 5L", qty=500, order_date="2026-05-08", expected_delivery="2026-06-10", status="open", delay_days=0),
    PurchaseOrder(id="PO-2026-015", supplier_id="S02", supplier_name="Cargill Middle East", sku_id="FL006", sku_name="Maida Fine Flour 50kg", qty=1500, order_date="2026-05-10", expected_delivery="2026-06-01", status="open", delay_days=0),
]


# ─── Supply Alerts (12) ───────────────────────────────────────────────────

SUPPLY_ALERTS: list[SupplyAlert] = [
    SupplyAlert(id="SA001", sku_id="FL009", sku_name="Industrial Flour 50kg", alert_type="delivery_delay", severity="critical", title="PO-2026-006 delayed 7 days", description="Black Sea Grain Corp shipment delayed due to port congestion at Jebel Ali. Expected arrival pushed to May 30.", date="2026-05-17", plant="Al Ghurair Foods Jebel Ali", recommended_action="Expedite alternative supply from Cargill or draw from Dubai safety stock"),
    SupplyAlert(id="SA002", sku_id="AF001", sku_name="Poultry Layer Feed 50kg", alert_type="stockout_risk", severity="critical", title="Feed stock critically low — 5 DOS remaining", description="Poultry Layer Feed at Grand Mills Abu Dhabi has only 5 days of supply. Current demand running 15% above forecast due to increased local poultry farm orders.", date="2026-05-18", plant="Grand Mills Abu Dhabi", recommended_action="Expedite PO-2026-008 and consider emergency local procurement"),
    SupplyAlert(id="SA003", sku_id="OL001", sku_name="Jenan Sunflower Oil 1.5L", alert_type="excess_risk", severity="warning", title="Sunflower Oil approaching excess — 38 DOS", description="Post-Ramadan demand decline faster than forecast. Current stock at 38 days vs target of 21 days. Risk of shelf-life issues if not moved.", date="2026-05-16", plant="Al Ghurair Foods Jebel Ali", recommended_action="Increase promotional allocation to Modern Trade, consider export diversion to KSA"),
    SupplyAlert(id="SA004", sku_id="SP012", sku_name="Maamoul Mix 2kg", alert_type="excess_risk", severity="warning", title="Seasonal Maamoul stock unsold — 42 DOS", description="Ramadan/Eid seasonal product with 42 days stock remaining. Demand dropped 70% post-Eid. Shelf life concern in 3 months.", date="2026-05-15", plant="Al Ghurair Foods Jebel Ali", recommended_action="Markdown pricing for clearance, halt production until next Ramadan planning"),
    SupplyAlert(id="SA005", sku_id="PA001", sku_name="Jenan Spaghetti 500g", alert_type="stockout_risk", severity="warning", title="Spaghetti stock below safety level — 11 DOS", description="Strong export demand from KSA depleting spaghetti faster than forecast. Current run-rate will exhaust stock before PO-2026-013 arrives.", date="2026-05-18", plant="Al Ghurair Foods Jebel Ali", recommended_action="Prioritize pasta line production, consider partial KSA order deferral"),
    SupplyAlert(id="SA006", sku_id=None, sku_name="Grand Mills Dubai Line A", alert_type="capacity_constraint", severity="warning", title="Flour Mill Line A approaching max utilization — 92%", description="Line A running at 92% capacity with maintenance window in 2 weeks. Limited ability to absorb demand spikes.", date="2026-05-17", plant="Grand Mills Dubai", recommended_action="Pre-build flour inventory ahead of maintenance window, shift some volume to Line B"),
    SupplyAlert(id="SA007", sku_id="FL002", sku_name="Grand Mills Chakki Atta 10kg", alert_type="delivery_delay", severity="info", title="PO-2026-011 minor delay — 2 days", description="GrainCorp MENA shipment arriving 2 days late. Minimal impact due to adequate safety stock.", date="2026-05-17", plant="Grand Mills Dubai", recommended_action="Monitor — no action required unless further delays"),
    SupplyAlert(id="SA008", sku_id="RI001", sku_name="Jenan Basmati Rice 5kg", alert_type="quality_issue", severity="warning", title="Quality variance on incoming rice shipment", description="Lab sample from PO-2026-005 showing higher moisture content than spec (13.2% vs 12.5% max). Awaiting full inspection.", date="2026-05-18", plant="Al Ghurair Foods Jebel Ali", recommended_action="Hold shipment in quarantine pending full QC. Prepare alternate supplier activation if rejected"),
    SupplyAlert(id="SA009", sku_id="SU001", sku_name="White Granulated Sugar 50kg", alert_type="stockout_risk", severity="warning", title="Sugar supply tight — 12 DOS, seasonal uptick expected", description="Industrial sugar stock at 12 days with Eid holiday baking season approaching. PO-2026-007 not arriving until May 24.", date="2026-05-18", plant="Al Ghurair Foods Jebel Ali", recommended_action="Place emergency order with Olam for fast-track delivery, negotiate air freight for partial qty"),
    SupplyAlert(id="SA010", sku_id="OL006", sku_name="Industrial Frying Oil 20L", alert_type="stockout_risk", severity="info", title="HoReCa frying oil demand spike — summer catering season", description="HoReCa channel ordering 25% above forecast as summer catering events begin. Current stock adequate (18 DOS) but trending down.", date="2026-05-16", plant="Al Ghurair Foods Jebel Ali", recommended_action="Increase next replenishment qty by 25%, align with Wilmar for expedited delivery"),
    SupplyAlert(id="SA011", sku_id="AF005", sku_name="Camel Feed 50kg", alert_type="excess_risk", severity="info", title="Camel feed slow-moving — 40 DOS", description="Low season for camel feed. Stock at 40 days but shelf life adequate (90 days). Monitor for now.", date="2026-05-14", plant="Grand Mills Abu Dhabi", recommended_action="Reduce next production batch, monitor sell-through rate"),
    SupplyAlert(id="SA012", sku_id="SP010", sku_name="Arabic Bread Premix 50kg", alert_type="capacity_constraint", severity="info", title="Premix line scheduling conflict with croissant orders", description="Specialty premix line has competing demand from Arabic Bread (steady) and Croissant (growing HoReCa). Line at 68% but changeover time reducing effective capacity.", date="2026-05-17", plant="Grand Mills Dubai", recommended_action="Optimize changeover schedule — batch Arabic Bread Mon-Wed, Croissant Thu-Sat"),
]


# ─── Replenishment Actions (8 pending) ────────────────────────────────────

REPLENISHMENT_ACTIONS: list[ReplenishmentAction] = [
    ReplenishmentAction(id="RA001", action_type="expedite", sku_id="FL009", sku_name="Industrial Flour 50kg", recommended_qty=1000, supplier_id="S02", plant=Plant.AGHURAIR_JEBELALI, urgency="critical", rationale="PO-2026-006 delayed 7 days. Bridge stock needed from Cargill to prevent stockout at Jebel Ali plant.", kpi_impact={"fill_rate": "+1.5%", "dos": "+4 days", "working_capital": "+AED 38K"}, confidence="high", scenario="balanced"),
    ReplenishmentAction(id="RA002", action_type="purchase_order", sku_id="AF001", sku_name="Poultry Layer Feed 50kg", recommended_qty=600, supplier_id="S02", plant=Plant.GRAND_MILLS_ABUDHABI, urgency="critical", rationale="Feed stock at 5 DOS — below safety threshold. Demand running 15% above forecast. Emergency order to prevent farm customer stockout.", kpi_impact={"fill_rate": "+2%", "stockout_rate": "-1.2%", "working_capital": "+AED 13.2K"}, confidence="high", scenario="aggressive"),
    ReplenishmentAction(id="RA003", action_type="production_priority", sku_id="PA001", sku_name="Jenan Spaghetti 500g", recommended_qty=800, supplier_id=None, plant=Plant.AGHURAIR_JEBELALI, urgency="high", rationale="Spaghetti at 11 DOS. Prioritize Pasta Line 1 for spaghetti run before next PO arrival on June 2.", kpi_impact={"fill_rate": "+0.8%", "dos": "+5 days", "production_utilization": "+4%"}, confidence="high", scenario="balanced"),
    ReplenishmentAction(id="RA004", action_type="safety_stock_adjust", sku_id="OL001", sku_name="Jenan Sunflower Oil 1.5L", recommended_qty=-200, supplier_id=None, plant=Plant.AGHURAIR_JEBELALI, urgency="medium", rationale="Post-Ramadan demand normalization. Reduce safety stock from 21 to 16 days to prevent obsolescence. Current DOS at 38.", kpi_impact={"obsolescence_rate": "-0.3%", "working_capital": "-AED 90K", "dos": "-5 days"}, confidence="medium", scenario="balanced"),
    ReplenishmentAction(id="RA005", action_type="purchase_order", sku_id="SU001", sku_name="White Granulated Sugar 50kg", recommended_qty=1000, supplier_id="S04", plant=Plant.AGHURAIR_JEBELALI, urgency="high", rationale="Sugar at 12 DOS with seasonal uptick expected. Fast-track order to Olam for delivery by May 22.", kpi_impact={"fill_rate": "+1%", "dos": "+8 days", "working_capital": "+AED 35K"}, confidence="high", scenario="balanced"),
    ReplenishmentAction(id="RA006", action_type="production_priority", sku_id="FL003", sku_name="Bread Flour 50kg", recommended_qty=500, supplier_id=None, plant=Plant.GRAND_MILLS_DUBAI, urgency="medium", rationale="Pre-build bread flour inventory ahead of Line A maintenance window (June 1-2). Need 2 extra days of buffer.", kpi_impact={"fill_rate": "+0.5%", "dos": "+2 days", "production_utilization": "+3%"}, confidence="high", scenario="conservative"),
    ReplenishmentAction(id="RA007", action_type="expedite", sku_id="RI001", sku_name="Jenan Basmati Rice 5kg", recommended_qty=0, supplier_id="S04", plant=Plant.AGHURAIR_JEBELALI, urgency="medium", rationale="Quality hold on PO-2026-005. If rejected, activate backup supply from Olam alternate warehouse. No qty change yet — contingency.", kpi_impact={"fill_rate": "0%", "quality_score": "maintain"}, confidence="low", scenario="conservative"),
    ReplenishmentAction(id="RA008", action_type="safety_stock_adjust", sku_id="SP012", sku_name="Maamoul Mix 2kg", recommended_qty=-150, supplier_id=None, plant=Plant.AGHURAIR_JEBELALI, urgency="low", rationale="Seasonal product — Ramadan/Eid demand complete. Reduce safety stock to minimal level, halt production until Sep planning cycle.", kpi_impact={"obsolescence_rate": "-0.2%", "working_capital": "-AED 10.5K"}, confidence="high", scenario="balanced"),
]


# ─── KPI Metrics ───────────────────────────────────────────────────────────

CURRENT_KPIS = KPIMetrics(
    forecast_accuracy_mape=12.8,
    inventory_dos=18.4,
    fill_rate=96.2,
    stockout_rate=2.8,
    obsolescence_rate=1.2,
    working_capital_mm=42.5,
    production_utilization=81.3,
    on_time_delivery=89.5,
    alerts_open=len([a for a in SUPPLY_ALERTS if not a.read]),
    pending_actions=len(REPLENISHMENT_ACTIONS),
)

KPI_HISTORY: list[dict] = [
    {"week": "2026-W15", "mape": 14.2, "dos": 19.1, "fill_rate": 95.8, "stockout_rate": 3.1, "obsolescence": 1.4},
    {"week": "2026-W16", "mape": 13.5, "dos": 18.8, "fill_rate": 96.0, "stockout_rate": 2.9, "obsolescence": 1.3},
    {"week": "2026-W17", "mape": 13.1, "dos": 18.5, "fill_rate": 96.1, "stockout_rate": 2.7, "obsolescence": 1.3},
    {"week": "2026-W18", "mape": 12.9, "dos": 18.3, "fill_rate": 96.3, "stockout_rate": 2.6, "obsolescence": 1.2},
    {"week": "2026-W19", "mape": 12.8, "dos": 18.4, "fill_rate": 96.2, "stockout_rate": 2.8, "obsolescence": 1.2},
    {"week": "2026-W20", "mape": 12.5, "dos": 18.2, "fill_rate": 96.5, "stockout_rate": 2.5, "obsolescence": 1.1},
]


# ─── Supplier Contacts (1 per supplier) ─────────────────────────────────────

SUPPLIER_CONTACTS: list[SupplierContact] = [
    SupplierContact(supplier_id="S01", name="Dmytro Kovalenko", role="Account Manager", email="d.kovalenko@bsgcorp.ua", phone="+380 44 555 0101"),
    SupplierContact(supplier_id="S02", name="Michael Chen", role="Regional Director MENA", email="m.chen@cargill.com", phone="+971 4 321 0200"),
    SupplierContact(supplier_id="S03", name="Ricardo Oliveira", role="Senior Account Executive", email="r.oliveira@bunge.com", phone="+55 11 3035 5500"),
    SupplierContact(supplier_id="S04", name="Priya Sharma", role="Key Account Manager", email="p.sharma@olamagri.com", phone="+65 6339 4100"),
    SupplierContact(supplier_id="S05", name="Jean-Pierre Moreau", role="Trade Director Gulf", email="jp.moreau@ldc.com", phone="+33 1 4069 5000"),
    SupplierContact(supplier_id="S06", name="David Wilson", role="Export Manager MENA", email="d.wilson@viterra.com", phone="+1 306 569 4411"),
    SupplierContact(supplier_id="S07", name="Tan Wei Lin", role="Sales Director Middle East", email="w.tan@wilmar.com", phone="+60 3 2117 8888"),
    SupplierContact(supplier_id="S08", name="Zhang Wei", role="International Trade Manager", email="w.zhang@cofco.com", phone="+86 10 8260 6688"),
    SupplierContact(supplier_id="S09", name="James Mitchell", role="Head of MENA Sales", email="j.mitchell@graincorp.com.au", phone="+61 2 9325 9100"),
    SupplierContact(supplier_id="S10", name="Ahmed Al Rashid", role="General Manager", email="ahmed@localuaepack.ae", phone="+971 4 885 9900"),
]


# ─── Supplier Performance History (6 months × 10 suppliers) ──────────────────

def _generate_supplier_performance() -> list[SupplierPerformanceRecord]:
    records = []
    months = ["2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]
    base_profiles = {
        "S01": {"otd": 70, "quality": 76, "lead": 28, "incidents_rate": 0.3},
        "S02": {"otd": 94, "quality": 95, "lead": 21, "incidents_rate": 0.05},
        "S03": {"otd": 87, "quality": 91, "lead": 35, "incidents_rate": 0.1},
        "S04": {"otd": 90, "quality": 89, "lead": 18, "incidents_rate": 0.08},
        "S05": {"otd": 84, "quality": 88, "lead": 25, "incidents_rate": 0.12},
        "S06": {"otd": 89, "quality": 93, "lead": 30, "incidents_rate": 0.07},
        "S07": {"otd": 92, "quality": 90, "lead": 14, "incidents_rate": 0.06},
        "S08": {"otd": 80, "quality": 81, "lead": 22, "incidents_rate": 0.2},
        "S09": {"otd": 86, "quality": 96, "lead": 32, "incidents_rate": 0.05},
        "S10": {"otd": 95, "quality": 92, "lead": 5, "incidents_rate": 0.03},
    }
    for sid, profile in base_profiles.items():
        for i, month in enumerate(months):
            trend = i * 0.3
            records.append(SupplierPerformanceRecord(
                supplier_id=sid,
                month=month,
                on_time_delivery_pct=round(min(99, profile["otd"] + random.uniform(-3, 3) + trend), 1),
                quality_pass_rate=round(min(99.5, profile["quality"] + random.uniform(-2, 2)), 1),
                avg_lead_time_days=profile["lead"] + random.randint(-2, 3),
                incidents=1 if random.random() < profile["incidents_rate"] else 0,
            ))
    return records


SUPPLIER_PERFORMANCE: list[SupplierPerformanceRecord] = _generate_supplier_performance()


# ─── Supplier Certifications (~3 per supplier) ───────────────────────────────

SUPPLIER_CERTIFICATIONS: list[SupplierCertification] = [
    SupplierCertification(supplier_id="S01", name="ISO 9001:2015", status="valid", expiry_date="2027-03-15", issuing_body="TÜV SÜD"),
    SupplierCertification(supplier_id="S01", name="HACCP", status="valid", expiry_date="2026-11-20", issuing_body="SGS"),
    SupplierCertification(supplier_id="S01", name="Halal", status="expiring", expiry_date="2026-07-01", issuing_body="ESMA"),
    SupplierCertification(supplier_id="S02", name="ISO 9001:2015", status="valid", expiry_date="2027-08-30", issuing_body="Bureau Veritas"),
    SupplierCertification(supplier_id="S02", name="FSSC 22000", status="valid", expiry_date="2027-06-15", issuing_body="SGS"),
    SupplierCertification(supplier_id="S02", name="Halal", status="valid", expiry_date="2027-01-20", issuing_body="IFANCA"),
    SupplierCertification(supplier_id="S03", name="ISO 14001", status="valid", expiry_date="2027-04-10", issuing_body="DNV"),
    SupplierCertification(supplier_id="S03", name="RSPO", status="valid", expiry_date="2026-12-30", issuing_body="RSPO Secretariat"),
    SupplierCertification(supplier_id="S03", name="Halal", status="valid", expiry_date="2027-02-28", issuing_body="MUI"),
    SupplierCertification(supplier_id="S04", name="ISO 22000", status="valid", expiry_date="2027-05-20", issuing_body="Intertek"),
    SupplierCertification(supplier_id="S04", name="Organic", status="valid", expiry_date="2026-09-15", issuing_body="Control Union"),
    SupplierCertification(supplier_id="S04", name="Halal", status="valid", expiry_date="2027-03-10", issuing_body="JAKIM"),
    SupplierCertification(supplier_id="S05", name="ISO 9001:2015", status="valid", expiry_date="2027-07-22", issuing_body="AFNOR"),
    SupplierCertification(supplier_id="S05", name="BRC Global Standard", status="valid", expiry_date="2026-10-15", issuing_body="BRC"),
    SupplierCertification(supplier_id="S05", name="Halal", status="valid", expiry_date="2026-12-01", issuing_body="ESMA"),
    SupplierCertification(supplier_id="S06", name="ISO 9001:2015", status="valid", expiry_date="2027-09-10", issuing_body="SAI Global"),
    SupplierCertification(supplier_id="S06", name="CFIA Approved", status="valid", expiry_date="2027-04-30", issuing_body="CFIA"),
    SupplierCertification(supplier_id="S06", name="Kosher", status="valid", expiry_date="2026-11-30", issuing_body="OK Kosher"),
    SupplierCertification(supplier_id="S07", name="RSPO", status="valid", expiry_date="2027-01-15", issuing_body="RSPO Secretariat"),
    SupplierCertification(supplier_id="S07", name="ISO 22000", status="valid", expiry_date="2027-06-20", issuing_body="SGS"),
    SupplierCertification(supplier_id="S07", name="Halal", status="valid", expiry_date="2027-05-10", issuing_body="JAKIM"),
    SupplierCertification(supplier_id="S08", name="ISO 9001:2015", status="valid", expiry_date="2026-08-15", issuing_body="CQC"),
    SupplierCertification(supplier_id="S08", name="HACCP", status="expiring", expiry_date="2026-06-30", issuing_body="CNCA"),
    SupplierCertification(supplier_id="S08", name="Halal", status="expired", expiry_date="2026-03-01", issuing_body="ESMA"),
    SupplierCertification(supplier_id="S09", name="ISO 9001:2015", status="valid", expiry_date="2027-11-20", issuing_body="SAI Global"),
    SupplierCertification(supplier_id="S09", name="FSSC 22000", status="valid", expiry_date="2027-08-10", issuing_body="BSI"),
    SupplierCertification(supplier_id="S09", name="Organic", status="valid", expiry_date="2027-02-15", issuing_body="Australian Organic"),
    SupplierCertification(supplier_id="S10", name="ISO 9001:2015", status="valid", expiry_date="2027-06-30", issuing_body="Bureau Veritas"),
    SupplierCertification(supplier_id="S10", name="ESMA Approved", status="valid", expiry_date="2027-12-31", issuing_body="ESMA"),
    SupplierCertification(supplier_id="S10", name="FSC Chain of Custody", status="valid", expiry_date="2026-10-20", issuing_body="FSC"),
]


# ─── Alternative Suppliers (~2 per A-class SKU) ──────────────────────────────

ALTERNATIVE_SUPPLIERS: list[AlternativeSupplier] = [
    AlternativeSupplier(sku_id="FL001", supplier_id="S05", supplier_name="Louis Dreyfus MENA", lead_time_days=27, unit_cost_premium_pct=4.5, min_order_qty=600, notes="Good quality French wheat, slightly longer lead time"),
    AlternativeSupplier(sku_id="FL001", supplier_id="S09", supplier_name="GrainCorp MENA", lead_time_days=33, unit_cost_premium_pct=8.0, min_order_qty=400, notes="Premium Australian wheat, best for high-protein flour"),
    AlternativeSupplier(sku_id="FL002", supplier_id="S02", supplier_name="Cargill Middle East", lead_time_days=22, unit_cost_premium_pct=3.0, min_order_qty=250, notes="Reliable US supplier, fast turnaround"),
    AlternativeSupplier(sku_id="FL002", supplier_id="S01", supplier_name="Black Sea Grain Corp", lead_time_days=30, unit_cost_premium_pct=-5.0, min_order_qty=300, notes="Cost-effective but less reliable delivery"),
    AlternativeSupplier(sku_id="FL003", supplier_id="S06", supplier_name="Viterra Gulf", lead_time_days=28, unit_cost_premium_pct=2.5, min_order_qty=150, notes="Canadian durum, excellent for bread flour"),
    AlternativeSupplier(sku_id="FL003", supplier_id="S05", supplier_name="Louis Dreyfus MENA", lead_time_days=26, unit_cost_premium_pct=3.8, min_order_qty=120, notes="French wheat blend, good consistency"),
    AlternativeSupplier(sku_id="FL006", supplier_id="S02", supplier_name="Cargill Middle East", lead_time_days=23, unit_cost_premium_pct=5.0, min_order_qty=120, notes="Premium US soft wheat for maida"),
    AlternativeSupplier(sku_id="FL008", supplier_id="S09", supplier_name="GrainCorp MENA", lead_time_days=34, unit_cost_premium_pct=6.5, min_order_qty=80, notes="High-protein durum for premium semolina"),
    AlternativeSupplier(sku_id="FL009", supplier_id="S02", supplier_name="Cargill Middle East", lead_time_days=22, unit_cost_premium_pct=7.0, min_order_qty=200, notes="Emergency backup — fast delivery from Dubai warehouse"),
    AlternativeSupplier(sku_id="FL009", supplier_id="S05", supplier_name="Louis Dreyfus MENA", lead_time_days=27, unit_cost_premium_pct=2.0, min_order_qty=250, notes="Comparable quality at near-parity cost"),
    AlternativeSupplier(sku_id="PA001", supplier_id="S06", supplier_name="Viterra Gulf", lead_time_days=26, unit_cost_premium_pct=3.0, min_order_qty=500, notes="Canadian durum ideal for pasta"),
    AlternativeSupplier(sku_id="PA001", supplier_id="S02", supplier_name="Cargill Middle East", lead_time_days=24, unit_cost_premium_pct=5.5, min_order_qty=300, notes="US durum, slightly different gluten profile"),
    AlternativeSupplier(sku_id="PA002", supplier_id="S06", supplier_name="Viterra Gulf", lead_time_days=26, unit_cost_premium_pct=3.0, min_order_qty=350, notes="Same spec as spaghetti — batch together"),
    AlternativeSupplier(sku_id="PA003", supplier_id="S06", supplier_name="Viterra Gulf", lead_time_days=26, unit_cost_premium_pct=3.5, min_order_qty=400, notes="Bundled procurement with other pasta SKUs"),
    AlternativeSupplier(sku_id="OL001", supplier_id="S07", supplier_name="Wilmar International", lead_time_days=16, unit_cost_premium_pct=2.0, min_order_qty=200, notes="Fast delivery from Malaysia, high-oleic variant available"),
    AlternativeSupplier(sku_id="OL001", supplier_id="S05", supplier_name="Louis Dreyfus MENA", lead_time_days=28, unit_cost_premium_pct=-2.0, min_order_qty=350, notes="French sunflower, cost-effective for bulk"),
    AlternativeSupplier(sku_id="OL002", supplier_id="S07", supplier_name="Wilmar International", lead_time_days=15, unit_cost_premium_pct=4.0, min_order_qty=150, notes="Can substitute with palm-corn blend"),
    AlternativeSupplier(sku_id="OL003", supplier_id="S03", supplier_name="Bunge MENA", lead_time_days=36, unit_cost_premium_pct=0.0, min_order_qty=100, notes="Primary supplier — this is backup stock allocation"),
    AlternativeSupplier(sku_id="RI001", supplier_id="S08", supplier_name="COFCO International", lead_time_days=24, unit_cost_premium_pct=6.0, min_order_qty=180, notes="Chinese-sourced basmati, acceptable quality grade B"),
    AlternativeSupplier(sku_id="RI002", supplier_id="S04", supplier_name="Olam Agri", lead_time_days=20, unit_cost_premium_pct=3.5, min_order_qty=100, notes="Indian parboiled rice — direct origin sourcing"),
    AlternativeSupplier(sku_id="SU001", supplier_id="S08", supplier_name="COFCO International", lead_time_days=24, unit_cost_premium_pct=4.0, min_order_qty=250, notes="Chinese refined sugar, meets ESMA standards"),
    AlternativeSupplier(sku_id="SU001", supplier_id="S03", supplier_name="Bunge MENA", lead_time_days=32, unit_cost_premium_pct=1.5, min_order_qty=300, notes="Brazilian raw sugar for refining"),
    AlternativeSupplier(sku_id="AF001", supplier_id="S04", supplier_name="Olam Agri", lead_time_days=20, unit_cost_premium_pct=8.0, min_order_qty=100, notes="Soybean meal component source — formulate locally"),
    AlternativeSupplier(sku_id="AF002", supplier_id="S02", supplier_name="Cargill Middle East", lead_time_days=23, unit_cost_premium_pct=5.0, min_order_qty=100, notes="Complete feed premix — higher cost but fast"),
    AlternativeSupplier(sku_id="SP010", supplier_id="S02", supplier_name="Cargill Middle East", lead_time_days=22, unit_cost_premium_pct=10.0, min_order_qty=50, notes="Specialty flour blend — needs recipe adjustment"),
    AlternativeSupplier(sku_id="OL006", supplier_id="S07", supplier_name="Wilmar International", lead_time_days=12, unit_cost_premium_pct=3.0, min_order_qty=30, notes="Palm-based frying oil, good HoReCa acceptance"),
]


# ─── Maintenance Events (~5 per production line) ─────────────────────────────

def _generate_maintenance_events() -> list[MaintenanceEvent]:
    events = []
    line_profiles = {
        "PL01": {"freq": 5, "types": ["planned", "planned", "unplanned", "planned", "breakdown"]},
        "PL02": {"freq": 5, "types": ["planned", "planned", "planned", "unplanned", "planned"]},
        "PL03": {"freq": 4, "types": ["planned", "planned", "unplanned", "planned"]},
        "PL04": {"freq": 5, "types": ["planned", "breakdown", "planned", "planned", "unplanned"]},
        "PL05": {"freq": 6, "types": ["planned", "planned", "unplanned", "planned", "breakdown", "planned"]},
        "PL06": {"freq": 5, "types": ["planned", "planned", "planned", "unplanned", "planned"]},
        "PL07": {"freq": 4, "types": ["planned", "planned", "unplanned", "planned"]},
        "PL08": {"freq": 5, "types": ["planned", "planned", "planned", "planned", "unplanned"]},
    }
    root_causes_by_type = {
        "planned": ["Scheduled bearing replacement", "Lubrication cycle", "Belt tension check", "Sieve mesh replacement", "Roller gap calibration", "Filter cleaning"],
        "unplanned": ["Unexpected vibration detected", "Temperature sensor alert", "Motor current spike", "Conveyor belt misalignment", "Packaging seal failure"],
        "breakdown": ["Main motor burnout", "Gearbox failure", "Hydraulic line rupture", "PLC controller fault", "Compressor failure"],
    }
    base_date = date(2026, 1, 10)
    for line_id, profile in line_profiles.items():
        for i, mtype in enumerate(profile["types"]):
            event_date = base_date + timedelta(days=random.randint(i * 25, (i + 1) * 30))
            duration = random.uniform(2, 8) if mtype == "planned" else (random.uniform(4, 24) if mtype == "breakdown" else random.uniform(1, 6))
            cost = duration * random.uniform(800, 3000) if mtype == "breakdown" else duration * random.uniform(200, 800)
            events.append(MaintenanceEvent(
                line_id=line_id,
                date=event_date.isoformat(),
                duration_hours=round(duration, 1),
                type=mtype,
                root_cause=random.choice(root_causes_by_type[mtype]),
                cost_aed=round(cost, 0),
            ))
    return events


MAINTENANCE_EVENTS: list[MaintenanceEvent] = _generate_maintenance_events()


# ─── Quality Test Results (~2 per SKU, recent batches) ────────────────────────

def _generate_quality_results() -> list[QualityTestResult]:
    results = []
    inspectors = ["Fatima Al Zahra", "Rajesh Patel", "Omar Hassan", "Sara Ibrahim", "Chen Yao"]
    for sku in SKUS:
        for batch_num in range(1, 3):
            test_date = date(2026, 5, random.randint(1, 17))
            batch_id = f"B-{sku.id}-{test_date.strftime('%m%d')}-{batch_num:02d}"
            is_flour = sku.category == Category.FLOUR
            is_oil = sku.category == Category.COOKING_OIL
            moisture = round(random.uniform(10.5, 14.0), 1) if is_flour else (round(random.uniform(0.05, 0.15), 2) if is_oil else None)
            protein = round(random.uniform(9.0, 13.5), 1) if is_flour else None
            contaminant = "pass" if random.random() < 0.92 else ("marginal" if random.random() < 0.7 else "fail")
            overall = "pass" if contaminant == "pass" and (moisture is None or moisture < 13.5) else ("hold" if contaminant == "marginal" else "reject")
            results.append(QualityTestResult(
                sku_id=sku.id,
                batch_id=batch_id,
                test_date=test_date.isoformat(),
                moisture_pct=moisture,
                protein_pct=protein,
                contaminant_level=contaminant,
                overall_result=overall,
                inspector=random.choice(inspectors),
            ))
    return results


QUALITY_TEST_RESULTS: list[QualityTestResult] = _generate_quality_results()


# ─── Production Runs (~10 per line) ──────────────────────────────────────────

def _generate_production_runs() -> list[ProductionRun]:
    runs = []
    line_skus = {
        "PL01": ["FL003", "FL001", "FL002"],
        "PL02": ["FL001", "FL004", "SP005"],
        "PL03": ["SP010", "SP006", "SP011"],
        "PL04": ["FL006", "FL005", "FL008"],
        "PL05": ["AF001", "AF002", "AF003"],
        "PL06": ["PA001", "PA002", "PA003"],
        "PL07": ["OL001", "OL002", "OL003"],
        "PL08": ["RI001", "RI002", "SU001"],
    }
    shifts = ["Morning", "Afternoon", "Night"]
    base_date = date(2026, 5, 5)
    for line_id, skus in line_skus.items():
        for i in range(10):
            run_date = base_date + timedelta(days=i + random.randint(0, 2))
            sku_id = skus[i % len(skus)]
            planned = random.uniform(30, 120)
            yield_pct = random.uniform(94, 99.5)
            actual = planned * yield_pct / 100
            waste = 100 - yield_pct
            runs.append(ProductionRun(
                line_id=line_id,
                sku_id=sku_id,
                date=run_date.isoformat(),
                planned_qty=round(planned, 1),
                actual_qty=round(actual, 1),
                yield_pct=round(yield_pct, 1),
                waste_pct=round(waste, 1),
                shift=random.choice(shifts),
            ))
    return runs


PRODUCTION_RUNS: list[ProductionRun] = _generate_production_runs()
