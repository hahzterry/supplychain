# ATLAS Supply Chain Copilot
## Executive Product Brief

**Product Name:** ATLAS — Aerospace Tracking, Logistics & Analysis System
**Organization:** Heroux-Devtek Inc.
**Core Business:** Landing Gear, Actuation Systems, Hydraulics — World's 3rd Largest Landing Gear Manufacturer
**Version:** 1.1 Prototype
**Date:** June 2026

---

## 1. Executive Summary

ATLAS is an AI-powered supply chain copilot purpose-built for Heroux-Devtek — the world's third-largest aerospace landing gear manufacturer operating facilities in Longueuil (QC), Kitchener (ON), Springfield (OH), Nottingham (UK), Laval (QC), Livonia (MI), and CESA operations in Getafe and Seville (Spain).

ATLAS unifies demand forecasting, inventory management, supplier monitoring, production scheduling, contract/PO validation, labor utilization tracking, and scenario planning through a multi-agent AI system, enabling supply chain planners to move from reactive firefighting to proactive decision-making — all from a single trilingual (English/French/Spanish) conversational interface.

At the heart of the platform is **Atlas AI** (✦) — an autonomous AI orchestrator that routes complex supply chain queries to specialist agents running in parallel. An S&OP planner can ask "What happens if our Ti-6Al-4V supplier cuts allocation 20% during 777X rate increase?" and Atlas will simultaneously dispatch five LLM agents to model demand impact, simulate inventory depletion, evaluate alternative suppliers, assess production capacity, and synthesize a mitigation plan — all in under 30 seconds.

Every page in the platform — from the KPI Dashboard to Scenario Planner to Report Builder — is an Atlas-powered workflow. The UI visualizes agent activity in real time, making the AI's reasoning transparent and auditable for board-level decisions. The entire interface adapts dynamically based on the user's language preference, with all labels, charts, tables, and AI responses rendered in the selected language.

**Tagline:** "Engineering Confidence in Every Landing"

---

## 2. The Problem

Heroux-Devtek's supply chain spans specialty metals procurement (titanium, high-strength steels, superalloys from global sources), precision machining and assembly operations, multi-program delivery (commercial, military, business aviation), and stringent aerospace compliance (AS9100, NADCAP, DCMA). The S&OP team faces acute challenges:

### 2.1 Core Challenges

| Challenge | Impact |
|-----------|--------|
| **Reactive planning** — Stockouts and material shortages detected after the fact | Program delivery delays; CAD $2M+ monthly in expedite costs |
| **Fragmented data** — Demand, inventory, supplier, and production data in separate systems | No unified view; S&OP meetings rely on stale Excel snapshots |
| **Manual scenario analysis** — What-if scenarios require days of spreadsheet modeling | Decisions made without quantitative risk assessment |
| **Report generation overhead** — Weekly S&OP decks, inventory reviews, and scorecards consume 6+ hours | Senior planners spend 40% of time on formatting, not analysis |
| **Limited visibility** — No real-time view of cascading supply chain risks | Titanium allocation cuts discovered when forging lines idle |
| **Contract compliance gaps** — PO prices exceed negotiated ceilings without detection | Margin erosion on long-term programs |
| **Labor tracking fragility** — Shift-level efficiency data scattered across facilities | Cannot identify underutilization or skill bottlenecks |
| **Global team communication** — Multi-site teams across Canada, US, UK, Spain | Language barriers delay decisions between Francophone/Anglophone/Hispanic teams |

### 2.2 The Heroux-Devtek Complexity

Unlike a single-product company, Heroux-Devtek must simultaneously manage:

| Dimension | Scale |
|-----------|-------|
| Active SKUs | 50+ assemblies across 7 categories |
| Production Lines | 8 lines across 8 global facilities |
| Supplier Network | 10 specialized aerospace suppliers (France, USA, Canada) |
| Lead Time Range | 7-150 days depending on material and process |
| Program Mix | Commercial (777X, A350, A220, 737MAX), Military (F-35, CH-53K, CF-18), Business (Global 7500) |
| Certification Requirements | AS9100D, NADCAP Heat Treat, NADCAP NDT, Boeing/Airbus approvals |
| Service Level Target | >94% on-time delivery with <2% stockout |
| Languages | English, French (Canada), Spanish (CESA Spain operations) |

