"""Synthetic data store for HD ATLAS — 50 SKUs, suppliers, demand, inventory (aerospace)."""
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
    Contract, ContractPriceValidation, POValidationResult, DailyLaborRecord,
)

random.seed(42)

# ─── SKU Master (50 items) ─────────────────────────────────────────────────

SKUS: list[SKU] = [
    # Landing Gear (10)
    SKU(id="LG001", name="777X MLG Shock Strut Assy", name_fr="Ensemble amortisseur train principal 777X", name_es="Conjunto amortiguador tren principal 777X", category=Category.LANDING_GEAR, part_number="PN-LG-777X-SS-001", drawing_rev="D", material_spec="300M Steel", program="Boeing 777X", uom="Each", unit_cost=185000.0, inspection_interval_days=180, abc_class="A", xyz_class="X", min_order_qty=2, lead_time_days=120, safety_stock_days=45, plant=Plant.LONGUEUIL_QC),
    SKU(id="LG002", name="A350 NLG Cylinder", name_fr="Cylindre train avant A350", name_es="Cilindro tren delantero A350", category=Category.LANDING_GEAR, part_number="PN-LG-A350-NLC-001", drawing_rev="C", material_spec="Ti-6Al-4V", program="Airbus A350", uom="Each", unit_cost=92000.0, inspection_interval_days=180, abc_class="A", xyz_class="X", min_order_qty=4, lead_time_days=90, safety_stock_days=30, plant=Plant.LONGUEUIL_QC),
    SKU(id="LG003", name="F-35 MLG Side Brace", name_fr="Contrefiche latérale train principal F-35", name_es="Abrazadera lateral tren principal F-35", category=Category.LANDING_GEAR, part_number="PN-LG-F35-SB-001", drawing_rev="E", material_spec="Custom 465 Steel", program="F-35 JSF", uom="Each", unit_cost=145000.0, inspection_interval_days=120, abc_class="A", xyz_class="X", min_order_qty=2, lead_time_days=150, safety_stock_days=60, plant=Plant.SPRINGFIELD_OH),
    SKU(id="LG004", name="CH-53K MLG Axle Forging", name_fr="Forgeage essieu train principal CH-53K", name_es="Forja eje tren principal CH-53K", category=Category.LANDING_GEAR, part_number="PN-LG-CH53K-AX-001", drawing_rev="B", material_spec="4340 Steel", program="CH-53K", uom="Each", unit_cost=68000.0, inspection_interval_days=180, abc_class="A", xyz_class="Y", min_order_qty=4, lead_time_days=100, safety_stock_days=30, plant=Plant.KITCHENER_ON),
    SKU(id="LG005", name="737MAX NLG Trunnion", name_fr="Tourillon train avant 737MAX", name_es="Muñón tren delantero 737MAX", category=Category.LANDING_GEAR, part_number="PN-LG-737M-TR-001", drawing_rev="F", material_spec="Ti-10V-2Fe-3Al", program="Boeing 737 MAX", uom="Each", unit_cost=42000.0, inspection_interval_days=180, abc_class="A", xyz_class="X", min_order_qty=6, lead_time_days=75, safety_stock_days=21, plant=Plant.LONGUEUIL_QC),
    SKU(id="LG006", name="A220 MLG Bogie Beam", name_fr="Poutre bogie train principal A220", name_es="Viga bogie tren principal A220", category=Category.LANDING_GEAR, part_number="PN-LG-A220-BB-001", drawing_rev="C", material_spec="300M Steel", program="Airbus A220", uom="Each", unit_cost=56000.0, inspection_interval_days=180, abc_class="A", xyz_class="X", min_order_qty=4, lead_time_days=80, safety_stock_days=28, plant=Plant.LONGUEUIL_QC),
    SKU(id="LG007", name="Global 7500 NLG Drag Brace", name_fr="Contrefiche de trainée train avant Global 7500", name_es="Abrazadera de arrastre tren delantero Global 7500", category=Category.LANDING_GEAR, part_number="PN-LG-G7500-DB-001", drawing_rev="B", material_spec="15-5 PH Steel", program="Global 7500", uom="Each", unit_cost=38000.0, inspection_interval_days=180, abc_class="B", xyz_class="Y", min_order_qty=4, lead_time_days=60, safety_stock_days=21, plant=Plant.KITCHENER_ON),
    SKU(id="LG008", name="CF-18 MLG Oleo Strut Overhaul Kit", name_fr="Kit de révision amortisseur oléo train principal CF-18", name_es="Kit revisión amortiguador oleo tren principal CF-18", category=Category.LANDING_GEAR, part_number="PN-LG-CF18-OH-001", drawing_rev="G", material_spec="4340/300M", program="CF-18 Hornet", uom="Kit", unit_cost=28500.0, inspection_interval_days=90, abc_class="B", xyz_class="Y", min_order_qty=6, lead_time_days=45, safety_stock_days=14, plant=Plant.LAVAL_QC),
    SKU(id="LG009", name="E-2D NLG Steering Collar", name_fr="Collier de direction train avant E-2D", name_es="Collar de dirección tren delantero E-2D", category=Category.LANDING_GEAR, part_number="PN-LG-E2D-SC-001", drawing_rev="C", material_spec="Inconel 718", program="E-2D Hawkeye", uom="Each", unit_cost=22000.0, inspection_interval_days=120, abc_class="B", xyz_class="Z", min_order_qty=8, lead_time_days=60, safety_stock_days=21, plant=Plant.SPRINGFIELD_OH),
    SKU(id="LG010", name="CRJ Spare MLG Walking Beam", name_fr="Poutre de roulement rechange train principal CRJ", name_es="Viga de rodadura repuesto tren principal CRJ", category=Category.LANDING_GEAR, part_number="PN-LG-CRJ-WB-001", drawing_rev="D", material_spec="4340 Steel", program="CRJ Series", uom="Each", unit_cost=18000.0, inspection_interval_days=180, abc_class="C", xyz_class="Z", min_order_qty=6, lead_time_days=45, safety_stock_days=14, plant=Plant.KITCHENER_ON),
    # Actuation Systems (8)
    SKU(id="AC001", name="A350 Flap Actuator Assembly", name_fr="Ensemble actionneur de volets A350", name_es="Conjunto actuador de flaps A350", category=Category.ACTUATION, part_number="PN-AC-A350-FA-001", drawing_rev="C", material_spec="15-5 PH Steel", program="Airbus A350", uom="Each", unit_cost=72000.0, inspection_interval_days=150, abc_class="A", xyz_class="X", min_order_qty=4, lead_time_days=85, safety_stock_days=28, plant=Plant.KITCHENER_ON),
    SKU(id="AC002", name="777X Spoiler Actuator", name_fr="Actionneur de spoiler 777X", name_es="Actuador de spoiler 777X", category=Category.ACTUATION, part_number="PN-AC-777X-SP-001", drawing_rev="B", material_spec="Titanium Beta C", program="Boeing 777X", uom="Each", unit_cost=54000.0, inspection_interval_days=150, abc_class="A", xyz_class="X", min_order_qty=6, lead_time_days=80, safety_stock_days=28, plant=Plant.KITCHENER_ON),
    SKU(id="AC003", name="F-35 Weapons Bay Door Actuator", name_fr="Actionneur porte soute armes F-35", name_es="Actuador puerta compartimento armas F-35", category=Category.ACTUATION, part_number="PN-AC-F35-WB-001", drawing_rev="D", material_spec="Custom 465 Steel", program="F-35 JSF", uom="Each", unit_cost=125000.0, inspection_interval_days=90, abc_class="A", xyz_class="Y", min_order_qty=2, lead_time_days=120, safety_stock_days=45, plant=Plant.SPRINGFIELD_OH),
    SKU(id="AC004", name="A220 Slat Actuator LVDT Module", name_fr="Module LVDT actionneur de bec A220", name_es="Módulo LVDT actuador de slat A220", category=Category.ACTUATION, part_number="PN-AC-A220-SL-001", drawing_rev="B", material_spec="17-4 PH Steel", program="Airbus A220", uom="Each", unit_cost=18500.0, inspection_interval_days=120, abc_class="B", xyz_class="X", min_order_qty=8, lead_time_days=55, safety_stock_days=21, plant=Plant.KITCHENER_ON),
    SKU(id="AC005", name="Global 7500 Thrust Reverser Actuator", name_fr="Actionneur inverseur de poussée Global 7500", name_es="Actuador reversor de empuje Global 7500", category=Category.ACTUATION, part_number="PN-AC-G7500-TR-001", drawing_rev="C", material_spec="Inconel 718", program="Global 7500", uom="Each", unit_cost=86000.0, inspection_interval_days=180, abc_class="A", xyz_class="Y", min_order_qty=2, lead_time_days=100, safety_stock_days=35, plant=Plant.LAVAL_QC),
    SKU(id="AC006", name="CH-47 Ramp Actuator", name_fr="Actionneur de rampe CH-47", name_es="Actuador de rampa CH-47", category=Category.ACTUATION, part_number="PN-AC-CH47-RA-001", drawing_rev="E", material_spec="4340 Steel", program="CH-47 Chinook", uom="Each", unit_cost=34000.0, inspection_interval_days=150, abc_class="B", xyz_class="Y", min_order_qty=4, lead_time_days=65, safety_stock_days=21, plant=Plant.SPRINGFIELD_OH),
    SKU(id="AC007", name="CESA A320 Horizontal Stab Actuator", name_fr="Actionneur stabilisateur horizontal A320 CESA", name_es="Actuador estabilizador horizontal A320 CESA", category=Category.ACTUATION, part_number="PN-AC-A320-HS-001", drawing_rev="F", material_spec="15-5 PH Steel", program="Airbus A320", uom="Each", unit_cost=62000.0, inspection_interval_days=180, abc_class="A", xyz_class="X", min_order_qty=6, lead_time_days=70, safety_stock_days=28, plant=Plant.GETAFE_MADRID),
    SKU(id="AC008", name="CESA A330 MLG Door Actuator", name_fr="Actionneur porte train principal A330 CESA", name_es="Actuador puerta tren principal A330 CESA", category=Category.ACTUATION, part_number="PN-AC-A330-DRA-001", drawing_rev="D", material_spec="17-4 PH Steel", program="Airbus A330", uom="Each", unit_cost=44000.0, inspection_interval_days=180, abc_class="B", xyz_class="X", min_order_qty=4, lead_time_days=65, safety_stock_days=21, plant=Plant.SEVILLE_SPAIN),
    # Hydraulics (7)
    SKU(id="HY001", name="777X MLG Retract Hydraulic Cylinder", name_fr="Cylindre hydraulique rétraction train principal 777X", name_es="Cilindro hidráulico retracción tren principal 777X", category=Category.HYDRAULICS, part_number="PN-HY-777X-RC-001", drawing_rev="C", material_spec="Ti-6Al-4V", program="Boeing 777X", uom="Each", unit_cost=48000.0, inspection_interval_days=120, abc_class="A", xyz_class="X", min_order_qty=4, lead_time_days=75, safety_stock_days=28, plant=Plant.LONGUEUIL_QC),
    SKU(id="HY002", name="A350 NLG Steering Servo Valve", name_fr="Servo-valve direction train avant A350", name_es="Servo-válvula dirección tren delantero A350", category=Category.HYDRAULICS, part_number="PN-HY-A350-SV-001", drawing_rev="D", material_spec="440C Steel", program="Airbus A350", uom="Each", unit_cost=15200.0, inspection_interval_days=90, abc_class="A", xyz_class="X", min_order_qty=10, lead_time_days=45, safety_stock_days=21, plant=Plant.LONGUEUIL_QC),
    SKU(id="HY003", name="F-35 Brake Hydraulic Module", name_fr="Module hydraulique frein F-35", name_es="Módulo hidráulico freno F-35", category=Category.HYDRAULICS, part_number="PN-HY-F35-BM-001", drawing_rev="E", material_spec="Inconel 718", program="F-35 JSF", uom="Each", unit_cost=62000.0, inspection_interval_days=90, abc_class="A", xyz_class="Y", min_order_qty=4, lead_time_days=110, safety_stock_days=45, plant=Plant.SPRINGFIELD_OH),
    SKU(id="HY004", name="A220 Brake Metering Valve", name_fr="Robinet doseur frein A220", name_es="Válvula dosificadora freno A220", category=Category.HYDRAULICS, part_number="PN-HY-A220-BMV-001", drawing_rev="B", material_spec="17-4 PH Steel", program="Airbus A220", uom="Each", unit_cost=8900.0, inspection_interval_days=120, abc_class="B", xyz_class="X", min_order_qty=12, lead_time_days=40, safety_stock_days=14, plant=Plant.LAVAL_QC),
    SKU(id="HY005", name="737MAX MLG Uplock Actuator", name_fr="Actionneur verrouillage haut train principal 737MAX", name_es="Actuador cerrojo superior tren principal 737MAX", category=Category.HYDRAULICS, part_number="PN-HY-737M-UA-001", drawing_rev="C", material_spec="15-5 PH Steel", program="Boeing 737 MAX", uom="Each", unit_cost=22500.0, inspection_interval_days=150, abc_class="A", xyz_class="X", min_order_qty=8, lead_time_days=55, safety_stock_days=21, plant=Plant.LONGUEUIL_QC),
    SKU(id="HY006", name="Global Express Shimmy Damper", name_fr="Amortisseur de shimmy Global Express", name_es="Amortiguador de shimmy Global Express", category=Category.HYDRAULICS, part_number="PN-HY-GEX-SD-001", drawing_rev="D", material_spec="4130 Steel", program="Global Express", uom="Each", unit_cost=12800.0, inspection_interval_days=180, abc_class="B", xyz_class="Y", min_order_qty=6, lead_time_days=35, safety_stock_days=14, plant=Plant.KITCHENER_ON),
    SKU(id="HY007", name="CRJ Hydraulic Brake Manifold", name_fr="Collecteur hydraulique frein CRJ", name_es="Colector hidráulico freno CRJ", category=Category.HYDRAULICS, part_number="PN-HY-CRJ-BM-001", drawing_rev="C", material_spec="Aluminum 7075-T6", program="CRJ Series", uom="Each", unit_cost=6500.0, inspection_interval_days=180, abc_class="C", xyz_class="Z", min_order_qty=10, lead_time_days=30, safety_stock_days=14, plant=Plant.LAVAL_QC),
    # Structures (8)
    SKU(id="ST001", name="Ti-6Al-4V MLG Forging Blank", name_fr="Ébauche forgeage Ti-6Al-4V train principal", name_es="Pieza bruta forja Ti-6Al-4V tren principal", category=Category.STRUCTURES, part_number="PN-ST-TI64-FRG-001", drawing_rev="B", material_spec="Ti-6Al-4V AMS4928", program="Multi-Program", uom="Each", unit_cost=28000.0, inspection_interval_days=365, abc_class="A", xyz_class="X", min_order_qty=10, lead_time_days=90, safety_stock_days=30, plant=Plant.LONGUEUIL_QC),
    SKU(id="ST002", name="300M Shock Strut Forging", name_fr="Forgeage amortisseur 300M", name_es="Forja amortiguador 300M", category=Category.STRUCTURES, part_number="PN-ST-300M-SS-001", drawing_rev="C", material_spec="300M AMS6419", program="Multi-Program", uom="Each", unit_cost=34000.0, inspection_interval_days=365, abc_class="A", xyz_class="X", min_order_qty=8, lead_time_days=100, safety_stock_days=35, plant=Plant.LONGUEUIL_QC),
    SKU(id="ST003", name="Inconel 718 Brake Housing Casting", name_fr="Moulage boîtier frein Inconel 718", name_es="Fundición carcasa freno Inconel 718", category=Category.STRUCTURES, part_number="PN-ST-IN718-BH-001", drawing_rev="D", material_spec="Inconel 718 AMS5663", program="Multi-Program", uom="Each", unit_cost=18500.0, inspection_interval_days=180, abc_class="A", xyz_class="Y", min_order_qty=10, lead_time_days=75, safety_stock_days=28, plant=Plant.KITCHENER_ON),
    SKU(id="ST004", name="Al 7075-T6 Actuator Housing Block", name_fr="Bloc boîtier actionneur Al 7075-T6", name_es="Bloque carcasa actuador Al 7075-T6", category=Category.STRUCTURES, part_number="PN-ST-AL7075-AH-001", drawing_rev="C", material_spec="Al 7075-T6 AMS4045", program="Multi-Program", uom="Each", unit_cost=4200.0, inspection_interval_days=365, abc_class="B", xyz_class="X", min_order_qty=20, lead_time_days=45, safety_stock_days=14, plant=Plant.KITCHENER_ON),
    SKU(id="ST005", name="4340 Steel Trunnion Forging", name_fr="Forgeage tourillon acier 4340", name_es="Forja muñón acero 4340", category=Category.STRUCTURES, part_number="PN-ST-4340-TR-001", drawing_rev="E", material_spec="4340 AMS6415", program="Multi-Program", uom="Each", unit_cost=12500.0, inspection_interval_days=365, abc_class="A", xyz_class="X", min_order_qty=12, lead_time_days=60, safety_stock_days=21, plant=Plant.LONGUEUIL_QC),
    SKU(id="ST006", name="Ti-10V-2Fe-3Al Beam Forging", name_fr="Forgeage poutre Ti-10V-2Fe-3Al", name_es="Forja viga Ti-10V-2Fe-3Al", category=Category.STRUCTURES, part_number="PN-ST-TI1023-BM-001", drawing_rev="B", material_spec="Ti-10V-2Fe-3Al AMS4984", program="Boeing 777X", uom="Each", unit_cost=42000.0, inspection_interval_days=365, abc_class="A", xyz_class="Y", min_order_qty=6, lead_time_days=110, safety_stock_days=35, plant=Plant.LONGUEUIL_QC),
    SKU(id="ST007", name="Custom 465 MLG Fitting", name_fr="Ferrure train principal Custom 465", name_es="Herraje tren principal Custom 465", category=Category.STRUCTURES, part_number="PN-ST-C465-FT-001", drawing_rev="C", material_spec="Custom 465 AMS5936", program="F-35 JSF", uom="Each", unit_cost=36000.0, inspection_interval_days=180, abc_class="A", xyz_class="Y", min_order_qty=4, lead_time_days=120, safety_stock_days=45, plant=Plant.SPRINGFIELD_OH),
    SKU(id="ST008", name="PH 13-8Mo Actuator Pivot", name_fr="Pivot actionneur PH 13-8Mo", name_es="Pivote actuador PH 13-8Mo", category=Category.STRUCTURES, part_number="PN-ST-PH138-PV-001", drawing_rev="B", material_spec="PH 13-8Mo AMS5629", program="Multi-Program", uom="Each", unit_cost=8200.0, inspection_interval_days=180, abc_class="B", xyz_class="X", min_order_qty=15, lead_time_days=50, safety_stock_days=14, plant=Plant.KITCHENER_ON),
    # MRO Parts (7)
    SKU(id="MR001", name="MLG Seal Kit - Wide Body", name_fr="Kit joints train principal - gros porteur", name_es="Kit sellos tren principal - fuselaje ancho", category=Category.MRO_PARTS, part_number="PN-MR-SEAL-WB-001", drawing_rev="H", material_spec="Viton/PTFE", program="Multi-Program", uom="Kit", unit_cost=2800.0, inspection_interval_days=730, abc_class="A", xyz_class="X", min_order_qty=50, lead_time_days=21, safety_stock_days=14, plant=Plant.LAVAL_QC),
    SKU(id="MR002", name="NLG Bearing Set", name_fr="Ensemble roulements train avant", name_es="Conjunto rodamientos tren delantero", category=Category.MRO_PARTS, part_number="PN-MR-BRG-NL-001", drawing_rev="F", material_spec="52100 Steel", program="Multi-Program", uom="Set", unit_cost=4500.0, inspection_interval_days=365, abc_class="A", xyz_class="X", min_order_qty=30, lead_time_days=28, safety_stock_days=14, plant=Plant.LAVAL_QC),
    SKU(id="MR003", name="Actuator Rod End Assembly", name_fr="Embout de tige actionneur", name_es="Conjunto rótula vástago actuador", category=Category.MRO_PARTS, part_number="PN-MR-ROD-END-001", drawing_rev="D", material_spec="17-4 PH Steel", program="Multi-Program", uom="Each", unit_cost=1200.0, inspection_interval_days=365, abc_class="B", xyz_class="X", min_order_qty=100, lead_time_days=18, safety_stock_days=10, plant=Plant.LAVAL_QC),
    SKU(id="MR004", name="Brake Wear Indicator Pin", name_fr="Broche indicateur d'usure frein", name_es="Pin indicador desgaste freno", category=Category.MRO_PARTS, part_number="PN-MR-BWIP-001", drawing_rev="C", material_spec="Inconel 625", program="Multi-Program", uom="Pack/10", unit_cost=350.0, inspection_interval_days=730, abc_class="B", xyz_class="X", min_order_qty=200, lead_time_days=14, safety_stock_days=7, plant=Plant.LAVAL_QC),
    SKU(id="MR005", name="Hydraulic Filter Element 10μm", name_fr="Élément filtre hydraulique 10μm", name_es="Elemento filtro hidráulico 10μm", category=Category.MRO_PARTS, part_number="PN-MR-HFE-10-001", drawing_rev="E", material_spec="SS 316L Mesh", program="Multi-Program", uom="Each", unit_cost=185.0, inspection_interval_days=180, abc_class="C", xyz_class="X", min_order_qty=500, lead_time_days=10, safety_stock_days=7, plant=Plant.LAVAL_QC),
    SKU(id="MR006", name="Oleo Strut Charge Valve", name_fr="Robinet de charge amortisseur oléo", name_es="Válvula de carga amortiguador oleo", category=Category.MRO_PARTS, part_number="PN-MR-OCV-001", drawing_rev="D", material_spec="Titanium Grade 5", program="Multi-Program", uom="Each", unit_cost=980.0, inspection_interval_days=365, abc_class="B", xyz_class="Y", min_order_qty=40, lead_time_days=21, safety_stock_days=10, plant=Plant.LAVAL_QC),
    SKU(id="MR007", name="Landing Gear Position Sensor", name_fr="Capteur de position train d'atterrissage", name_es="Sensor de posición tren de aterrizaje", category=Category.MRO_PARTS, part_number="PN-MR-LGPS-001", drawing_rev="G", material_spec="Ti/Al housing", program="Multi-Program", uom="Each", unit_cost=3200.0, inspection_interval_days=180, abc_class="A", xyz_class="Y", min_order_qty=20, lead_time_days=35, safety_stock_days=14, plant=Plant.NOTTINGHAM_UK),
    # Raw Materials (5)
    SKU(id="RM001", name="Ti-6Al-4V Round Bar Ø200mm", name_fr="Barre ronde Ti-6Al-4V Ø200mm", name_es="Barra redonda Ti-6Al-4V Ø200mm", category=Category.RAW_MATERIALS, part_number="PN-RM-TI64-RB200", drawing_rev="A", material_spec="Ti-6Al-4V AMS4928", program="Multi-Program", uom="Kg", unit_cost=95.0, inspection_interval_days=730, abc_class="A", xyz_class="X", min_order_qty=500, lead_time_days=60, safety_stock_days=28, plant=Plant.LONGUEUIL_QC),
    SKU(id="RM002", name="300M Steel Billet 250mm sq", name_fr="Billette acier 300M 250mm carré", name_es="Palanquilla acero 300M 250mm cuadrado", category=Category.RAW_MATERIALS, part_number="PN-RM-300M-BIL250", drawing_rev="A", material_spec="300M AMS6419", program="Multi-Program", uom="Kg", unit_cost=38.0, inspection_interval_days=730, abc_class="A", xyz_class="X", min_order_qty=2000, lead_time_days=45, safety_stock_days=21, plant=Plant.LONGUEUIL_QC),
    SKU(id="RM003", name="Inconel 718 Bar Ø150mm", name_fr="Barre Inconel 718 Ø150mm", name_es="Barra Inconel 718 Ø150mm", category=Category.RAW_MATERIALS, part_number="PN-RM-IN718-BAR150", drawing_rev="A", material_spec="Inconel 718 AMS5663", program="Multi-Program", uom="Kg", unit_cost=72.0, inspection_interval_days=730, abc_class="A", xyz_class="X", min_order_qty=300, lead_time_days=55, safety_stock_days=28, plant=Plant.KITCHENER_ON),
    SKU(id="RM004", name="Al 7075-T6 Plate 50mm", name_fr="Plaque Al 7075-T6 50mm", name_es="Placa Al 7075-T6 50mm", category=Category.RAW_MATERIALS, part_number="PN-RM-AL7075-PL50", drawing_rev="A", material_spec="Al 7075-T6 AMS4045", program="Multi-Program", uom="Kg", unit_cost=18.0, inspection_interval_days=730, abc_class="B", xyz_class="X", min_order_qty=1000, lead_time_days=30, safety_stock_days=14, plant=Plant.KITCHENER_ON),
    SKU(id="RM005", name="Custom 465 Stainless Bar", name_fr="Barre inox Custom 465", name_es="Barra inox Custom 465", category=Category.RAW_MATERIALS, part_number="PN-RM-C465-BAR", drawing_rev="A", material_spec="Custom 465 AMS5936", program="F-35 JSF", uom="Kg", unit_cost=125.0, inspection_interval_days=730, abc_class="A", xyz_class="Y", min_order_qty=200, lead_time_days=75, safety_stock_days=35, plant=Plant.SPRINGFIELD_OH),
    # Fasteners & Seals (5)
    SKU(id="FS001", name="Hi-Lok Bolt NAS6204 (Ti)", name_fr="Boulon Hi-Lok NAS6204 (Ti)", name_es="Perno Hi-Lok NAS6204 (Ti)", category=Category.FASTENERS_SEALS, part_number="PN-FS-HILOK-6204", drawing_rev="B", material_spec="Ti-6Al-4V", program="Multi-Program", uom="Pack/100", unit_cost=420.0, inspection_interval_days=730, abc_class="B", xyz_class="X", min_order_qty=50, lead_time_days=14, safety_stock_days=7, plant=Plant.LAVAL_QC),
    SKU(id="FS002", name="AN Fitting MS33656 Hydraulic", name_fr="Raccord AN MS33656 Hydraulique", name_es="Conexión AN MS33656 Hidráulica", category=Category.FASTENERS_SEALS, part_number="PN-FS-AN-MS33656", drawing_rev="C", material_spec="Steel cadmium plated", program="Multi-Program", uom="Pack/25", unit_cost=280.0, inspection_interval_days=730, abc_class="C", xyz_class="X", min_order_qty=100, lead_time_days=10, safety_stock_days=7, plant=Plant.LAVAL_QC),
    SKU(id="FS003", name="Parker O-Ring Kit AS568 (Viton)", name_fr="Kit joints toriques Parker AS568 (Viton)", name_es="Kit juntas tóricas Parker AS568 (Viton)", category=Category.FASTENERS_SEALS, part_number="PN-FS-ORING-AS568", drawing_rev="D", material_spec="Viton FKM", program="Multi-Program", uom="Kit", unit_cost=145.0, inspection_interval_days=365, abc_class="B", xyz_class="X", min_order_qty=200, lead_time_days=7, safety_stock_days=7, plant=Plant.LAVAL_QC),
    SKU(id="FS004", name="NAS1149 Washer Assortment (Steel)", name_fr="Assortiment rondelles NAS1149 (Acier)", name_es="Surtido arandelas NAS1149 (Acero)", category=Category.FASTENERS_SEALS, part_number="PN-FS-NAS1149-WSH", drawing_rev="B", material_spec="Corrosion Resistant Steel", program="Multi-Program", uom="Pack/500", unit_cost=95.0, inspection_interval_days=730, abc_class="C", xyz_class="X", min_order_qty=100, lead_time_days=7, safety_stock_days=7, plant=Plant.LAVAL_QC),
    SKU(id="FS005", name="MS21042 Self-Locking Nut (Inconel)", name_fr="Écrou autobloquant MS21042 (Inconel)", name_es="Tuerca autoblocante MS21042 (Inconel)", category=Category.FASTENERS_SEALS, part_number="PN-FS-MS21042-NUT", drawing_rev="C", material_spec="Inconel 718", program="Multi-Program", uom="Pack/100", unit_cost=380.0, inspection_interval_days=730, abc_class="C", xyz_class="Y", min_order_qty=80, lead_time_days=14, safety_stock_days=7, plant=Plant.LAVAL_QC),
]


