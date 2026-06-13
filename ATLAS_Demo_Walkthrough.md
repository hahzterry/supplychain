---
pdf_options:
  format: A4
  margin: 25mm
  displayHeaderFooter: true
  headerTemplate: '<div style="font-size:8px; width:100%; text-align:right; padding-right:25mm; color:#999;">ATLAS Supply Chain Intelligence — Demo Script</div>'
  footerTemplate: '<div style="font-size:8px; width:100%; text-align:center; color:#999;">Heroux-Devtek Inc. | Internal — Executive Review | Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
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
  blockquote { border-left: 4px solid #D4930D; background: #fdf8ee; padding: 10px 16px; margin: 16px 0; font-style: normal; }
  code { background: #f0e6cc; color: #6b5300; padding: 2px 5px; border-radius: 3px; font-size: 11px; }
  strong { color: #001f3f; }
---

# ATLAS — Aerospace Supply Chain Intelligence
# Demo Walkthrough & Presenter Script

**Duration:** 35-40 minutes  
**Audience:** Heroux-Devtek Leadership, S&OP Committee, IT/Digital teams  
**Presenter:** Platform team lead  
**Setup:** Frontend running at http://localhost:5174, backend on port 8001, browser full-screen  
**Pre-requisites:** Both servers running, fresh browser session

---

## Personas

| Persona | Role | Focus Areas |
|---------|------|-------------|
| **Sophie Tremblay** | S&OP Planning Manager, Longueuil | Daily operations, demand, inventory, replenishment |
| **Marc-Andre Gagnon** | VP Supply Chain | Executive decisions, risk escalation, board reporting |
| **Nadia Leclerc** | Procurement Manager | Contract compliance, supplier management, PO validation |
| **James Mitchell** | Operations Director, Springfield | Production scheduling, labor utilization, capacity |
| **Carlos Ruiz** | CESA Plant Manager, Getafe | Spanish-language operations, production, local reporting |

---

## Story Thread

> Today's demo follows a single cascading event: **TIMET, our primary titanium supplier, announces a 30% allocation cut effective immediately due to a furnace failure at their Henderson, Nevada facility.** We'll see how each persona discovers, quantifies, mitigates, and reports on this disruption — demonstrating how ATLAS transforms a multi-day manual fire drill into a 30-minute coordinated response.

---

## Introduction (2 min)

*[Open browser to login page — ATLAS logo, credentials form visible]*

**NARRATOR:**

> "Good morning. Today I'm demonstrating ATLAS — an AI-powered supply chain copilot built specifically for Heroux-Devtek's aerospace operations.
>
> ATLAS stands for Aerospace Tracking, Logistics & Analysis System. It serves five core personas across our 8 global facilities — from the S&OP planner managing daily inventory decisions in Longueuil, to the plant manager in Getafe running operations entirely in Spanish.
>
> The platform is built on a multi-agent AI architecture. At its center is Atlas AI — represented by this sparkle symbol ✦ — an orchestrator that routes queries to specialist agents running in parallel. A planner can ask a natural language question and receive quantitative analysis backed by real supply chain data in seconds.
>
> Today's story: TIMET just announced a 30% titanium allocation cut. Let's see how the team responds."

*[Login with demo credentials]*

---

## Act 1: S&OP Planner — Morning Discovery (5 min)

*[Login → Dashboard loads with KPI cards, sidebar shows active indicator on Dashboard]*

**NARRATOR:**

> "Meet Sophie Tremblay. She's the S&OP Planning Manager based in Longueuil — the person who lives in this platform every day. Her morning starts here on the Dashboard."

*[Point to the 8 KPI cards]*

> "Notice the KPI cards: Forecast Accuracy at 8.2% MAPE — green, within target. Inventory DOS at 42 days — healthy. Fill Rate 96.8%. But look here — Critical Alerts showing 5. That's new. Something happened overnight."

*[Point to the Atlas AI chat panel on the right side]*

> "The chat panel shows a welcome message specific to the Dashboard page: 'I'm Atlas AI — your aerospace supply chain copilot. Ask me about KPI trends, supply risks, or get your morning brief.' The suggestion chips below are also page-specific."

*[Click the chip: "Morning supply brief"]*

**NARRATOR:**

> "Watch the chat panel. I'm asking for the morning brief. Notice the planning block that appears — it shows the agent working: 'Atlas AI' using the 'morning_supply_brief' tool. This transparency lets Sophie know exactly what's happening behind the scenes."

*[Wait for streaming response]*

> "The response is structured: KPI summary, then critical alerts. And there it is — TIMET allocation cut flagged as the top risk. Atlas has already identified which SKUs are affected and estimated the DOS impact. In 10 seconds, Sophie knows exactly what her morning looks like."

*[Point to the follow-up suggestion chips that appear after the response]*

> "Notice the follow-up chips: 'Check inventory risk', 'Run what-if scenario'. Atlas suggests the logical next steps. Let's follow that thread."

---

## Act 2: S&OP Planner — Quantifying the Impact (6 min)

### Inventory Health Deep-Dive

*[Click "Inventory Health" in sidebar — note the active indicator moves]*

**NARRATOR:**

> "Sophie navigates to Inventory Health. Notice the sidebar — the left accent bar moves to indicate the current page. The chat panel's welcome message also changes: 'I can help you analyze inventory positions, identify at-risk SKUs, and track certification expiry.'"

*[Point to the Inventory Health page — risk distribution, table with DOS, risk badges]*

> "The table is sorted by days-of-supply — lowest first. Ti-6Al-4V Bar Stock is at the top with 18 DOS and a red 'Critical' badge. The allocation cut hasn't hit yet, but we're already thin."

*[Click the chip in chat panel — it now shows inventory-specific suggestions]*

> "The chips have changed for this page: 'SKUs below safety stock', 'Certification expiry risk', 'Critical inventory positions'. Each page gets relevant quick actions."

### Demand Forecast

*[Click "Demand Forecast" in sidebar]*

**NARRATOR:**

> "Now let's look at the demand side. The 8-week forecast shows projected demand for titanium-dependent SKUs."

*[Point to the area chart with confidence bands]*

> "The chart shows point forecast with 80% and 95% confidence intervals. Notice how the Y-axis scales properly to production volumes — hundreds of units per week, not single digits. The legend labels say 'CI 95%', 'CI 80%', 'Forecast' — all translatable."

> "The stat cards below show forecast accuracy, trend direction, and demand signals. Sophie can see that 777X program demand is trending up — which makes the titanium constraint even more urgent."

### Running the Scenario

*[Click "Scenario Planner" in sidebar]*

**NARRATOR:**

> "This is where ATLAS truly differentiates. The Scenario Planner runs a 5-stage AI pipeline to quantitatively model any what-if scenario. Look at the quick scenario chips."

*[Point to the translated chips: "Program Rate Increase: A220 +30%", "Forging Supplier Delay: 28 days", etc.]*

> "These are pre-built aerospace scenarios. But Sophie needs a custom one."

*[Type in the custom scenario input: "What if TIMET cuts Ti-6Al-4V allocation by 30% for the next 12 weeks while 777X program rate increases to 5/month?"]*

*[Click "Run Analysis"]*

**NARRATOR:**

> "Watch the pipeline progress indicator. Five stages execute in sequence:"

*[Point to the progress stages as they animate]*

> "1. **Scenario Planner** — classifies and structures the scenario
> 2. **Impact Analyzer** — quantitative modeling across demand, inventory, supply, production
> 3. **Mitigation Designer** — generates alternative supply and production options
> 4. **Risk Assessor** — probability and severity assessment
> 5. **Synthesizer** — executive summary with decision points
>
> In about 25 seconds, we have a complete analysis that would take a team 2-3 days manually."

*[Results load — point to the 4 tab layout]*

> "Four result tabs — let's walk through each."

#### Impact Summary Tab

*[Point to stat cards: Total Affected SKUs, Critical count, Avg Demand Increase]*

> "8 part numbers affected. 3 are critical — meaning stockout within 4 weeks. The KPI impact shows fill rate dropping from 96.8% to 89.2% if we do nothing. The bar chart compares baseline vs projected across each KPI."

#### Affected Part Numbers Tab

*[Click "Affected Part Numbers" tab]*

> "A severity-coded table. Each SKU shows baseline demand vs adjusted, the demand delta percentage, weeks until stockout, current DOS, and severity badge. The Ti-6Al-4V Bar Stock shows +67% effective demand increase with only 2.3 weeks to stockout. This is the data Sophie needs to escalate."

#### Stock Timeline Tab

*[Click "Stock Timeline" tab]*

> "Three charts. The first shows demand trajectory — baseline vs adjusted over 8 weeks. The second shows inventory depletion with a net position line that goes negative in Week 4. The third is a bar chart: stock vs demand, showing when demand outstrips available inventory."

#### Mitigation & Supply Tab

*[Click "Mitigation & Supply" tab]*

> "This is the action playbook. Mitigation options ranked by priority — each with cost in CAD, fill rate recovery percentage, and lead time. Below that: alternative suppliers with capacity, reliability scores, and cost premiums. And production capacity showing which lines have spare capacity for surge production."

*[Point to the Alternative Suppliers table]*

> "Aubert & Duval has 200 MT available capacity, 80-day lead time, 94% reliability, +12% cost premium. This is decision-ready data."

---

## Act 3: VP Supply Chain — Executive Escalation (5 min)

*[Narrator pauses — persona switch]*

**NARRATOR:**

> "Sophie has quantified the impact. Now she needs to escalate. Marc-Andre Gagnon, VP Supply Chain, opens ATLAS for his morning review."

*[Point to Dashboard — note same interface, same KPIs]*

> "Marc-Andre sees the same platform but asks different questions. He's not looking at individual SKUs — he wants portfolio impact and decision options."

*[Type in chat: "Give me an executive summary of the TIMET titanium situation — what's the financial exposure and what are my options?"]*

**NARRATOR:**

> "Atlas routes this to multiple agents. Watch the planning block — Inventory Risk, Supply Constraint, and the Scenario Pipeline all contribute. The response comes in executive format: financial exposure in CAD, program delivery risk by customer, and three option paths ranked by cost/risk trade-off."

*[Point to the structured response with bullet points, cost figures]*

> "Option 1: Emergency order from Aubert & Duval — CAD $180K premium, 80-day lead, covers 65% of gap. Option 2: Split between Aubert & Duval and Howmet — CAD $240K, covers 90%. Option 3: Production re-sequencing plus partial order — CAD $95K, buys 3 weeks while long-lead orders arrive."

### Generating the Board Report

*[Click "Reports" in sidebar]*

**NARRATOR:**

> "Marc-Andre needs to brief the executive team. The Report Builder offers 7 templates across 4 formats."

*[Point to the template cards: Weekly S&OP Review (PPTX), Executive S&OP Summary (DOCX/PDF), etc.]*

> "He selects 'Executive S&OP Summary' — this generates a DOCX with the current supply chain status, risk assessment, and recommended actions."

*[Click Generate on Executive S&OP Summary]*

> "The 5-agent pipeline runs: Planner, Content Writer, Designer, Critic, Repair. In about 45 seconds, a formatted document downloads — HD branding, navy/gold color scheme, ready to email to the CEO."

---

## Act 4: Procurement Manager — Supplier Action (5 min)

*[Narrator pauses — persona switch]*

**NARRATOR:**

> "Nadia Leclerc in Procurement needs to execute the mitigation. First — she validates that existing contracts support emergency ordering."

*[Click "Supply Network" in sidebar]*

> "The Supply Network page shows all 10 suppliers with lead times, reliability scores, and active orders. She can see TIMET's reliability has dropped — the allocation cut is already reflected."

*[Type in chat: "Validate pricing for an emergency Ti-6Al-4V order from Aubert & Duval — 200 MT at their quoted premium rate"]*

**NARRATOR:**

> "Atlas runs the Contract Price Validation tool. It checks the quoted price against the negotiated contract ceiling. The response confirms: within ceiling for emergency quantities, but flags that the premium rate exceeds standard pricing by 12% — within the authorized variance for supply disruptions per the contract terms."

*[Point to the structured response with pricing comparison]*

> "Nadia now has compliance confirmation. She can issue the PO knowing it won't trigger a contract breach flag later."

### Replenishment Plan

*[Click "Replenishment Plan" in sidebar]*

**NARRATOR:**

> "The Replenishment page shows AI-prioritized action cards. Each card has a SKU, urgency badge, recommended quantity, supplier, confidence level, and rationale."

*[Point to the top card — likely Ti-6Al-4V with "Critical" badge]*

> "The top recommendation: Emergency order — 200 MT Ti-6Al-4V Bar Stock from Aubert & Duval. Confidence: 92%. Rationale: TIMET allocation cut reduces DOS below safety stock by Week 3. Approval returns DOS to 38 days."

*[Click "Approve" on the action card — confirmation dialog appears]*

> "The confirmation dialog shows KPI impact: +18 DOS improvement, fill rate recovery to 94.1%. Translated button text — 'Approve' and 'Cancel'. One click to commit."

---

## Act 5: Operations Director — Production Response (5 min)

*[Narrator pauses — persona switch]*

**NARRATOR:**

> "James Mitchell runs operations at Springfield. The titanium constraint means some production lines may need re-sequencing. He needs to see which lines are affected and where he has capacity headroom."

### Production Priorities

*[Click "Production Priorities" in sidebar]*

> "The utilization chart shows all 8 production lines. Springfield Line A is at 91% — almost maxed. But Longueuil Line B is at 72% — there's headroom."

*[Point to the schedule table — line names, plants, capacity, current SKU, shifts]*

> "The schedule table shows which SKU each line is currently running. Springfield Line A is on Ti-6Al-4V MLG Cylinders — the exact SKU at risk. If material runs out, this line idles."

### Labor Utilization

*[Click "Labor Utilization" in sidebar]*

**NARRATOR:**

> "James checks labor readiness. If he needs to surge production at Longueuil, does the workforce support it?"

*[Point to KPI cards: Average Efficiency, Direct Labor %, Total Headcount, Overtime Hours]*

> "Four KPI cards give the instant picture. Average efficiency 87% — above target. But look at overtime: already at 12% across the portfolio."

*[Point to the facility comparison bar chart]*

> "The efficiency chart covers all 8 facilities — Longueuil, Kitchener, Springfield, Nottingham, Laval, Livonia, Getafe, Seville. Longueuil is at 91% — excellent. Springfield at 84% — acceptable but tight."

*[Point to the filterable table]*

> "The daily records table is filterable by facility and shift. James filters to Longueuil — he can see headcount by skill category, direct vs indirect hours, and overtime. The data confirms: Longueuil has capacity for surge without excessive overtime."

*[Type in chat: "Can Longueuil absorb a 25% production increase on Ti-6Al-4V lines if we re-route from Springfield?"]*

> "Atlas analyzes labor availability, line capacity, and skill mix. The answer: yes, Longueuil can absorb with one additional shift, requiring 8 overtime hours per day for 3 weeks. Cost impact: CAD $45K in overtime premium."

---

## Act 6: CESA Plant Manager — Spanish Operations (4 min)

*[Narrator pauses — persona switch]*

**NARRATOR:**

> "Now we demonstrate something unique. Carlos Ruiz manages the Getafe facility in Spain. His team works in Spanish. Watch what happens when he switches language."

*[Click the language toggle in the sidebar — cycle to ES]*

**NARRATOR:**

> "One click. The entire interface switches to Spanish. Let me point out what changed:"

*[Point to each translated element]*

> "- Navigation tooltips: 'Panel de control', 'Prevision de demanda', 'Salud del inventario'
> - KPI card titles: 'Precision del pronostico', 'Dias de suministro'
> - The chat welcome message: 'Soy Atlas IA — su copiloto de cadena de suministro aeroespacial...'
> - Suggestion chips: 'Resumen matutino de suministro', 'Verificar riesgos de suministro'
> - Table column headers, chart legends, badge text — everything."

*[Click "Planificador de escenarios" (Scenario Planner) in sidebar]*

> "Even the Scenario Planner chips are in Spanish: 'Aumento cadencia: A220 +30%', 'Retraso proveedor forja: 28 dias'."

*[Click the first chip]*

**NARRATOR:**

> "Watch carefully. The chip label was in Spanish, but the message sent to Atlas AI is in English — 'Simulate a 30% program rate increase for A220 affecting landing gear assemblies.' This is by design. The LLM reasons better in English, but Atlas detects Carlos's language preference and responds entirely in Spanish."

*[Wait for response]*

> "The response comes in Spanish. The result tabs are also fully translated: 'Resumen de impacto', 'Numeros de pieza afectados', 'Cronologia de stock', 'Mitigacion y suministro'. Every table header, chart legend, badge, and label — Spanish throughout."

*[Click "Mitigacion y suministro" tab]*

> "'Opciones de mitigacion', 'Costo: CAD...', 'Recuperacion tasa servicio', 'Plazo: ... dias'. Carlos's team can make decisions in their native language without translation delays."

*[Switch language back to EN]*

> "And one click back to English. The platform is truly trilingual — every element, not just navigation labels."

---

## Act 7: S&OP Planner — Scenario History & Comparison (3 min)

*[Navigate to Scenario Planner — scroll to History section]*

**NARRATOR:**

> "Back to Sophie. She's run several scenarios this week. The Scenario History table stores every analysis with scenario type, affected SKU count, and date."

*[Point to the history table with checkboxes]*

> "She can select any two scenarios for comparison. Let's compare the TIMET 30% cut scenario against last week's 'A220 rate increase' scenario."

*[Check two scenarios → Click "Compare Selected"]*

> "The Scenario Comparison shows KPI-by-KPI comparison: fill rate, DOS, stockout risk — with Scenario A values, Scenario B values, and the delta. Green for improvement, red for degradation. This is the quantitative basis for her S&OP meeting recommendation."

---

## Act 8: Generating Reports & Documents (4 min)

*[Click "Reports" in sidebar]*

**NARRATOR:**

> "The Report Builder is where everything comes together. Seven templates serve different needs."

*[Point to the template grid]*

| Template | Format | Audience |
|----------|--------|----------|
| Weekly S&OP Review | PPTX (10 slides) | S&OP Committee |
| Inventory Status | PPTX | Inventory team |
| Demand Accuracy | PPTX | Demand planning |
| Executive S&OP Summary | DOCX/PDF | Leadership |
| Inventory Deep-Dive | DOCX/PDF | Analysts |
| Replenishment Plan | XLSX | Procurement |
| Supplier Scorecard | XLSX | Supplier management |

*[Click "Generate" on Weekly S&OP Review PPTX]*

**NARRATOR:**

> "The 5-agent pipeline runs for the PPTX:
> 1. **Planner** — outlines 10 slides with section allocation
> 2. **Content Writer** — generates narrative for each slide
> 3. **Designer** — applies HD navy/gold branding, chart layouts
> 4. **Critic** — reviews for completeness, accuracy, executive tone
> 5. **Repair** — fixes any issues flagged by the critic
>
> The progress indicator shows each stage. In about 45 seconds..."

*[Wait for download]*

> "A 10-slide branded PPTX downloads. HD logo, navy headers, gold accents. KPI overview, risk matrix, demand outlook, inventory positions, supplier status, production utilization, recommended actions — all current data, zero formatting effort."

*[Open the downloaded PPTX briefly if time allows]*

> "This replaced 6+ hours of manual deck preparation. Every week."

---

## Act 9: Settings & Platform Configuration (2 min)

*[Click "Settings" in sidebar]*

**NARRATOR:**

> "Quick look at Settings. Three key configurations:"

*[Point to each setting]*

> "1. **Language** — EN / FR / ES. Changes apply immediately across the entire platform. All labels, charts, tables, badges, chat messages, and AI responses adapt.
>
> 2. **Notifications** — Toggle email alerts for critical inventory, supplier delays, certification expiry.
>
> 3. **Default view preferences** — Table density, chart animation, timezone for global teams."

> "The settings page itself is fully translated — proof that the i18n system covers even administrative interfaces."

---

## Closing — Platform Summary (2 min)

*[Return to Dashboard]*

**NARRATOR:**

> "Let me summarize what we demonstrated in 35 minutes:
>
> 1. **Morning discovery** — Atlas AI surfaced the titanium risk proactively within 10 seconds
>
> 2. **Quantitative impact analysis** — 5-stage scenario pipeline modeled demand impact, inventory depletion, and production disruption across 8 SKUs in 25 seconds
>
> 3. **Executive escalation** — VP received portfolio-level financial exposure and ranked options instantly
>
> 4. **Procurement validation** — Contract compliance confirmed before emergency order issued
>
> 5. **Operations readiness** — Labor and production capacity verified for surge production
>
> 6. **Trilingual operations** — CESA Spain team works natively in Spanish with zero translation friction
>
> 7. **Scenario comparison** — Historical what-if analyses compared quantitatively for S&OP decisions
>
> 8. **Automated reporting** — 7 templates across PPTX/DOCX/PDF/XLSX, generated by AI pipelines in under a minute
>
> The thread that ties it all together: a single supply disruption was discovered, quantified, escalated, mitigated, and reported — across 5 personas in 5 different functional areas — in the time it used to take one person to open the right spreadsheet.
>
> ATLAS doesn't replace the supply chain team. It gives them superpowers."

---

## Demo Tips & Recovery

### Best Demo Flow

Follow the story thread: **Discovery → Quantify → Escalate → Execute → Report**. This maps naturally to the personas and shows how ATLAS connects workflows.

### If the AI Agent Errors

- Click "↺ New Session" in chat and retry
- Each query is stateless — no accumulated context needed
- Rephrase if the response seems off-topic

### Strongest Visual Moments

| Moment | Why It Works |
|--------|-------------|
| Scenario pipeline progress | Shows real multi-agent orchestration in real-time |
| Language switch (full page) | Immediate visual proof of trilingual depth |
| Mitigation tab data | Decision-ready: costs, suppliers, lead times in one view |
| PPTX download + open | Tangible output — "this used to take 6 hours" |
| Active page indicator | Subtle but polished — shows production-quality UI |

### What to Emphasize

- **"30 seconds vs 3 days"** — Scenario analysis time reduction
- **"Zero formatting"** — Report generation eliminates busywork
- **"One platform, three languages"** — Global team enablement
- **"AI drives it, doesn't decorate it"** — Every page is an Atlas workflow
- **"Decision-ready, not data-ready"** — Outputs include recommendations, not just charts

### What to Avoid

- Don't demo Settings unless audience asks — it's not visually compelling
- Don't switch personas too rapidly — let each moment land
- Don't explain the technology stack unless IT is the audience
- Don't apologize for mock data — say "synthetic data for the PoC, agent intelligence is production-ready"

### Audience-Specific Emphasis

| Audience | Emphasize |
|----------|-----------|
| **CEO / Board** | Financial impact numbers, time savings, competitive advantage |
| **S&OP Committee** | Scenario comparison, replenishment approval workflow, report automation |
| **IT / Digital** | Multi-agent architecture, SSE streaming, i18n implementation, scalability |
| **Operations** | Labor utilization, production re-sequencing, facility comparison |
| **Procurement** | Contract validation, supplier reliability, PO compliance |
| **CESA Spain** | Full Spanish demo — switch language first, never switch back |

---

## Quick Reference — Chat Commands by Page

| Page | Best Demo Query | What It Shows |
|------|-----------------|---------------|
| Dashboard | "Morning supply brief" | Multi-KPI summary + risk flagging |
| Demand Forecast | "What's the 8-week outlook for titanium SKUs?" | Forecast with confidence bands |
| Inventory Health | "Which SKUs are below safety stock?" | Risk scoring + DOS analysis |
| Supply Network | "Show supplier reliability rankings" | Performance monitoring |
| Scenario Planner | Custom: "What if TIMET cuts allocation 30%..." | Full 5-stage pipeline |
| Replenishment | "What should I order this week?" | Prioritized action cards |
| Production | "Which lines have capacity for surge?" | Utilization + headroom |
| Labor | "Compare efficiency across all sites" | 8-facility visualization |
| Reports | Click any "Generate" button | Multi-agent document pipeline |

---

## Persona Capabilities Matrix

| Capability | S&OP Planner | VP Supply Chain | Procurement | Operations | CESA PM |
|-----------|:---:|:---:|:---:|:---:|:---:|
| KPI Dashboard | ✓ | ✓ | ✓ | ✓ | ✓ |
| Demand Forecast | ✓ | ✓ | | | ✓ |
| Inventory Health | ✓ | ✓ | ✓ | | ✓ |
| Supply Network | ✓ | ✓ | ✓ | ✓ | ✓ |
| Scenario Planner | ✓ | ✓ | | ✓ | ✓ |
| Replenishment | ✓ | | ✓ | | |
| Production | | | | ✓ | ✓ |
| Labor Utilization | | ✓ | | ✓ | ✓ |
| Reports | ✓ | ✓ | ✓ | ✓ | ✓ |
| Language | EN/FR | EN/FR | EN/FR | EN | ES |

---

*End of Demo Script*

*Prepared for Heroux-Devtek Inc. — Internal Use Only*  
*ATLAS v1.1 — June 2026*