No existing supply chain tool combines real-time KPI monitoring, conversational AI, multi-agent scenario simulation, contract validation, labor tracking, automated report generation, and full trilingual support in a single platform. ATLAS solves this.

---

## 3. Solution Architecture

### 3.1 Design Philosophy

ATLAS is built on the principle that **AI should drive the application, not decorate it**. Atlas AI is not a chatbot sidebar — it is the central nervous system that powers every workflow. Each page in the platform is a visualization layer over Atlas's agent outputs. When a user runs a Scenario Analysis, Atlas's 5-stage pipeline does the work. When the Report Builder produces an S&OP deck, Atlas's multi-agent pipeline built it. When Inventory Health flags critical items, Atlas's risk engine scored them.

### 3.2 Platform Architecture

```
+-----------------------------------------------------------------------+
|                         ATLAS Frontend                                  |
|              React 19 + TypeScript + Fluent UI 9 + Vite                |
|                                                                        |
|  +----------+ +----------+ +----------+ +----------+ +----------+      |
|  |Dashboard | | Demand   | |Inventory | | Supply   | |Scenario  |      |
|  |          | | Forecast | | Health   | | Network  | | Planner  |      |
|  +----------+ +----------+ +----------+ +----------+ +----------+      |
|  +----------+ +----------+ +----------+ +----------+ +----------+      |
|  |Replenish | |Production| | Reports  | |  Labor   | | Settings |      |
|  |  Plan    | |Priorities| | Builder  | |Utilization|           |      |
|  +----------+ +----------+ +----------+ +----------+ +----------+      |
|                                                                        |
|  +----------------------------------------------------------------+   |
|  |         Atlas AI Chat Panel (Context-Aware, Trilingual)         |   |
|  |   Page-Specific Welcome | Dynamic Chips | Agent Status Cards    |   |
|  +----------------------------------------------------------------+   |
+-----------------------------------+------------------------------------+
                                    |
                         +----------+----------+
                         |   FastAPI Backend    |  (Python, port 8001)
                         |   SSE Streaming      |
                         +----------+----------+
                                    |
                         +----------+----------------------------+
                         |          ATLAS ORCHESTRATOR AGENT      |
                         |        (GPT-5.4-mini via Azure OpenAI) |
                         |                                        |
                         |  Demand Sensing  | Inventory Risk      |
                         |  Supply Constraint | Replenishment     |
                         |  Contract Validation | Labor Tracking  |
                         |  Scenario Pipeline | Report Pipelines  |
                         +----------------------------------------+
```

---

## 4. Multi-Agent Architecture — Atlas Orchestrator

### 4.1 Agent Identity

| Property | Value |
|----------|-------|
| Name | Atlas AI |
| Symbol | ✦ (sparkle star) |
| Meaning | Aerospace Tracking, Logistics & Analysis System |
| Role | Senior Aerospace Supply Chain Analyst & Orchestrator |
| Model | GPT-5.4-mini via Azure OpenAI |
| Protocol | SSE (Server-Sent Events) for real-time streaming |
| Personality | Data-driven, executive-concise, action-oriented |
| Languages | Responds in user's selected language (en/fr/es) |

### 4.2 Specialist Agents

Atlas delegates work to specialist agents that run in parallel:

| Agent | Responsibility | Key Outputs |
|-------|---------------|-------------|
| **Demand Sensing** | Program rates, order history, OEM schedule changes, MRO forecasting | SKU-level 8-week forecasts with confidence bands |
| **Inventory Risk** | Stock positions, days-of-supply, risk scoring, cert expiry tracking | Risk matrix (critical/warning/normal/excess), certification monitoring |
| **Supply Constraint** | Supplier lead times, production capacity, material allocation alerts | Reliability scores, delayed PO flags, capacity utilization |
| **Replenishment** | Purchase orders, production priorities, safety stock adjustments | Prioritized action cards with confidence scoring & KPI impact |

### 4.3 Additional Tools

| Tool | Purpose |
|------|---------|
| **Contract Price Validation** | Compare PO unit prices against negotiated contract ceilings, flag overages |
| **PO Validation** | Check qty ranges, lead time feasibility, duplicates, budget compliance |
| **Labor Utilization Dashboard** | Shift-level efficiency metrics, headcount, overtime tracking by facility |
| **Scenario Analysis Pipeline** | 5-stage quantitative what-if simulation |
| **Report Generation Pipeline** | Multi-agent PPTX/DOCX/PDF/XLSX document creation |