# ─── Suppliers (10) ────────────────────────────────────────────────────────

SUPPLIERS: list[Supplier] = [
    Supplier(id="S01", name="Aubert & Duval", name_fr="Aubert & Duval", name_es="Aubert & Duval", country="France", material_types=["Ti-6Al-4V", "300M Steel", "Inconel 718", "Custom 465"], avg_lead_time_days=75, min_lead_time_days=55, max_lead_time_days=110, reliability_score=0.94, current_orders=12, total_capacity_units=8500, quality_score=0.97, last_delivery_date="2026-06-08", payment_terms="Net 60", certifications=["AS9100D", "NADCAP Heat Treat", "NADCAP NDT"]),
    Supplier(id="S02", name="Precision Castparts Corp", name_fr="Precision Castparts Corp", name_es="Precision Castparts Corp", country="USA", material_types=["Inconel 718 Castings", "Ti Forgings", "Structural Castings"], avg_lead_time_days=90, min_lead_time_days=65, max_lead_time_days=130, reliability_score=0.91, current_orders=8, total_capacity_units=5200, quality_score=0.95, last_delivery_date="2026-06-05", payment_terms="Net 45", certifications=["AS9100D", "NADCAP", "Boeing D1-4426"]),
    Supplier(id="S03", name="Magellan Aerospace", name_fr="Magellan Aérospatiale", name_es="Magellan Aerospace", country="Canada", material_types=["Al 7075 Machined Parts", "Complex Assemblies", "Castings"], avg_lead_time_days=55, min_lead_time_days=35, max_lead_time_days=80, reliability_score=0.93, current_orders=15, total_capacity_units=12000, quality_score=0.96, last_delivery_date="2026-06-10", payment_terms="Net 45", certifications=["AS9100D", "NADCAP", "Airbus AIPS"]),
    Supplier(id="S04", name="Safran Landing Systems", name_fr="Safran Systèmes d'Atterrissage", name_es="Safran Sistemas de Aterrizaje", country="France", material_types=["LG Sub-assemblies", "Hydraulic Components", "Brake Systems"], avg_lead_time_days=85, min_lead_time_days=60, max_lead_time_days=120, reliability_score=0.92, current_orders=6, total_capacity_units=3800, quality_score=0.96, last_delivery_date="2026-06-02", payment_terms="Net 60", certifications=["AS9100D", "NADCAP", "EN9100"]),
    Supplier(id="S05", name="Titanium Metals Corp (TIMET)", name_fr="Titanium Metals Corp (TIMET)", name_es="Titanium Metals Corp (TIMET)", country="USA", material_types=["Ti-6Al-4V", "Ti-10V-2Fe-3Al", "Ti-5Al-5V-5Mo-3Cr"], avg_lead_time_days=60, min_lead_time_days=40, max_lead_time_days=95, reliability_score=0.95, current_orders=18, total_capacity_units=25000, quality_score=0.98, last_delivery_date="2026-06-11", payment_terms="Net 30", certifications=["AS9100D", "Boeing BAC5000", "Airbus AIMS"]),
    Supplier(id="S06", name="Howmet Aerospace (Arconic)", name_fr="Howmet Aerospace (Arconic)", name_es="Howmet Aerospace (Arconic)", country="USA", material_types=["Al 7075 Plate", "Al 2024", "Ti Forgings"], avg_lead_time_days=45, min_lead_time_days=28, max_lead_time_days=70, reliability_score=0.96, current_orders=22, total_capacity_units=35000, quality_score=0.97, last_delivery_date="2026-06-12", payment_terms="Net 30", certifications=["AS9100D", "NADCAP", "AMS Approved"]),
    Supplier(id="S07", name="Carpenter Technology", name_fr="Carpenter Technology", name_es="Carpenter Technology", country="USA", material_types=["Custom 465", "15-5 PH", "300M", "PH 13-8Mo"], avg_lead_time_days=50, min_lead_time_days=35, max_lead_time_days=80, reliability_score=0.93, current_orders=14, total_capacity_units=18000, quality_score=0.96, last_delivery_date="2026-06-09", payment_terms="Net 45", certifications=["AS9100D", "NADCAP Heat Treat"]),
    Supplier(id="S08", name="Parker Hannifin Aerospace", name_fr="Parker Hannifin Aérospatiale", name_es="Parker Hannifin Aeroespacial", country="USA", material_types=["Hydraulic Valves", "Seals", "Actuator Components", "Filters"], avg_lead_time_days=35, min_lead_time_days=18, max_lead_time_days=55, reliability_score=0.97, current_orders=25, total_capacity_units=50000, quality_score=0.98, last_delivery_date="2026-06-12", payment_terms="Net 30", certifications=["AS9100D", "NADCAP"]),
    Supplier(id="S09", name="Moog Inc.", name_fr="Moog Inc.", name_es="Moog Inc.", country="USA", material_types=["Servo Valves", "Actuator Assemblies", "Flight Control Components"], avg_lead_time_days=70, min_lead_time_days=50, max_lead_time_days=100, reliability_score=0.94, current_orders=9, total_capacity_units=6000, quality_score=0.97, last_delivery_date="2026-06-07", payment_terms="Net 45", certifications=["AS9100D", "NADCAP", "MIL-STD"]),
    Supplier(id="S10", name="Lisi Aerospace", name_fr="Lisi Aérospatiale", name_es="Lisi Aeroespacial", country="France", material_types=["Hi-Lok Fasteners", "Titanium Bolts", "Specialty Nuts", "Bushings"], avg_lead_time_days=25, min_lead_time_days=12, max_lead_time_days=40, reliability_score=0.96, current_orders=30, total_capacity_units=100000, quality_score=0.99, last_delivery_date="2026-06-13", payment_terms="Net 30", certifications=["AS9100D", "EN9100", "Airbus Approved"]),
]


