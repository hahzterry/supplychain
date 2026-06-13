import type { Lang } from '../i18n';

interface MultiLangChip {
  id: string;
  label: Record<Lang, string>;
  message: string;
}

interface PageContext {
  welcome: Record<Lang, string>;
  chips: MultiLangChip[];
}

const contexts: Record<string, PageContext> = {
  '/': {
    welcome: {
      en: "I'm Atlas AI — your aerospace supply chain copilot. Ask me about alerts, KPIs, inventory risks, or generate reports.",
      fr: "Je suis Atlas IA — votre copilote de chaîne d'approvisionnement aérospatiale. Interrogez-moi sur les alertes, KPI, risques d'inventaire ou générez des rapports.",
      es: "Soy Atlas IA — su copiloto de cadena de suministro aeroespacial. Pregunte sobre alertas, KPIs, riesgos de inventario o genere informes.",
    },
    chips: [
      { id: 'brief', label: { en: 'Morning supply brief', fr: 'Briefing matinal', es: 'Resumen matutino' }, message: 'Give me the morning supply brief' },
      { id: 'alerts', label: { en: 'Critical alerts', fr: 'Alertes critiques', es: 'Alertas críticas' }, message: 'Show me all critical supply chain alerts' },
      { id: 'kpis', label: { en: 'KPI dashboard', fr: 'Tableau de bord KPI', es: 'Panel KPI' }, message: 'Show me the current KPI dashboard overview' },
      { id: 'deck', label: { en: 'Generate S&OP deck', fr: 'Générer rapport S&OP', es: 'Generar informe S&OP' }, message: 'Generate the weekly S&OP presentation' },
    ],
  },
  '/demand-forecast': {
    welcome: {
      en: 'I can help you analyze demand patterns, forecast accuracy, and upcoming demand shifts across programs.',
      fr: "Je peux analyser les schémas de demande, la précision des prévisions et les évolutions à venir par programme.",
      es: 'Puedo ayudarle a analizar patrones de demanda, precisión de previsiones y cambios futuros por programa.',
    },
    chips: [
      { id: 'forecast_lg', label: { en: 'Landing gear forecast', fr: 'Prévision trains', es: 'Previsión trenes' }, message: 'Analyze the demand forecast for landing gear assemblies' },
      { id: 'forecast_accuracy', label: { en: 'Forecast accuracy', fr: 'Précision prévisions', es: 'Precisión previsiones' }, message: 'How accurate have our demand forecasts been this quarter?' },
      { id: 'demand_drivers', label: { en: 'Demand drivers', fr: 'Facteurs de demande', es: 'Factores de demanda' }, message: 'What are the key demand drivers for the next 8 weeks?' },
      { id: 'program_rates', label: { en: 'Program rate changes', fr: 'Changements de cadence', es: 'Cambios de cadencia' }, message: 'Are there any upcoming program rate changes affecting demand?' },
    ],
  },
  '/inventory-health': {
    welcome: {
      en: 'I can assess inventory risks, identify stockout candidates, and recommend rebalancing actions.',
      fr: "Je peux évaluer les risques d'inventaire, identifier les ruptures potentielles et recommander des actions de rééquilibrage.",
      es: 'Puedo evaluar riesgos de inventario, identificar candidatos a rotura y recomendar acciones de reequilibrio.',
    },
    chips: [
      { id: 'stockout_risk', label: { en: 'Stockout risks', fr: 'Risques de rupture', es: 'Riesgos de rotura' }, message: 'Which SKUs are at risk of stockout in the next 2 weeks?' },
      { id: 'excess', label: { en: 'Excess inventory', fr: 'Surstock', es: 'Exceso de inventario' }, message: 'Show me SKUs with excess inventory above 90 days of supply' },
      { id: 'abc_analysis', label: { en: 'ABC analysis', fr: 'Analyse ABC', es: 'Análisis ABC' }, message: 'Give me an ABC classification breakdown of current inventory' },
      { id: 'safety_stock', label: { en: 'Safety stock review', fr: 'Revue stock sécurité', es: 'Revisión stock seguridad' }, message: 'Which items have safety stock levels that need adjustment?' },
    ],
  },
  '/supply-network': {
    welcome: {
      en: 'I can evaluate supplier performance, identify supply constraints, and assess network resilience.',
      fr: "Je peux évaluer la performance des fournisseurs, identifier les contraintes et évaluer la résilience du réseau.",
      es: 'Puedo evaluar el rendimiento de proveedores, identificar restricciones y evaluar la resiliencia de la red.',
    },
    chips: [
      { id: 'constraints', label: { en: 'Supply constraints', fr: 'Contraintes', es: 'Restricciones' }, message: 'What are the current supply constraints across our network?' },
      { id: 'supplier_risk', label: { en: 'Supplier risk', fr: 'Risque fournisseur', es: 'Riesgo proveedor' }, message: 'Which suppliers are highest risk right now?' },
      { id: 'lead_times', label: { en: 'Lead time changes', fr: 'Évolution des délais', es: 'Cambios de plazos' }, message: 'Show me suppliers with recent lead time increases' },
      { id: 'alt_sources', label: { en: 'Alt sources', fr: 'Sources alternatives', es: 'Fuentes alternativas' }, message: 'Which critical materials have no alternative source qualified?' },
    ],
  },
  '/replenishment-plan': {
    welcome: {
      en: 'I can help prioritize purchase orders, expedite critical items, and optimize replenishment timing.',
      fr: "Je peux prioriser les bons de commande, accélérer les articles critiques et optimiser le réapprovisionnement.",
      es: 'Puedo priorizar órdenes de compra, acelerar artículos críticos y optimizar tiempos de reposición.',
    },
    chips: [
      { id: 'urgent_pos', label: { en: 'Urgent POs', fr: 'Commandes urgentes', es: 'POs urgentes' }, message: 'Which purchase orders need expediting this week?' },
      { id: 'reorder', label: { en: 'Reorder now', fr: 'Commander maintenant', es: 'Pedir ahora' }, message: 'What items have hit their reorder point and need ordering?' },
      { id: 'late_pos', label: { en: 'Late deliveries', fr: 'Livraisons en retard', es: 'Entregas tardías' }, message: 'Show me overdue purchase orders with delivery risk' },
      { id: 'cost_opt', label: { en: 'Cost optimization', fr: 'Optimisation coûts', es: 'Optimización costos' }, message: 'Are there consolidation opportunities to reduce freight costs?' },
    ],
  },
  '/production-priorities': {
    welcome: {
      en: 'I can help prioritize production runs, identify capacity bottlenecks, and balance workloads.',
      fr: "Je peux prioriser les ordres de fabrication, identifier les goulots de capacité et équilibrer les charges.",
      es: 'Puedo priorizar órdenes de producción, identificar cuellos de botella y equilibrar cargas de trabajo.',
    },
    chips: [
      { id: 'bottlenecks', label: { en: 'Bottlenecks', fr: 'Goulots', es: 'Cuellos de botella' }, message: 'What are the current production bottlenecks?' },
      { id: 'schedule', label: { en: "This week's schedule", fr: 'Planning semaine', es: 'Calendario semana' }, message: 'Show me the production schedule for this week' },
      { id: 'capacity', label: { en: 'Capacity gaps', fr: 'Écarts de capacité', es: 'Brechas de capacidad' }, message: 'Where do we have capacity gaps versus demand?' },
      { id: 'priorities', label: { en: 'Top priorities', fr: 'Priorités principales', es: 'Prioridades principales' }, message: 'What should be our top production priorities today?' },
    ],
  },
  '/scenario-planner': {
    welcome: {
      en: 'I can model supply chain disruptions, demand spikes, and what-if scenarios with full impact analysis.',
      fr: "Je peux modéliser les perturbations, pics de demande et scénarios hypothétiques avec analyse d'impact complète.",
      es: 'Puedo modelar disrupciones, picos de demanda y escenarios hipotéticos con análisis de impacto completo.',
    },
    chips: [
      { id: 'titanium', label: { en: 'Titanium disruption', fr: 'Perturbation titane', es: 'Disrupción titanio' }, message: 'What if titanium supply is disrupted by 60% for 3 months?' },
      { id: 'demand_surge', label: { en: 'Demand surge', fr: 'Pic de demande', es: 'Pico de demanda' }, message: 'Model a 40% demand surge across all A-class items' },
      { id: 'supplier_loss', label: { en: 'Supplier loss', fr: 'Perte fournisseur', es: 'Pérdida proveedor' }, message: 'What if we lose our primary forging supplier for 6 weeks?' },
      { id: 'rate_increase', label: { en: 'Rate increase', fr: 'Hausse de cadence', es: 'Aumento cadencia' }, message: 'Simulate an A220 program rate increase of 25%' },
    ],
  },
  '/labor-utilization': {
    welcome: {
      en: 'I can analyze workforce utilization, overtime trends, and identify staffing gaps or rebalancing needs.',
      fr: "Je peux analyser l'utilisation de la main-d'œuvre, les tendances d'heures supplémentaires et identifier les besoins en personnel.",
      es: 'Puedo analizar la utilización de la fuerza laboral, tendencias de horas extra e identificar brechas de personal.',
    },
    chips: [
      { id: 'utilization', label: { en: 'Current utilization', fr: 'Utilisation actuelle', es: 'Utilización actual' }, message: 'What is current labor utilization across all lines?' },
      { id: 'overtime', label: { en: 'Overtime trends', fr: "Tendances heures sup.", es: 'Tendencias horas extra' }, message: 'Show me overtime trends and which teams are over-extended' },
      { id: 'gaps', label: { en: 'Staffing gaps', fr: 'Écarts de personnel', es: 'Brechas de personal' }, message: 'Where do we have staffing gaps relative to planned production?' },
      { id: 'efficiency', label: { en: 'Efficiency metrics', fr: "Métriques d'efficacité", es: 'Métricas de eficiencia' }, message: 'What are our labor efficiency metrics by work center?' },
    ],
  },
  '/reports': {
    welcome: {
      en: "I can generate S&OP decks, inventory reports, executive summaries, and custom exports.",
      fr: "Je peux générer des présentations S&OP, rapports d'inventaire, résumés exécutifs et exports personnalisés.",
      es: 'Puedo generar presentaciones S&OP, informes de inventario, resúmenes ejecutivos y exportaciones personalizadas.',
    },
    chips: [
      { id: 'sop_deck', label: { en: 'S&OP deck', fr: 'Présentation S&OP', es: 'Presentación S&OP' }, message: 'Generate the weekly S&OP presentation' },
      { id: 'exec_summary', label: { en: 'Executive summary', fr: 'Résumé exécutif', es: 'Resumen ejecutivo' }, message: 'Generate an executive summary report for this week' },
      { id: 'inventory_report', label: { en: 'Inventory report', fr: "Rapport d'inventaire", es: 'Informe de inventario' }, message: 'Generate a detailed inventory health report in Excel' },
      { id: 'supply_report', label: { en: 'Supply risk report', fr: 'Rapport risque appro.', es: 'Informe riesgo suministro' }, message: 'Generate a supply risk assessment report' },
    ],
  },
  '/settings': {
    welcome: {
      en: 'I can help you configure thresholds, alert rules, and system preferences.',
      fr: "Je peux vous aider à configurer les seuils, règles d'alertes et préférences système.",
      es: 'Puedo ayudarle a configurar umbrales, reglas de alertas y preferencias del sistema.',
    },
    chips: [
      { id: 'thresholds', label: { en: 'Alert thresholds', fr: "Seuils d'alertes", es: 'Umbrales de alertas' }, message: 'What are the current alert threshold settings?' },
      { id: 'preferences', label: { en: 'My preferences', fr: 'Mes préférences', es: 'Mis preferencias' }, message: 'Show me my current notification and display preferences' },
    ],
  },
};

export function getPageContext(pathname: string): PageContext {
  return contexts[pathname] || contexts['/'];
}