### 4.4 Routing Intelligence

Atlas classifies every user query and routes to the appropriate specialist:

| Query Type | Route |
|-----------|-------|
| Demand / forecast / program rate question | Demand Sensing |
| Stock / inventory status / cert expiry | Inventory Risk |
| Supplier / capacity / material allocation | Supply Constraint |
| What to order / replenishment | Replenishment |
| Contract pricing / PO compliance | Contract/PO Validation Tools |
| Labor / efficiency / overtime | Labor Utilization Dashboard |
| Full S&OP review | All agents in parallel |
| What-if / scenario | Scenario Analysis Pipeline (5-stage) |
| Generate deck / report | Report Generation Pipeline (multi-agent) |

---

## 5. Feature Deep-Dive — Ten Modules

### 5.1 KPI Dashboard

Real-time operational health across all supply chain dimensions:

- **8 KPI Cards** — Forecast Accuracy (MAPE), Inventory DOS, Fill Rate, Stockout Rate, Labor Utilization, Contract Compliance, Critical Alerts, Production Utilization
- **Risk Matrix** — Pie chart: critical, warning, normal, excess inventory distribution
- **Critical Alerts** — Top active alerts with severity badges and affected programs
- **Quick Actions** — Context-aware chips: Morning Brief, Check Risks, Generate Report
- **Fully Translated** — All KPI labels, targets, and chart legends adapt to selected language

**KPI Targets:**

| KPI | Target | Status Logic |
|-----|--------|--------------|
| Forecast Accuracy (MAPE) | < 10% | Green <= 10%, Red > 10% |
| Inventory Days of Supply | 30-60 days | Green 30-60, Red outside |
| Fill Rate | > 96% | Green >= 96%, Red < 96% |
| On-Time Delivery | > 94% | Green >= 94%, Red < 94% |
| Labor Utilization | > 85% | Green >= 85%, Red < 85% |
| Contract Compliance | > 90% | Green >= 90%, Red < 90% |
| Production Utilization | 75-90% | Optimal range |

### 5.2 Demand Forecast

AI-powered demand intelligence with confidence visualization:

- **SKU Selection** — Filter by part number, program, or category
- **8-Week Forecast Chart** — Point forecast with 80% and 95% confidence bands (area chart)
- **Program Change Flags** — Visual indicators for OEM rate changes
- **Demand Signals** — Trend direction, program schedules, MRO forecasts
- **Translated Legends** — Chart legends (CI 95%, CI 80%, Forecast) display in selected language

### 5.3 Inventory Health

Portfolio-level inventory risk assessment:

- **Risk Matrix Visualization** — Distribution across critical, warning, normal, excess
- **Position Table** — SKU, category, DOS, stock level, risk badge, certification expiry remaining
- **DOS-Sorted View** — Lowest days-of-supply first to highlight at-risk items
- **Cert Expiry Tracking** — Material certifications approaching expiry flagged for re-test or scrap
- **Translated Table Headers & Badges** — All column headers, risk levels, and status badges render in selected language

### 5.4 Supply Network

Supplier performance monitoring and production capacity visualization:

- **Supplier Table** — Name, country, lead time (days), reliability score, active orders, certifications
- **Production Capacity** — Horizontal bar chart of line utilization with color-coded thresholds
- **Detail Panels** — Click supplier for performance trends, NADCAP certs, PO history
- **All 8 Facilities Covered** — Longueuil, Kitchener, Springfield, Nottingham, Laval, Livonia, Getafe/Madrid, Seville

### 5.5 Scenario Planner (What-If Analysis)

The flagship analytical capability — a 5-stage LLM pipeline for quantitative scenario simulation:

- **Quick Scenario Chips** — Pre-built common scenarios (translated to active language)
- **Custom Natural Language Input** — Describe any what-if in any supported language
- **Real-Time Pipeline Progress** — Visual 5-stage tracker with status badges
- **Fully Translated Results** — All tabs, charts, tables, badges, and labels render in the selected language

**5-Stage Pipeline:**

```
Scenario Planner -> Impact Analyzer -> Mitigation Designer -> Risk Assessor -> Synthesizer
```

**Result Tabs (All Translated):**