# ─── Production Lines (8) ──────────────────────────────────────────────────

PRODUCTION_LINES: list[ProductionLine] = [
    ProductionLine(id="PL01", plant=Plant.LONGUEUIL_QC, line_name="LG Assembly Cell A", product_categories=[Category.LANDING_GEAR, Category.STRUCTURES], capacity_units_per_day=3, current_utilization_pct=87, planned_maintenance=["2026-06-20"], current_sku="LG001", shift_pattern="3-shift 24/7"),
    ProductionLine(id="PL02", plant=Plant.LONGUEUIL_QC, line_name="CNC Machining Center B", product_categories=[Category.STRUCTURES, Category.HYDRAULICS], capacity_units_per_day=12, current_utilization_pct=92, planned_maintenance=[], current_sku="ST001", shift_pattern="2-shift"),
    ProductionLine(id="PL03", plant=Plant.KITCHENER_ON, line_name="Actuation Assembly Line", product_categories=[Category.ACTUATION, Category.HYDRAULICS], capacity_units_per_day=8, current_utilization_pct=78, planned_maintenance=["2026-06-25"], current_sku="AC001", shift_pattern="2-shift"),
    ProductionLine(id="PL04", plant=Plant.SPRINGFIELD_OH, line_name="Military LG Cell", product_categories=[Category.LANDING_GEAR, Category.STRUCTURES], capacity_units_per_day=4, current_utilization_pct=95, planned_maintenance=[], current_sku="LG003", shift_pattern="3-shift 24/7"),
    ProductionLine(id="PL05", plant=Plant.LAVAL_QC, line_name="MRO Overhaul Bay", product_categories=[Category.MRO_PARTS, Category.HYDRAULICS], capacity_units_per_day=15, current_utilization_pct=68, planned_maintenance=["2026-07-01"], current_sku="MR001", shift_pattern="Day shift"),
    ProductionLine(id="PL06", plant=Plant.NOTTINGHAM_UK, line_name="Sensor & Avionics Assembly", product_categories=[Category.MRO_PARTS, Category.ACTUATION], capacity_units_per_day=20, current_utilization_pct=72, planned_maintenance=[], current_sku="MR007", shift_pattern="2-shift"),
    ProductionLine(id="PL07", plant=Plant.GETAFE_MADRID, line_name="CESA Actuator Line", product_categories=[Category.ACTUATION, Category.HYDRAULICS], capacity_units_per_day=10, current_utilization_pct=84, planned_maintenance=["2026-06-18"], current_sku="AC007", shift_pattern="2-shift"),
    ProductionLine(id="PL08", plant=Plant.LIVONIA_MI, line_name="Heat Treat & Surface Finishing", product_categories=[Category.STRUCTURES, Category.RAW_MATERIALS], capacity_units_per_day=25, current_utilization_pct=81, planned_maintenance=[], current_sku=None, shift_pattern="3-shift 24/7"),
]


