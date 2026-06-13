---
pdf_options:
  format: A4
  margin: 25mm
  displayHeaderFooter: true
  headerTemplate: '<div style="font-size:8px; width:100%; text-align:right; padding-right:25mm; color:#999;">ATLAS — Aerospace Supply Chain Intelligence</div>'
  footerTemplate: '<div style="font-size:8px; width:100%; text-align:center; color:#999;">Page <span class="pageNumber"></span> of <span class="totalPages"></span> | Confidential</div>'
css: |-
  body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1a1a2e; font-size: 12px; line-height: 1.6; }
  h1 { color: #001f3f; border-bottom: 3px solid #D4930D; padding-bottom: 8px; font-size: 24px; }
  h2 { color: #001f3f; border-bottom: 1px solid #D4930D; padding-bottom: 4px; margin-top: 28px; font-size: 18px; }
  h3 { color: #002b5c; font-size: 14px; }
  h4 { color: #333; font-size: 12px; }
  table { font-size: 11px; border-collapse: collapse; width: 100%; margin: 10px 0; }
  th { background-color: #001f3f; color: white; padding: 6px 8px; text-align: left; }
  td { padding: 5px 8px; border-bottom: 1px solid #e0e0e0; }
  tr:nth-child(even) { background-color: #f8f8f8; }
  code { background: #f0e6cc; color: #6b5300; padding: 2px 5px; border-radius: 3px; font-size: 11px; }
  pre { background: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; padding: 12px; font-size: 10px; }
  blockquote { border-left: 4px solid #D4930D; background: #fdf8ee; padding: 10px 16px; margin: 16px 0; font-style: normal; }
  strong { color: #001f3f; }
---

# ATLAS — Aerospace Supply Chain Intelligence

## Executive Product Brief

**Platform:** Multi-Agent AI Copilot for Aerospace Supply Chain Operations  
**AI Assistant:** Atlas AI Orchestrator  
**Organization:** Heroux-Devtek Inc.  
**Framework:** Microsoft Agent Framework & Microsoft Foundry  
**AI Models:** GPT-5.4-mini, KIMI2.6 (via Microsoft Foundry)  
**Version:** 1.1 — Proof of Concept  
**Date:** June 2026

---

## 1. Executive Summary

Heroux-Devtek is the world's third-largest aerospace landing gear manufacturer, operating 8 facilities across Canada, USA, UK, and Spain — serving programs including 777X, A350, A220, 737MAX, F-35, CH-53K, and Global 7500. The current S&OP environment relies on disconnected systems for demand planning, inventory management, supplier monitoring, and production scheduling — resulting in reactive decision-making, stockout events, and significant manual overhead.

The **ATLAS Supply Chain Intelligence Platform** introduces a multi-agent AI orchestration layer that transforms how S&OP planners, procurement managers, operations directors, and leadership interact with supply chain data. The platform uses 4 specialist AI agents with a 5-stage scenario pipeline to deliver quantitative what-if simulation, predictive inventory risk scoring, automated replenishment recommendations, contract compliance validation, labor utilization tracking, and multi-format report generation — all through a trilingual (English/French/Spanish) conversational interface.

> **Key Differentiator:** Every page in ATLAS is an Atlas AI-powered workflow. The AI doesn't decorate the app — it drives it. The entire UI adapts dynamically based on the user's language preference, with all labels, charts, tables, and AI responses rendered in the selected language.

---

## 2. The Problem

### 2.1 Current State Challenges

| Domain | Challenge | Impact |
|--------|-----------|--------|
| Demand Planning | Forecasts in separate systems, manual reconciliation | Misaligned production, missed program rate changes |
| Inventory Management | Reactive stockout detection, no predictive visibility | CAD $2M+/month in expedite costs |
| Scenario Analysis | Manual spreadsheet modeling for what-if simulations | 2-3 days per scenario, decisions without quantitative backing |
| Report Generation | Weekly S&OP decks assembled manually from multiple sources | 6+ hours per deck, 40% of planner time on formatting |
| Supplier Monitoring | No real-time view of cascading supply risks | Titanium allocation cuts discovered when forging lines idle |
| Contract Compliance | PO pricing checked via monthly spot-audits | Margin erosion on long-term programs |
| Labor Tracking | Shift-level efficiency scattered across 8 facilities | Cannot identify underutilization or skill bottlenecks |
| Global Communication | Multi-site teams across Canada, US, UK, Spain | Language barriers delay decisions between sites |

### 2.2 Core Pain Points

1. **Reactive planning** — stockouts detected after the fact, not 8 weeks in advance
2. **Data fragmentation** — S&OP meetings rely on stale Excel snapshots from 5+ systems
3. **Scenario paralysis** — what-if questions take days, so decisions are made on intuition
4. **Report drudgery** — senior planners spend 40% of time formatting, not analyzing
5. **Supplier blindness** — no cascading risk visibility across the 10-supplier network
6. **Contract leakage** — PO overages go undetected between quarterly reviews
7. **Language friction** — CESA Spain teams require translation for every English report

---

## 3. Solution Architecture

### 3.1 Design Philosophy

The platform operates as an **AI-driven decision engine**:

- **AI drives the application, not decorates it** — every page is an Atlas AI-powered workflow
- **Microsoft Agent Framework & Microsoft Foundry** for multi-agent orchestration
- **4 specialist agents + orchestrator** running in parallel
- **5-stage scenario pipeline** for quantitative what-if simulation
- **Trilingual operation** — all UI, charts, tables, and AI responses adapt to EN/FR/ES
- **All agent output is real** (LLM-generated) — only underlying data is synthetic for this PoC
- **Conversational interface** as the primary interaction mode

### 3.2 Platform Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│              Frontend — React 19 + TypeScript + Vite + Fluent UI 9       │
│   10 Module Pages │ Atlas AI Chat Panel │ Agent Results │ Report Gen    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ SSE Streaming (/api/chat)
┌────────────────────────────────────▼────────────────────────────────────┐
│                   Backend — FastAPI + Agent Framework                     │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │   Atlas AI Orchestrator (Microsoft Agent Framework & Foundry)       │ │
│  │     Models: GPT-5.4-mini + KIMI2.6 (via Microsoft Foundry)              │ │
│  │     Routes to specialist agents based on query classification       │ │
│  └──────────┬─────────────────────────────────────────────────────────┘ │
│             │                                                            │
│  ┌──────────▼─────────────────────────────────────────────────────────┐ │
│  │  Specialist Agents (4)                  Tools & Pipelines           │ │
│  │  • Demand Sensing Specialist            • Contract Price Validation │ │
│  │  • Inventory Risk Specialist            • PO Compliance Checker     │ │
│  │  • Supply Constraint Specialist         • Labor Utilization Dash    │ │
│  │  • Replenishment Specialist             • Scenario Pipeline (5-stg) │ │
│  │                                         • Report Gen (5 agents)     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│             │                                                            │
│  ┌──────────▼─────────────────────────────────────────────────────────┐ │
│  │  Data Service Layer                     Document Generation          │ │
│  │  • SKU Master (50 assemblies)           • PPTX Pipeline (5 agents)  │ │
│  │  • Inventory Positions                  • DOCX/PDF Renderer         │ │
│  │  • Supplier Network (10)                • XLSX Workbooks            │ │
│  │  • Production Schedule (8 lines)        • HD Navy/Gold Branding     │ │
│  │  • Labor Records (8 facilities)                                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Product Modules

### 4.1 KPI Dashboard

| Capability | How It Works |
|-----------|--------------|
| Real-time KPI cards | 8 metrics: MAPE, DOS, Fill Rate, OTD, Labor Util, Contract Compliance, Alerts, Production |
| Risk matrix | Pie chart: critical, warning, normal, excess inventory distribution |
| Critical alerts | Top active alerts with severity badges and affected programs |
| Context-aware chips | Page-specific quick actions adapt to current module and language |

### 4.2 Demand Forecast

| Capability | How It Works |
|-----------|--------------|
| 8-week forecast | SKU-level point forecast with 80% and 95% confidence bands |
| Program change flags | Visual indicators when OEM rate changes affect demand |
| Demand signals | Trend direction, program schedules, MRO forecast signals |
| Translated legends | Chart legends and stat cards render in selected language |

### 4.3 Inventory Health

| Capability | How It Works |
|-----------|--------------|
| Risk scoring | Every SKU scored: critical (stockout imminent), warning, normal, excess |
| DOS-sorted view | Lowest days-of-supply first for immediate triage |
| Cert expiry tracking | Material certifications approaching expiry flagged for re-test |
| Badge translation | Risk levels display in active language (Critical/Critique/Critico) |

### 4.4 Supply Network

| Capability | How It Works |
|-----------|--------------|
| Supplier monitoring | 10 aerospace suppliers: reliability scores, lead times, active orders |
| Production capacity | Horizontal bar chart of 8-line utilization with threshold coloring |
| Certification tracking | NADCAP, AS9100 approval status per supplier |
| Detail panels | Click-through for performance trends, PO history, quality metrics |

### 4.5 Scenario Planner (Flagship)

| Capability | How It Works |
|-----------|--------------|
| 5-stage AI pipeline | Planner → Impact Analyzer → Mitigation Designer → Risk Assessor → Synthesizer |
| Quick scenario chips | Pre-built aerospace scenarios (rate increase, forging delay, AOG, titanium disruption) |
| Custom natural language | Describe any what-if in any supported language |
| 4 result tabs | Impact Summary, Affected Part Numbers, Stock Timeline, Mitigation & Supply |
| Scenario comparison | Select any 2 historical scenarios for side-by-side KPI delta analysis |
| Full translation | Every tab, chart, table, badge renders in active language |

### 4.6 Replenishment Plan

| Capability | How It Works |
|-----------|--------------|
| Prioritized action cards | SKU, urgency badge, recommended qty, confidence, supplier, rationale |
| Scenario variants | Conservative, balanced, aggressive options with KPI trade-offs |
| Approve/dismiss workflow | One-click approval with KPI impact confirmation dialog |
| Translated dialogs | All button text, labels, and rationale in active language |

### 4.7 Production Priorities

| Capability | How It Works |
|-----------|--------------|
| Utilization chart | All 8 lines visualized with current utilization % |
| Schedule table | Line, plant, capacity, current SKU, shift pattern, maintenance |
| Capacity headroom | Spare capacity available for surge production identified |

### 4.8 Labor Utilization

| Capability | How It Works |
|-----------|--------------|
| Facility coverage | All 8 global facilities: Longueuil, Kitchener, Springfield, Nottingham, Laval, Livonia, Getafe, Seville |
| KPI cards | Average efficiency, direct labor %, total headcount, overtime hours |
| Facility comparison | Bar chart comparing all 8 sites |
| Filterable records | Daily records by facility, shift, skill category, overtime |

### 4.9 Report Builder (Multi-Agent)

| Capability | How It Works |
|-----------|--------------|
| 7 templates | Weekly S&OP (PPTX), Inventory Status (PPTX), Executive Summary (DOCX/PDF), Replenishment (XLSX), Supplier Scorecard (XLSX) |
| 5-agent pipeline | Planner → Content Writer → Designer → Critic → Repair (up to 2 iterations) |
| HD branding | Navy/gold corporate identity, logo, consistent formatting |
| Language-aware | Report content generated in selected language |

### 4.10 Atlas AI Chat Panel

| Capability | How It Works |
|-----------|--------------|
| Page-aware context | Welcome message and chips change based on active page |
| Trilingual interface | All UI elements adapt to EN/FR/ES |
| Agent visualization | Real-time planning blocks show active specialist and tool |
| Dynamic follow-ups | Post-response suggestion chips based on AI analysis |
| Message actions | Copy, upvote, downvote, regenerate on every response |
| Language-aware LLM | Responds in user's language; internal prompts stay English for optimal reasoning |

---

## 5. Personas & Use Cases

The platform serves **5 core personas** across Heroux-Devtek's global operations:

| Persona | Role | Key Journeys |
|---------|------|-------------|
| S&OP Planner | Daily operations owner | Morning brief, demand analysis, scenario simulation, replenishment approval, report generation |
| VP Supply Chain | Executive decision-maker | Risk escalation, financial exposure assessment, board reporting, mitigation approval |
| Procurement Manager | Supplier & contract owner | Contract validation, PO compliance, emergency ordering, supplier scorecards |
| Operations Director | Production & labor | Capacity planning, surge assessment, labor utilization, production re-sequencing |
| CESA Plant Manager | Spanish operations | Full Spanish-language operations, local reporting, production management |

---

## 6. AI Agent Architecture

### 6.1 Agent Identity

| Property | Value |
|----------|-------|
| Name | Atlas AI |
| Symbol | ✦ (sparkle star) |
| Framework | Microsoft Agent Framework & Microsoft Foundry |
| Models | GPT-5.4-mini (orchestration, routing), KIMI2.6 (complex reasoning) |
| Protocol | SSE (Server-Sent Events) for real-time streaming |
| Personality | Data-driven, executive-concise, action-oriented |
| Language | Responds in user's selected language (en/fr/es) |

### 6.2 Specialist Agents

| Agent | Responsibility | Key Outputs |
|-------|---------------|-------------|
| **Demand Sensing** | Program rates, OEM schedule changes, MRO forecasting | SKU-level 8-week forecasts with confidence bands |
| **Inventory Risk** | Stock positions, DOS, risk scoring, cert expiry | Risk matrix, predictive stockout alerts |
| **Supply Constraint** | Supplier lead times, capacity, material allocation | Reliability scores, delayed PO flags |
| **Replenishment** | Purchase orders, safety stock, production priorities | Prioritized action cards with KPI impact |

### 6.3 Scenario Pipeline (5-Stage)

| Stage | Agent | Output |
|-------|-------|--------|
| 1 | Scenario Planner | Classify and structure the scenario |
| 2 | Impact Analyzer | Quantitative modeling (demand, inventory, supply, production) |
| 3 | Mitigation Designer | Generate alternatives (suppliers, production surge) |
| 4 | Risk Assessor | Probability and severity assessment |
| 5 | Synthesizer | Executive summary with decision points |

### 6.4 Report Generation Pipeline (5-Agent)

| Stage | Agent | Output |
|-------|-------|--------|
| 1 | Planner | Outline slides/sections with allocation |
| 2 | Content Writer | Fill with real data and narrative |
| 3 | Designer | Apply HD branding, layout validation |
| 4 | Critic | Score quality 1-10, identify issues |
| 5 | Repair | Fix issues if score < 7 (max 2 iterations) |

### 6.5 Query Routing

| Query Type | Route |
|-----------|-------|
| Demand / forecast / program rate | Demand Sensing Agent |
| Stock / inventory / cert expiry | Inventory Risk Agent |
| Supplier / capacity / material | Supply Constraint Agent |
| Replenishment / orders | Replenishment Agent |
| Contract / PO pricing | Contract Validation Tool |
| Labor / efficiency / overtime | Labor Utilization Dashboard |
| What-if / scenario | 5-Stage Scenario Pipeline |
| Generate report / deck | 5-Agent Report Pipeline |

---

## 7. Trilingual Internationalization

The platform supports full trilingual operation across all UI elements:

| Element Type | Coverage |
|-------------|----------|
| Navigation & page titles | All 10 modules |
| Table column headers | Every data table across all pages |
| Chart legends & labels | All Recharts visualizations |
| KPI card titles | Dashboard, Labor, all modules |
| Badge text | Critical/Warning/Safe (translated) |
| Scenario results | All 4 tabs, history, comparison |
| Dialog text & buttons | Confirmations, approve, cancel |
| Atlas AI responses | Language-aware LLM prompting |
| Report content | Generated in selected language |
| Chat welcome & chips | Page-specific per language |

**Implementation:** 300+ translation keys via custom React i18n context.  
**Language switch:** One-click rotation (EN → FR → ES → EN) in sidebar.

---

## 8. Key Differentiators

| Feature | Description |
|---------|-------------|
| **AI drives, not decorates** | Every page is an Atlas AI workflow — not a chatbot sidebar bolted on |
| **Multi-agent orchestration** | 4 specialists + orchestrator with parallel execution |
| **5-stage scenario pipeline** | Quantitative what-if replacing days of manual modeling |
| **Trilingual operation** | Complete EN/FR/ES coverage — UI, charts, tables, AI responses |
| **Context-aware chat** | Welcome messages and chips change per page and language |
| **Decision-ready output** | Recommendations with costs, timelines, and KPI impact — not just data |
| **One-click reports** | 7 templates across 4 formats, branded, generated in seconds |
| **Microsoft Foundry** | Enterprise-grade agent framework with GPT-5.4-mini + KIMI2.6 models |
| **Real AI output** | All agent responses are LLM-generated — not templates or rules |

---

## 9. Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Fluent UI 9 |
| Backend | Python FastAPI, Microsoft Agent Framework |
| AI Platform | Microsoft Foundry |
| AI Models | GPT-5.4-mini (orchestration), KIMI2.6 (complex reasoning) |
| Streaming | SSE (Server-Sent Events) for real-time agent communication |
| Charts | Recharts (area, line, bar, pie) |
| Document Gen | PptxGenJS, docx, jsPDF, ExcelJS |
| i18n | Custom React context (300+ keys, 3 languages) |
| Session | UUID-based multi-user isolation |
| Deployment | Vite dev server (5174) + FastAPI (8001) |

---

## 10. Demonstrated Value (PoC Metrics)

Based on synthetic data simulating Heroux-Devtek's operational environment:

| Metric | Value |
|--------|-------|
| Scenario analysis time | 2-3 days → 30 seconds (99% reduction) |
| S&OP deck preparation | 6+ hours → 45 seconds (99% reduction) |
| Morning supply review | 45 minutes → 2 minutes (95% reduction) |
| Stockout detection | Reactive → 8-week predictive horizon |
| Contract compliance | Monthly spot-check → real-time continuous |
| Labor reporting | Manual end-of-week → daily automated (80% reduction) |
| Report formatting effort | 40% of planner time → zero (100% elimination) |
| Cross-site communication | English-only → native language (zero translation overhead) |

---

## 11. Roadmap

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Full prototype — mock data, all agent pipelines, 10 modules, trilingual UI | **PoC Complete** |
| Phase 2 | SAP/ERP data integration, live inventory feeds, Windchill PLM link | Q3 2026 |
| Phase 3 | MES integration (production actuals), LIMS quality data | Q4 2026 |
| Phase 4 | Automated PO creation (agent-initiated procurement) | Q1 2027 |
| Phase 5 | Predictive maintenance integration (IoT sensor feeds) | Q2 2027 |

---

## 12. Summary

ATLAS transforms Heroux-Devtek's supply chain planning from a fragmented, reactive, spreadsheet-driven process into a unified, AI-powered decision engine. By combining multi-agent orchestration with domain-specific aerospace knowledge (program rate impacts, titanium supply dynamics, NADCAP certification requirements, multi-facility production), the platform delivers measurable value across all 5 operational personas — from S&OP planners managing daily inventory decisions to leadership needing board-ready scenario analysis.

Key capabilities in v1.1:
- **Microsoft Agent Framework orchestration** — 4 specialists + orchestrator powered by GPT-5.4-mini and KIMI2.6
- **5-stage scenario pipeline** — quantitative what-if replacing 2-3 days of manual modeling
- **Trilingual operation** — complete EN/FR/ES coverage for global team collaboration
- **7 report templates** across PPTX/DOCX/PDF/XLSX with HD branding and zero formatting
- **Context-aware Atlas AI** — page-specific, language-aware conversational interface
- **300+ translated elements** — tables, charts, badges, dialogs, settings all adapt to language

The platform is designed to complement and augment existing ERP/MES systems rather than replace them, making it deployable alongside current workflows with minimal disruption.

---

*Prepared by Atlas AI Platform Team | Heroux-Devtek Inc. | June 2026*