| Tab | Content |
|-----|---------|
| **Impact Summary** | Affected SKU count, KPI comparison (baseline vs. projected), target breaches |
| **Affected Part Numbers** | Severity-coded table with demand delta %, weeks-to-stockout, DOS projection |
| **Stock Timeline** | 8-week demand trajectory, inventory depletion curves, stockout risk visualization |
| **Mitigation & Supply** | Prioritized options with cost (CAD), delivery recovery, lead time; alternative suppliers; production surge capacity |

**Scenario Comparison:** Select any 2 historical scenarios for side-by-side KPI comparison with delta analysis.

### 5.6 Replenishment Plan

AI-generated, action-ready replenishment recommendations:

- **Prioritized Action Cards** — Each card shows SKU, urgency badge (critical/high/normal), recommended quantity, confidence level
- **Action Types** — Emergency order, expedite, safety stock increase, internal transfer, new PO
- **Scenario Variants** — Conservative, balanced, aggressive options with KPI trade-offs
- **Approve/Dismiss Workflow** — One-click approval with KPI impact confirmation dialog
- **Translated Dialogs** — Approval confirmation, cancel, and all button text in active language

### 5.7 Production Priorities

Real-time production line monitoring and scheduling:

- **Utilization Chart** — All 8 lines visualized with current utilization %
- **Schedule Table** — Line name, plant, capacity (units/day), current SKU, shift pattern, planned maintenance
- **Capacity Headroom** — Spare capacity available for surge production
- **Translated Headers** — All table columns and labels render in selected language

### 5.8 Labor Utilization

Daily labor efficiency tracking across all 8 facilities:

- **KPI Cards** — Average efficiency, direct labor %, total headcount, overtime hours
- **Efficiency by Facility Chart** — Bar chart comparing all 8 facility performance
- **Daily Records Table** — Filterable by facility, shift; shows headcount, direct/indirect hours, overtime, skill category
- **Full Site Coverage** — Longueuil, Kitchener, Springfield, Nottingham, Laval, Livonia, Getafe/Madrid, Seville
- **Translated Labels** — KPI titles, chart legend, table headers, filter options all in active language

### 5.9 Report Builder (Multi-Agent Document Generation)

Fully agentic report generation with zero manual formatting:

| Template | Format | Use Case |
|----------|--------|----------|
| Weekly S&OP Review | PPTX | KPIs, alerts, demand outlook, actions (10 slides) |
| Inventory Status | PPTX | Stock positions, risk matrix, cert expiry analysis |
| Demand Accuracy | PPTX | MAPE trends, bias analysis, forecast vs actuals |
| Executive S&OP Summary | DOCX/PDF | High-level performance & decisions for leadership |
| Inventory Deep-Dive | DOCX/PDF | Portfolio health, stockout risk, safety stock optimization |
| Replenishment Plan | XLSX | Priority orders, production schedule, cost analysis |
| Supplier Scorecard | XLSX | Lead times, reliability rankings, quality scores, NADCAP status |

**Generation Pipeline (PPTX — 5 Agents):**

```
Planner -> Content Writer -> Designer -> Critic -> Repair (up to 2 iterations)
```

**Features:**
- Section customization (toggle specific sections on/off)
- Audience configuration (S&OP Committee, Executive Leadership, Operations Team)
- Real-time progress visualization per pipeline stage
- Preview before download
- Regeneration with per-section feedback
- HD branding with navy/gold corporate identity

### 5.10 Atlas AI Chat Panel — Context-Aware Conversational Interface

The Atlas AI chat panel is not a feature bolted on — it is the primary interaction mode:

- **Page-Aware Context** — Welcome message and suggestion chips change based on the active page
- **Trilingual Interface** — Welcome messages, chips, processing indicators, and error messages in active language
- **Natural Language Queries** — "What's the cert expiry risk for titanium forgings this quarter?"
- **Agent Activity Visualization** — Real-time planning blocks showing which specialist agent and tool is executing
- **Dynamic Follow-Up Chips** — Post-response suggestions based on AI analysis
- **Language-Aware Responses** — Atlas responds in the user's selected language while keeping internal LLM prompts in English for optimal reasoning

**Page Context Examples:**

| Page | Welcome Message (EN) | Example Chips |
|------|---------------------|---------------|
| Dashboard | "I'm Atlas AI — your aerospace supply chain copilot..." | Morning supply brief, Check supply risks |
| Demand Forecast | "I can analyze demand patterns..." | 8-week forecast, Program rate impact |
| Scenario Planner | "I can run complex what-if simulations..." | Rate increase scenario, Forging delay |
| Labor Utilization | "I can analyze workforce efficiency..." | Site efficiency comparison, Overtime analysis |