# ─── Purchase Orders (15) ──────────────────────────────────────────────────

PURCHASE_ORDERS: list[PurchaseOrder] = [
    PurchaseOrder(id="PO-2026-001", supplier_id="S01", supplier_name="Aubert & Duval", sku_id="ST001", sku_name="Ti-6Al-4V MLG Forging Blank", qty=50, unit_price=28000.0, currency="CAD", contract_id="CTR-001", order_date="2026-05-15", expected_delivery="2026-08-10", status="confirmed", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-002", supplier_id="S01", supplier_name="Aubert & Duval", sku_id="ST002", sku_name="300M Shock Strut Forging", qty=25, unit_price=34500.0, currency="CAD", contract_id="CTR-001", order_date="2026-05-20", expected_delivery="2026-08-25", status="confirmed", delay_days=0, validation_status="warning", validation_flags=["price_above_contract"]),
    PurchaseOrder(id="PO-2026-003", supplier_id="S02", supplier_name="Precision Castparts Corp", sku_id="ST003", sku_name="Inconel 718 Brake Housing Casting", qty=10, unit_price=18500.0, currency="CAD", contract_id="CTR-002", order_date="2026-04-28", expected_delivery="2026-07-20", status="in_transit", delay_days=5, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-004", supplier_id="S05", supplier_name="Titanium Metals Corp (TIMET)", sku_id="RM001", sku_name="Ti-6Al-4V Round Bar Ø200mm", qty=2000, unit_price=97.0, currency="CAD", contract_id=None, order_date="2026-05-01", expected_delivery="2026-07-01", status="in_transit", delay_days=0, validation_status="failed", validation_flags=["no_contract", "exceeds_budget"]),
    PurchaseOrder(id="PO-2026-005", supplier_id="S03", supplier_name="Magellan Aerospace", sku_id="ST004", sku_name="Al 7075-T6 Actuator Housing Block", qty=30, unit_price=4350.0, currency="CAD", contract_id="CTR-003", order_date="2026-06-01", expected_delivery="2026-07-15", status="confirmed", delay_days=0, validation_status="warning", validation_flags=["price_above_contract"]),
    PurchaseOrder(id="PO-2026-006", supplier_id="S08", supplier_name="Parker Hannifin Aerospace", sku_id="MR005", sku_name="Hydraulic Filter Element 10μm", qty=500, unit_price=185.0, currency="CAD", contract_id=None, order_date="2026-06-05", expected_delivery="2026-06-20", status="confirmed", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-007", supplier_id="S10", supplier_name="Lisi Aerospace", sku_id="FS001", sku_name="Hi-Lok Bolt NAS6204 (Ti)", qty=100, unit_price=420.0, currency="CAD", contract_id=None, order_date="2026-06-02", expected_delivery="2026-06-18", status="delivered", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-008", supplier_id="S06", supplier_name="Howmet Aerospace (Arconic)", sku_id="RM004", sku_name="Al 7075-T6 Plate 50mm", qty=1500, unit_price=18.5, currency="CAD", contract_id=None, order_date="2026-05-25", expected_delivery="2026-06-28", status="in_transit", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-009", supplier_id="S07", supplier_name="Carpenter Technology", sku_id="RM005", sku_name="Custom 465 Stainless Bar", qty=200, unit_price=128.0, currency="CAD", contract_id=None, order_date="2026-05-10", expected_delivery="2026-07-25", status="confirmed", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-010", supplier_id="S04", supplier_name="Safran Landing Systems", sku_id="HY002", sku_name="A350 NLG Steering Servo Valve", qty=15, unit_price=15500.0, currency="CAD", contract_id=None, order_date="2026-05-18", expected_delivery="2026-07-30", status="confirmed", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-011", supplier_id="S09", supplier_name="Moog Inc.", sku_id="AC005", sku_name="Global 7500 Thrust Reverser Actuator", qty=4, unit_price=88000.0, currency="CAD", contract_id=None, order_date="2026-04-20", expected_delivery="2026-07-10", status="in_transit", delay_days=8, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-012", supplier_id="S02", supplier_name="Precision Castparts Corp", sku_id="LG002", sku_name="A350 NLG Cylinder", qty=6, unit_price=94000.0, currency="CAD", contract_id="CTR-002", order_date="2026-06-10", expected_delivery="2026-09-15", status="confirmed", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-013", supplier_id="S01", supplier_name="Aubert & Duval", sku_id="RM002", sku_name="300M Steel Billet 250mm sq", qty=3000, unit_price=39.0, currency="CAD", contract_id="CTR-001", order_date="2026-06-08", expected_delivery="2026-07-25", status="confirmed", delay_days=0, validation_status="passed", validation_flags=[]),
    PurchaseOrder(id="PO-2026-014", supplier_id="S05", supplier_name="Titanium Metals Corp (TIMET)", sku_id="RM001", sku_name="Ti-6Al-4V Round Bar Ø200mm", qty=800, unit_price=96.0, currency="CAD", contract_id=None, order_date="2026-06-12", expected_delivery="2026-08-12", status="pending", delay_days=0, validation_status="pending", validation_flags=[]),
    PurchaseOrder(id="PO-2026-015", supplier_id="S03", supplier_name="Magellan Aerospace", sku_id="AC004", sku_name="A220 Slat Actuator LVDT Module", qty=12, unit_price=19200.0, currency="CAD", contract_id="CTR-003", order_date="2026-06-11", expected_delivery="2026-08-05", status="pending", delay_days=0, validation_status="pending", validation_flags=[]),
]


# ─── Generated Data Functions ──────────────────────────────────────────────

def _generate_inventory() -> list[InventoryPosition]:
    positions = []
    warehouses = {
        Plant.LONGUEUIL_QC: "Longueuil Main Warehouse",
        Plant.KITCHENER_ON: "Kitchener Storage",
        Plant.SPRINGFIELD_OH: "Springfield Secure Store",
        Plant.NOTTINGHAM_UK: "Nottingham Facility",
        Plant.LAVAL_QC: "Laval MRO Stores",
        Plant.LIVONIA_MI: "Livonia Raw Materials",
        Plant.GETAFE_MADRID: "CESA Getafe",
        Plant.SEVILLE_SPAIN: "Seville Facility",
    }
    for sku in SKUS:
        stock = random.uniform(sku.min_order_qty * 0.5, sku.min_order_qty * 4)
        allocated = stock * random.uniform(0.2, 0.6)
        in_transit = random.uniform(0, sku.min_order_qty * 1.5)
        dos = random.uniform(5, 90)
        if dos < 15:
            risk = RiskLevel.CRITICAL
        elif dos < 30:
            risk = RiskLevel.WARNING
        elif dos > 120:
            risk = RiskLevel.EXCESS
        else:
            risk = RiskLevel.NORMAL
        cert_remaining = random.uniform(25, 100)
        positions.append(InventoryPosition(
            sku_id=sku.id,
            sku_name=sku.name,
            category=sku.category,
            warehouse=warehouses.get(sku.plant, "General Storage"),
            current_stock=round(stock, 1),
            allocated_stock=round(allocated, 1),
            available_stock=round(stock - allocated, 1),
            in_transit=round(in_transit, 1),
            days_of_supply=round(dos, 1),
            risk_level=risk,
            last_receipt_date="2026-06-01",
            next_expected_receipt="2026-07-01",
            batch_age_days=random.randint(5, 180),
            cert_expiry_remaining_pct=round(cert_remaining, 1),
        ))
    return positions


INVENTORY: list[InventoryPosition] = _generate_inventory()


def _generate_demand() -> tuple[list[DemandRecord], list[DemandForecast]]:
    history: list[DemandRecord] = []
    forecasts: list[DemandForecast] = []
    channels = list(Channel)
    regions = [Region.NORTH_AMERICA, Region.EUROPE, Region.ASIA_PACIFIC]
    programs_events = {
        "Boeing 777X": "Rate increase to 5/month",
        "Airbus A350": "Stable rate 6/month",
        "F-35 JSF": "Lot 18 ramp-up",
        "Airbus A220": "Rate increase to 14/month",
        "Boeing 737 MAX": "Post-grounding recovery",
        "Multi-Program": "",
    }
    base_date = date(2026, 6, 13)
    for sku in SKUS[:25]:
        base_qty = sku.min_order_qty * random.uniform(4.0, 12.0)
        channel = random.choice(channels)
        region = random.choice(regions)
        program_flag = sku.program in ["Boeing 777X", "Airbus A220", "F-35 JSF"]
        event = programs_events.get(sku.program, "")
        for w in range(12):
            week_date = base_date - timedelta(weeks=12 - w)
            seasonal = 1.0 + 0.1 * math.sin(w * math.pi / 6)
            actual = base_qty * seasonal * random.uniform(0.85, 1.15)
            forecast = base_qty * seasonal * random.uniform(0.92, 1.08)
            history.append(DemandRecord(
                sku_id=sku.id,
                week=week_date.isoformat(),
                channel=channel,
                region=region,
                actual_qty=round(actual, 1),
                forecast_qty=round(forecast, 1),
                program_change_flag=program_flag and w > 8,
                event_flag=event if w > 8 and program_flag else "",
            ))
        for w in range(8):
            week_date = base_date + timedelta(weeks=w + 1)
            seasonal = 1.0 + 0.1 * math.sin((12 + w) * math.pi / 6)
            point = base_qty * seasonal * (1.05 if program_flag else 1.0)
            forecasts.append(DemandForecast(
                sku_id=sku.id,
                sku_name=sku.name,
                week=week_date.isoformat(),
                channel=channel,
                region=region,
                point_forecast=round(point, 1),
                lower_80=round(point * 0.88, 1),
                upper_80=round(point * 1.12, 1),
                lower_95=round(point * 0.78, 1),
                upper_95=round(point * 1.22, 1),
                confidence="high" if w < 4 else "medium",
                drivers=["OEM rate change", "Program schedule"] if program_flag else ["Baseline demand"],
            ))
    return history, forecasts


DEMAND_HISTORY, DEMAND_FORECASTS = _generate_demand()


# ─── Supply Alerts ─────────────────────────────────────────────────────────

SUPPLY_ALERTS: list[SupplyAlert] = [
    SupplyAlert(id="ALT-001", sku_id="RM001", sku_name="Ti-6Al-4V Round Bar Ø200mm", alert_type="supply_shortage", severity="critical", title="Ti-6Al-4V allocation cut 20%", description="TIMET has notified a 20% allocation reduction on Ti-6Al-4V bar for Q3 2026 due to sponge shortage. Affects MLG forging programs.", date="2026-06-12", plant="Longueuil, Quebec", recommended_action="Activate Aubert & Duval alternate source. Expedite PO-2026-004."),
    SupplyAlert(id="ALT-002", sku_id="LG003", sku_name="F-35 MLG Side Brace", alert_type="quality_hold", severity="critical", title="NDT indication on F-35 MLG batch", description="UT inspection found sub-surface indication on 2 of 8 F-35 MLG side braces (batch BT-2026-F35-004). DCMA hold pending MRB disposition.", date="2026-06-11", plant="Springfield, Ohio", recommended_action="Segregate affected parts. Initiate MRB review. Check if rework per DWG note 14 is acceptable."),
    SupplyAlert(id="ALT-003", sku_id="AC007", sku_name="CESA A320 Horizontal Stab Actuator", alert_type="delivery_delay", severity="warning", title="CESA Getafe line maintenance overrun", description="Planned 2-day maintenance on CESA actuator line extending to 5 days due to spindle replacement. 12 A320 actuators will be 3 days late.", date="2026-06-13", plant="Getafe/Madrid, Spain (CESA)", recommended_action="Notify Airbus Hamburg of revised delivery. Pull forward Seville capacity if A330 door actuators can wait."),
    SupplyAlert(id="ALT-004", sku_id="ST006", sku_name="Ti-10V-2Fe-3Al Beam Forging", alert_type="cert_expiry", severity="warning", title="NADCAP heat treat cert renewal due", description="Longueuil heat treat NADCAP certification expires 2026-08-15. Audit scheduled 2026-07-20. If delayed, cannot ship Ti-10V forgings to Boeing.", date="2026-06-10", plant="Longueuil, Quebec", recommended_action="Confirm NADCAP audit date. Prepare documentation package. Pre-position 2 months of Ti-10V inventory."),
    SupplyAlert(id="ALT-005", sku_id="LG001", sku_name="777X MLG Shock Strut Assy", alert_type="demand_spike", severity="warning", title="Boeing 777X rate increase confirmation", description="Boeing confirmed 777X production rate increase from 3/month to 5/month starting Sept 2026. Requires 67% increase in MLG deliveries.", date="2026-06-09", plant="Longueuil, Quebec", recommended_action="Assess capacity on LG Assembly Cell A. May need to add 3rd shift weekend coverage. Order additional Ti-6Al-4V."),
    SupplyAlert(id="ALT-006", sku_id="HY003", sku_name="F-35 Brake Hydraulic Module", alert_type="supplier_risk", severity="warning", title="PCC capacity constraint on Inconel castings", description="Precision Castparts reports 3-week extension on all Inconel 718 casting deliveries due to furnace rebuild. Affects brake housings for F-35 program.", date="2026-06-08", plant="Springfield, Ohio", recommended_action="Evaluate safety stock coverage. Contact Howmet for alternate casting source qualification."),
    SupplyAlert(id="ALT-007", sku_id=None, sku_name="General", alert_type="logistics", severity="info", title="Port of Montreal labor action", description="CUPE Local 375 has filed 72-hour strike notice for Port of Montreal starting June 20. May affect European material shipments.", date="2026-06-13", plant="Longueuil, Quebec", recommended_action="Reroute urgent European shipments through Halifax. Prioritize Aubert & Duval Ti-6Al-4V and Lisi fastener orders."),
    SupplyAlert(id="ALT-008", sku_id="MR001", sku_name="MLG Seal Kit - Wide Body", alert_type="inventory_excess", severity="info", title="Excess seal kit inventory at Laval", description="Wide-body seal kit inventory at 180 DOS (target 14). Driven by cancelled MRO work order from Air Canada.", date="2026-06-07", plant="Laval, Quebec", recommended_action="Defer next PO. Offer surplus to Safran MRO network or transfer to Nottingham for EU aftermarket."),
]


# ─── Replenishment Actions ─────────────────────────────────────────────────

REPLENISHMENT_ACTIONS: list[ReplenishmentAction] = [
    ReplenishmentAction(id="RA-001", action_type="emergency_order", sku_id="RM001", sku_name="Ti-6Al-4V Round Bar Ø200mm", recommended_qty=800, supplier_id="S01", plant=Plant.LONGUEUIL_QC, urgency="critical", rationale="TIMET allocation cut requires alternate source. Aubert & Duval has 800kg available in Pamiers warehouse.", kpi_impact={"dos_improvement": 18, "cost_premium_pct": 8}, confidence="high", scenario="ti64_shortage_mitigation"),
    ReplenishmentAction(id="RA-002", action_type="expedite", sku_id="ST003", sku_name="Inconel 718 Brake Housing Casting", recommended_qty=10, supplier_id="S02", plant=Plant.KITCHENER_ON, urgency="high", rationale="PO-2026-003 delayed 5 days. Expedite via air freight to avoid F-35 brake module line stoppage.", kpi_impact={"dos_improvement": 12, "freight_premium_cad": 15000}, confidence="high", scenario="pcc_delay_recovery"),
    ReplenishmentAction(id="RA-003", action_type="safety_stock_increase", sku_id="LG001", sku_name="777X MLG Shock Strut Assy", recommended_qty=4, supplier_id=None, plant=Plant.LONGUEUIL_QC, urgency="high", rationale="777X rate increase to 5/mo confirmed. Current safety stock of 45 days insufficient at new rate. Recommend 60 days.", kpi_impact={"dos_improvement": 15, "working_capital_increase_mm": 0.74}, confidence="medium", scenario="777x_rate_increase"),
    ReplenishmentAction(id="RA-004", action_type="internal_transfer", sku_id="MR001", sku_name="MLG Seal Kit - Wide Body", recommended_qty=200, supplier_id=None, plant=Plant.NOTTINGHAM_UK, urgency="low", rationale="Transfer excess Laval seal kits to Nottingham for EU aftermarket demand. Reduces excess from 180 to 60 DOS.", kpi_impact={"dos_reduction_laval": 120, "revenue_opportunity_cad": 56000}, confidence="high", scenario="inventory_rebalance"),
    ReplenishmentAction(id="RA-005", action_type="new_order", sku_id="RM005", sku_name="Custom 465 Stainless Bar", recommended_qty=300, supplier_id="S07", plant=Plant.SPRINGFIELD_OH, urgency="medium", rationale="F-35 Lot 18 ramp-up will increase Custom 465 consumption 40%. Place order now for Sept delivery.", kpi_impact={"dos_improvement": 25, "lot_18_readiness_pct": 95}, confidence="medium", scenario="f35_lot18_prep"),
]


# ─── KPI Metrics ───────────────────────────────────────────────────────────

KPI: KPIMetrics = KPIMetrics(
    forecast_accuracy_mape=6.8,
    inventory_dos=42.5,
    fill_rate=96.2,
    stockout_rate=1.8,
    obsolescence_rate=0.3,
    working_capital_mm=187.4,
    production_utilization=84.6,
    on_time_delivery=94.1,
    labor_utilization_pct=86.3,
    contract_compliance_pct=91.5,
    alerts_open=8,
    pending_actions=5,
)


# ─── Supplier Details ──────────────────────────────────────────────────────

SUPPLIER_CONTACTS: list[SupplierContact] = [
    SupplierContact(supplier_id="S01", name="Jean-Pierre Moreau", role="Key Account Manager", email="jp.moreau@aubertduval.fr", phone="+33 4 71 29 6000"),
    SupplierContact(supplier_id="S02", name="Mike Henderson", role="Aerospace Sales Director", email="m.henderson@precast.com", phone="+1 503 946 4800"),
    SupplierContact(supplier_id="S03", name="Sarah Blackwood", role="Program Manager", email="s.blackwood@magellan.aero", phone="+1 905 677 1889"),
    SupplierContact(supplier_id="S05", name="Robert Chen", role="Titanium Sales Manager", email="r.chen@timet.com", phone="+1 972 233 1700"),
    SupplierContact(supplier_id="S08", name="Jennifer Walsh", role="Aftermarket Director", email="j.walsh@parker.com", phone="+1 216 896 3000"),
]

SUPPLIER_PERFORMANCE: list[SupplierPerformanceRecord] = []
for sup in SUPPLIERS:
    for m in range(6):
        month_date = date(2026, 6, 1) - timedelta(days=30 * m)
        SUPPLIER_PERFORMANCE.append(SupplierPerformanceRecord(
            supplier_id=sup.id,
            month=month_date.strftime("%Y-%m"),
            on_time_delivery_pct=round(sup.reliability_score * 100 + random.uniform(-4, 3), 1),
            quality_pass_rate=round(sup.quality_score * 100 + random.uniform(-2, 1), 1),
            avg_lead_time_days=sup.avg_lead_time_days + random.randint(-5, 8),
            incidents=random.randint(0, 2),
        ))

SUPPLIER_CERTIFICATIONS: list[SupplierCertification] = [
    SupplierCertification(supplier_id="S01", name="AS9100 Rev D", status="active", expiry_date="2027-09-15", issuing_body="Bureau Veritas"),
    SupplierCertification(supplier_id="S01", name="NADCAP Heat Treat", status="active", expiry_date="2027-03-20", issuing_body="PRI/Nadcap"),
    SupplierCertification(supplier_id="S02", name="AS9100 Rev D", status="active", expiry_date="2027-11-01", issuing_body="SAI Global"),
    SupplierCertification(supplier_id="S02", name="NADCAP Special Processes", status="active", expiry_date="2026-12-15", issuing_body="PRI/Nadcap"),
    SupplierCertification(supplier_id="S03", name="AS9100 Rev D", status="active", expiry_date="2027-06-30", issuing_body="QMI-SAI"),
    SupplierCertification(supplier_id="S05", name="AS9100 Rev D", status="active", expiry_date="2028-01-15", issuing_body="NSF-ISR"),
    SupplierCertification(supplier_id="S05", name="Boeing BAC5000", status="active", expiry_date="2027-04-10", issuing_body="Boeing"),
    SupplierCertification(supplier_id="S08", name="AS9100 Rev D", status="active", expiry_date="2027-08-22", issuing_body="BSI"),
    SupplierCertification(supplier_id="S10", name="EN9100", status="active", expiry_date="2027-12-01", issuing_body="AFAQ/AFNOR"),
]

ALTERNATIVE_SUPPLIERS: list[AlternativeSupplier] = [
    AlternativeSupplier(sku_id="RM001", supplier_id="S01", supplier_name="Aubert & Duval", lead_time_days=80, unit_cost_premium_pct=8.0, min_order_qty=400, notes="Pamiers facility. Qualified alternate for Ti-6Al-4V bar per Boeing spec."),
    AlternativeSupplier(sku_id="RM001", supplier_id="S06", supplier_name="Howmet Aerospace (Arconic)", lead_time_days=65, unit_cost_premium_pct=5.0, min_order_qty=600, notes="Niles, OH facility. AMS4928 qualified."),
    AlternativeSupplier(sku_id="ST003", supplier_id="S06", supplier_name="Howmet Aerospace (Arconic)", lead_time_days=80, unit_cost_premium_pct=12.0, min_order_qty=8, notes="Hampton casting facility. Needs 6-month qual program for F-35."),
    AlternativeSupplier(sku_id="RM005", supplier_id="S01", supplier_name="Aubert & Duval", lead_time_days=85, unit_cost_premium_pct=15.0, min_order_qty=150, notes="Les Ancizes. Custom 465 available but longer lead due to EU source."),
    AlternativeSupplier(sku_id="AC001", supplier_id="S09", supplier_name="Moog Inc.", lead_time_days=95, unit_cost_premium_pct=10.0, min_order_qty=2, notes="Salt Lake City. Sub-assembly only, final test at Kitchener."),
]


# ─── Quality & Maintenance ─────────────────────────────────────────────────

QUALITY_RESULTS: list[QualityTestResult] = [
    QualityTestResult(sku_id="LG001", batch_id="BT-2026-777X-001", test_date="2026-06-10", dimensional_check="pass", ndt_result="pass", material_cert_status="valid", overall_result="pass", inspector="Marc Tremblay"),
    QualityTestResult(sku_id="LG003", batch_id="BT-2026-F35-004", test_date="2026-06-11", dimensional_check="pass", ndt_result="fail", material_cert_status="valid", overall_result="fail", inspector="David Miller"),
    QualityTestResult(sku_id="ST001", batch_id="BT-2026-TI64-012", test_date="2026-06-09", dimensional_check="pass", ndt_result="pass", material_cert_status="valid", overall_result="pass", inspector="Sylvie Dupont"),
    QualityTestResult(sku_id="AC007", batch_id="BT-2026-CESA-008", test_date="2026-06-08", dimensional_check="pass", ndt_result="pass", material_cert_status="valid", overall_result="pass", inspector="Carlos Ruiz"),
    QualityTestResult(sku_id="HY001", batch_id="BT-2026-HYD-003", test_date="2026-06-12", dimensional_check="marginal", ndt_result="pass", material_cert_status="valid", overall_result="pass", inspector="Marc Tremblay"),
    QualityTestResult(sku_id="ST002", batch_id="BT-2026-300M-007", test_date="2026-06-07", dimensional_check="pass", ndt_result="pass", material_cert_status="valid", overall_result="pass", inspector="Luc Bergeron"),
    QualityTestResult(sku_id="LG005", batch_id="BT-2026-737M-002", test_date="2026-06-06", dimensional_check="pass", ndt_result="pass", material_cert_status="valid", overall_result="pass", inspector="Sylvie Dupont"),
    QualityTestResult(sku_id="RM001", batch_id="BT-2026-TI64-RAW-015", test_date="2026-06-11", dimensional_check="pass", ndt_result="pass", material_cert_status="expiring_soon", overall_result="pass", inspector="Luc Bergeron"),
]

MAINTENANCE_EVENTS: list[MaintenanceEvent] = [
    MaintenanceEvent(line_id="PL01", date="2026-05-28", duration_hours=8.0, type="preventive", root_cause="Scheduled 500-hour spindle service", cost_cad=12500.0),
    MaintenanceEvent(line_id="PL02", date="2026-06-03", duration_hours=4.0, type="corrective", root_cause="Coolant pump seal failure", cost_cad=4800.0),
    MaintenanceEvent(line_id="PL04", date="2026-05-15", duration_hours=16.0, type="preventive", root_cause="Annual CNC calibration and laser alignment", cost_cad=28000.0),
    MaintenanceEvent(line_id="PL07", date="2026-06-13", duration_hours=40.0, type="corrective", root_cause="Main spindle bearing replacement (unplanned)", cost_cad=65000.0),
    MaintenanceEvent(line_id="PL05", date="2026-06-01", duration_hours=6.0, type="preventive", root_cause="Hydraulic test bench recalibration", cost_cad=8500.0),
    MaintenanceEvent(line_id="PL08", date="2026-05-20", duration_hours=24.0, type="preventive", root_cause="Vacuum furnace element replacement", cost_cad=42000.0),
]


def _generate_production_runs() -> list[ProductionRun]:
    runs = []
    base = date(2026, 6, 13)
    shifts = ["Day", "Afternoon", "Night"]
    for line in PRODUCTION_LINES:
        if not line.current_sku:
            continue
        for d in range(14):
            run_date = base - timedelta(days=d)
            for s_idx, shift in enumerate(shifts[:2]):
                planned = line.capacity_units_per_day / 2
                actual = planned * random.uniform(0.82, 1.02)
                yield_pct = random.uniform(94, 99.5)
                scrap_pct = random.uniform(0.5, 4.0)
                runs.append(ProductionRun(
                    line_id=line.id,
                    sku_id=line.current_sku,
                    date=run_date.isoformat(),
                    planned_qty=round(planned, 1),
                    actual_qty=round(actual, 1),
                    yield_pct=round(yield_pct, 1),
                    scrap_pct=round(scrap_pct, 1),
                    shift=shift,
                ))
    return runs


PRODUCTION_RUNS: list[ProductionRun] = _generate_production_runs()


# ─── Contracts ────────────────────────────────────────────────────────────────

CONTRACTS: list[Contract] = [
    Contract(id="CTR-001", supplier_id="S01", supplier_name="Aubert & Duval", part_numbers=["PN-TI64-FRG-001", "PN-TI64-FRG-002"], negotiated_prices={"PN-TI64-FRG-001": 4500.00, "PN-TI64-FRG-002": 6200.00}, escalation_pct_annual=2.5, effective_date="2025-01-01", expiry_date="2027-12-31", currency="CAD", status="active"),
    Contract(id="CTR-002", supplier_id="S02", supplier_name="Precision Castparts", part_numbers=["PN-INCO718-CST-001"], negotiated_prices={"PN-INCO718-CST-001": 12800.00}, escalation_pct_annual=3.0, effective_date="2025-04-01", expiry_date="2027-03-31", currency="CAD", status="active"),
    Contract(id="CTR-003", supplier_id="S03", supplier_name="Magellan Aerospace", part_numbers=["PN-AL7075-MCH-001", "PN-AL7075-MCH-002"], negotiated_prices={"PN-AL7075-MCH-001": 2100.00, "PN-AL7075-MCH-002": 3400.00}, escalation_pct_annual=2.0, effective_date="2024-07-01", expiry_date="2026-06-30", currency="CAD", status="active"),
]


# ─── Contract Price Validations ───────────────────────────────────────────────

CONTRACT_VALIDATIONS: list[ContractPriceValidation] = [
    ContractPriceValidation(po_id="PO-2026-001", contract_id="CTR-001", part_number="PN-TI64-FRG-001", contract_ceiling=4500.00, po_unit_price=4480.00, variance_pct=-0.4, status="compliant"),
    ContractPriceValidation(po_id="PO-2026-002", contract_id="CTR-001", part_number="PN-TI64-FRG-002", contract_ceiling=6200.00, po_unit_price=6450.00, variance_pct=4.0, status="over_ceiling"),
    ContractPriceValidation(po_id="PO-2026-003", contract_id="CTR-002", part_number="PN-INCO718-CST-001", contract_ceiling=12800.00, po_unit_price=12750.00, variance_pct=-0.4, status="compliant"),
    ContractPriceValidation(po_id="PO-2026-004", contract_id=None, part_number="PN-SS304-TUB-001", contract_ceiling=None, po_unit_price=890.00, variance_pct=0.0, status="no_contract"),
    ContractPriceValidation(po_id="PO-2026-005", contract_id="CTR-003", part_number="PN-AL7075-MCH-001", contract_ceiling=2100.00, po_unit_price=2250.00, variance_pct=7.1, status="over_ceiling"),
]


# ─── PO Validations ──────────────────────────────────────────────────────────

PO_VALIDATIONS: list[POValidationResult] = [
    POValidationResult(po_id="PO-2026-001", status="passed", checks=[
        {"check": "qty_within_range", "result": "pass", "detail": "Qty 50 within contract MOQ 10 and max 200"},
        {"check": "lead_time_feasible", "result": "pass", "detail": "45 days lead time meets 60 day need date"},
        {"check": "duplicate_check", "result": "pass", "detail": "No duplicate PO found"},
        {"check": "budget_compliance", "result": "pass", "detail": "Within quarterly budget allocation"},
    ]),
    POValidationResult(po_id="PO-2026-002", status="warning", checks=[
        {"check": "qty_within_range", "result": "pass", "detail": "Qty 25 within range"},
        {"check": "lead_time_feasible", "result": "warning", "detail": "Lead time 55 days tight for 60 day need date"},
        {"check": "duplicate_check", "result": "pass", "detail": "No duplicate PO found"},
        {"check": "budget_compliance", "result": "pass", "detail": "Within quarterly budget allocation"},
    ]),
    POValidationResult(po_id="PO-2026-003", status="passed", checks=[
        {"check": "qty_within_range", "result": "pass", "detail": "Qty 10 within range"},
        {"check": "lead_time_feasible", "result": "pass", "detail": "30 days lead time meets 90 day need date"},
        {"check": "duplicate_check", "result": "pass", "detail": "No duplicate PO found"},
        {"check": "budget_compliance", "result": "pass", "detail": "Within quarterly budget allocation"},
    ]),
    POValidationResult(po_id="PO-2026-004", status="failed", checks=[
        {"check": "qty_within_range", "result": "pass", "detail": "Qty 100 within range"},
        {"check": "lead_time_feasible", "result": "fail", "detail": "Lead time 90 days exceeds 45 day need date"},
        {"check": "duplicate_check", "result": "warning", "detail": "Similar PO PO-2026-001 placed last week"},
        {"check": "budget_compliance", "result": "fail", "detail": "Exceeds remaining quarterly budget by 15%"},
    ]),
    POValidationResult(po_id="PO-2026-005", status="warning", checks=[
        {"check": "qty_within_range", "result": "pass", "detail": "Qty 30 within range"},
        {"check": "lead_time_feasible", "result": "pass", "detail": "40 days lead time meets 75 day need date"},
        {"check": "duplicate_check", "result": "pass", "detail": "No duplicate PO found"},
        {"check": "budget_compliance", "result": "warning", "detail": "Within 5% of quarterly budget limit"},
    ]),
]


# ─── Daily Labor Records ─────────────────────────────────────────────────────

def _generate_daily_labor() -> list[DailyLaborRecord]:
    facilities = ["Longueuil, Quebec", "Kitchener, Ontario", "Springfield, Ohio", "Nottingham, UK", "Laval, Quebec", "Livonia, Michigan", "Getafe/Madrid, Spain (CESA)", "Seville, Spain"]
    shifts = ["Day", "Afternoon", "Night"]
    skill_categories = ["Machinist", "Assembly", "NDT Inspector", "Welder", "Heat Treat", "Quality"]
    records = []
    today = date(2026, 6, 13)
    rec_id = 0
    for day_offset in range(30):
        d = today - timedelta(days=day_offset)
        for facility in facilities:
            for shift in shifts[:2]:
                rec_id += 1
                headcount = random.randint(25, 60)
                direct = headcount * random.uniform(6.5, 7.8)
                indirect = headcount * random.uniform(0.5, 1.2)
                overtime = headcount * random.uniform(0, 1.5)
                efficiency = random.uniform(78, 96)
                records.append(DailyLaborRecord(
                    id=f"LBR-{rec_id:04d}",
                    facility=facility,
                    date=d.isoformat(),
                    shift=shift,
                    headcount=headcount,
                    direct_hours=round(direct, 1),
                    indirect_hours=round(indirect, 1),
                    overtime_hours=round(overtime, 1),
                    efficiency_pct=round(efficiency, 1),
                    skill_category=random.choice(skill_categories),
                    production_line_id=None,
                ))
    return records


DAILY_LABOR_RECORDS: list[DailyLaborRecord] = _generate_daily_labor()


# ─── Convenience aliases (used by service.py) ────────────────────────────────

SKU_MAP: dict[str, SKU] = {s.id: s for s in SKUS}
SUPPLIER_MAP: dict[str, Supplier] = {s.id: s for s in SUPPLIERS}
INVENTORY_POSITIONS = INVENTORY
CURRENT_KPIS = KPI
KPI_HISTORY = [KPI]
QUALITY_TEST_RESULTS = QUALITY_RESULTS