---

## 6. Internationalization (i18n) — Trilingual Support

ATLAS supports full trilingual operation for global aerospace operations:

| Aspect | Implementation |
|--------|---------------|
| **Supported Languages** | English (en), French (fr), Spanish (es) |
| **UI Labels & Navigation** | 300+ translation keys via React i18n context |
| **Table Column Headers** | All data tables translate headers dynamically |
| **Chart Legends & Labels** | Recharts `name` props use translated strings |
| **KPI Card Titles** | Dashboard, Labor, and all module cards translated |
| **Badge Text** | Risk levels (Critical/Warning/Safe), status indicators |
| **Dialog Text** | Confirmation dialogs, buttons, placeholder text |
| **Atlas AI Responses** | Language-aware prompting (responds in user's language) |
| **Report Generation** | LLM generates document content in selected language |
| **Chat Context** | Page-specific welcome messages and chip labels per language |
| **Settings Page** | All setting labels and status text translated |
| **Language Switch** | One-click rotation: EN -> FR -> ES -> EN |

**Translation Coverage by Module:**

| Module | Translated Elements |
|--------|-------------------|
| Dashboard | KPI targets, chip labels, chart legends |
| Demand Forecast | Stat cards, confidence band labels, chips |
| Inventory Health | Table headers, risk badges, chips |
| Supply Network | Table headers, chips |
| Scenario Planner | All 4 result tabs, charts, badges, history, comparison |
| Replenishment | Dialog labels, button text, chips |
| Production | Table headers, chips |
| Labor Utilization | KPIs, table headers, chart legend, filter, chips |
| Reports | Template names, section headers (in-progress) |
| Settings | All labels and status text |
| Agent Result Panel | Title, recommended actions, dismiss button |

---

## 7. User Interface Design

### 7.1 Sidebar Navigation

- **Company Logo** — HD logo on dark navy (#1a1a2e) background for visibility
- **Icon Navigation** — 10 pages with tooltip labels (translated)
- **Active Page Indicator** — Left accent bar (brand color inset box-shadow) for clear current page identification
- **Language Toggle** — Bottom of sidebar, cycles EN/FR/ES
- **Logout** — Session termination

### 7.2 Header Bar

- **Full HD Logo** — Heroux-Devtek wordmark with tagline
- **App Title** — "ATLAS — Aerospace Supply Chain Intelligence" (translated)
- **Chat Toggle** — Show/hide Atlas AI panel

### 7.3 Atlas AI Branding

- **Symbol:** ✦ (sparkle star) — used consistently across chat header, message avatars, suggestion chips, and loading states
- **Color Scheme:** Gold (#B8860B) accent on warm cream (#fdf8ee) backgrounds
- **Personality:** Concise, data-driven, action-oriented responses

---

## 8. User Journeys

### 8.1 Morning Routine — S&OP Planner

```
1. Open ATLAS -> Dashboard shows 3 critical alerts, on-time delivery at 94.1%
2. Ask: "Morning brief" -> Atlas compiles daily KPIs, flags Ti-6Al-4V shortage risk
3. Click critical SKU -> Detail Drawer shows 18 days DOS, declining trend
4. Ask: "What happens if TIMET allocation is cut another 10%?"
   -> Scenario pipeline runs: 8 SKUs affected, 3 will stock out by Week 6
5. Review mitigation tab -> Approve alternate source order from Aubert & Duval
6. Ask: "Generate the weekly S&OP deck for tomorrow's meeting"
   -> 10-slide PPTX generated with current data, downloaded in 45 seconds
```

### 8.2 Risk Escalation — VP Supply Chain

```
1. Receive Atlas alert: "NDT indication on F-35 MLG batch -- DCMA hold"
2. Open Supply Network -> See Springfield capacity at 95% (near limit)
3. Ask: "Run scenario: F-35 MLG rework adds 3 weeks to delivery schedule"
   -> Pipeline shows 4 assemblies affected, CAD $580K potential liquidated damages
4. Review alternative production -> Longueuil has 13% spare capacity
5. Ask: "Generate executive summary of this scenario for program management"
   -> DOCX generated with impact analysis, mitigation costs, recommendation
6. Approve: Split rework between Springfield and Longueuil
```

### 8.3 Spanish Operations — CESA Getafe Team

```
1. Switch language to Spanish -> Entire UI renders in Spanish
2. Open Scenario Planner -> Chips show "Aumento cadencia: A220 +30%"
3. Click chip -> Message posts in English to LLM (optimal reasoning)
   -> Response returns in Spanish (detects user language preference)
4. Review results -> All tabs (Resumen de impacto, Numeros de pieza afectados,
   Cronologia de stock, Mitigacion y suministro) fully in Spanish
5. Export report -> Content generated in Spanish for local stakeholders
```

### 8.4 Contract Review — Procurement Manager

```
1. Ask: "Validate all open PO pricing against contracts"
   -> Atlas runs contract price validation: 2 POs over ceiling
2. Review PO-2026-002: 300M Forging at CAD $34,500 vs ceiling $6,200/part
3. Ask: "What's the total exposure on over-ceiling POs this quarter?"
   -> Atlas calculates variance across all flagged POs
4. Generate supplier scorecard Excel for quarterly business review
```

---

## 9. Technical Architecture

### 9.1 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 19, TypeScript, Vite | SPA with HMR (port 5174) |
| UI Framework | Fluent UI 9 | Microsoft design system (enterprise grade) |
| Charts | Recharts | Data visualization (area, line, bar, pie) |
| Routing | React Router DOM | Client-side navigation |
| Backend | FastAPI (Python 3.13) | API server with async support (port 8001) |
| AI Orchestration | Agent Framework + Azure OpenAI | Multi-agent routing and tool dispatch |
| LLM Model | GPT-5.4-mini (Azure) | All agent reasoning and generation |
| Document Gen | PptxGenJS, docx, jsPDF, ExcelJS | Client-side file rendering |
| State Management | React Context + Custom Events | Cross-component communication |
| Session | UUID-based session management | Multi-user isolation |
| i18n | Custom React context (`useI18n` hook) | English/French/Spanish trilingual support |

### 9.2 Frontend Architecture

| Component | File | Responsibility |
|-----------|------|---------------|
| Layout | `src/components/Layout.tsx` | Sidebar nav, header, chat toggle, active page |
| Chat Panel | `src/components/ChatPanel.tsx` | Context-aware AI conversation |
| Agent Result | `src/components/AgentResultPanel.tsx` | Structured result display |
| i18n System | `src/i18n.tsx` | 300+ translation keys, `t()` function, `Lang` type |
| Chat Context | `src/lib/chatPageContext.ts` | Page-specific multilingual welcome/chips |
| PDF Renderer | `src/pdf/renderer.ts` | A4 PDF generation with HD branding |
| PPTX Renderer | `src/pptx/renderer.ts` | Slide deck generation |
| DOCX Renderer | `src/docx/renderer.ts` | Word document generation |
| XLSX Renderer | `src/xlsx/renderer.ts` | Excel workbook generation |

### 9.3 Data Architecture

| Data Source | Current | Production Target |
|-------------|---------|-------------------|
| SKU Master | Mock (50 SKUs) | SAP MM / Windchill PLM |
| Inventory Positions | Mock (real-time) | WMS API |
| Demand Forecasts | Mock (8-week) | SAP APO / IBP |
| Supplier Data | Mock (10 suppliers) | SAP SRM / Ariba |
| Production Schedule | Mock (8 lines) | SAP PP / MES |
| Purchase Orders | Mock (15 POs) | SAP MM |
| Contracts | Mock (3 contracts) | SAP CLM |
| Quality Results | Mock (NDT/dimensional) | LIMS / InfinityQS |
| Labor Records | Mock (300 records, all 8 sites) | ADP / Kronos |
| Alerts | Mock (rule-based) | Event stream / IoT |

---

## 10. Expected Outcomes

### 10.1 Efficiency Gains

| Metric | Before ATLAS | With ATLAS | Improvement |
|--------|--------------|------------|-------------|
| Scenario analysis time | 2-3 days (manual Excel) | 30 seconds | 99% reduction |
| Weekly S&OP deck preparation | 6+ hours | 45 seconds | 99% reduction |
| Morning supply review | 45 minutes (multiple systems) | 2 minutes (single query) | 95% reduction |
| Stockout detection | After the fact | Predictive (8-week horizon) | Proactive vs. reactive |
| Contract compliance review | Monthly spot-checks | Real-time on every PO | Continuous vs. periodic |
| Labor efficiency reporting | Manual end-of-week | Daily automated | 80% reduction |
| Report formatting effort | 40% of planner time | Zero (fully automated) | 100% elimination |
| Cross-site communication | English-only reports | Native language for each site | Zero translation overhead |

### 10.2 Strategic Impact

- **Decision Speed** — From weekly S&OP cycles to real-time scenario-based decisions
- **Risk Visibility** — Cascading risks (material -> production -> delivery) surfaced before they materialize
- **Service Level** — On-time delivery maintained >94% through predictive replenishment
- **Cost Control** — Contract compliance monitoring prevents margin erosion on long-term programs
- **Labor Optimization** — Shift-level visibility enables targeted efficiency improvements
- **Global Collaboration** — Trilingual support enables CESA Spain teams to work natively in Spanish
- **Stakeholder Communication** — Board-ready documents generated on demand in any supported language

---

## 11. Roadmap Considerations

| Phase | Scope | Timeline |
|-------|-------|----------|
| **Phase 1** (Current) | Prototype with mock data, full UI, all agent pipelines, trilingual i18n | Complete |
| **Phase 2** | SAP/ERP data integration, live inventory feeds, Windchill PLM link | Q3 2026 |
| **Phase 3** | MES integration (production actuals), LIMS quality data | Q4 2026 |
| **Phase 4** | Automated PO creation (agent-initiated procurement) | Q1 2027 |
| **Phase 5** | Predictive maintenance integration (IoT sensor feeds) | Q2 2027 |

---

## 12. Security & Classification

| Aspect | Current (Prototype) | Production Recommendation |
|--------|--------------------|-----------------------------|
| Authentication | Session-based login | Azure AD / SSO integration |
| Data Classification | Internal Confidential | ITAR/EAR compliance for military programs |
| API Security | Session headers | OAuth 2.0 + API key rotation |
| LLM Data | Azure OpenAI (data stays in Azure tenant) | Private endpoint, no external data leakage |
| Audit Trail | Session-based | Full action audit log with user attribution |
| Export Control | N/A (mock data) | ITAR screening on military program data |

---

## 13. Recent Changes (v1.1)

| Change | Description |
|--------|-------------|
| **Trilingual Support** | Added Spanish (es) as third language alongside English and French |
| **Full i18n Coverage** | 300+ translation keys covering all pages, tables, charts, badges, dialogs |
| **Context-Aware Chat** | Atlas AI welcome message and chips change per page, translated per language |
| **Atlas AI Branding** | Sparkle star symbol (✦), gold/cream color scheme |
| **Sidebar Active Indicator** | Left accent bar shows current active page |
| **Labor Coverage** | Daily utilization data now covers all 8 global facilities |
| **Forecast Scale** | 8-week forecast Y-axis properly scaled to production volumes |
| **Scenario Planner i18n** | All result tabs (Summary, Affected SKUs, Timeline, Mitigation) fully translated |
| **Browser Tab** | Title updated to "ATLAS — Aerospace Supply Chain Intelligence" |
| **Logo Visibility** | Sidebar logo on dark navy background for proper contrast |

---

## 14. Conclusion

ATLAS transforms Heroux-Devtek's supply chain planning from a fragmented, reactive, spreadsheet-driven process into a unified, AI-powered decision engine. By combining:

- **Multi-agent AI orchestration** — 4 specialist agents + orchestrator for parallel intelligence gathering
- **Quantitative scenario simulation** — 5-stage LLM pipeline replacing days of manual modeling
- **Contract & PO validation** — Real-time compliance checking against negotiated pricing
- **Labor utilization tracking** — Shift-level efficiency metrics across all 8 facilities
- **Automated document generation** — 7 templates across PPTX/DOCX/PDF/XLSX with zero formatting effort
- **Conversational interface** — Natural language access to all supply chain data and actions
- **Real-time risk monitoring** — Predictive alerts before stockouts or cert lapses materialize
- **Trilingual operation** — English, French, and Spanish for global team collaboration

...ATLAS enables Heroux-Devtek's S&OP team to make faster, better-informed decisions — protecting >94% on-time delivery across 50+ aerospace assemblies while managing a specialized global supplier network with lead times from 7 to 150 days.

The platform is designed for progressive deployment: immediate value from the prototype with mock data, scaling to full ERP/MES integration without architectural changes.

---

*This document was generated by Atlas AI for Heroux-Devtek Inc.*
*Classification: Internal — Executive Review*
*Version 1.1 — June 2026*
