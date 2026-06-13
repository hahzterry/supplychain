import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

export type Lang = 'en' | 'fr' | 'es';

interface I18nContextType {
  lang: Lang;
  dir: 'ltr' | 'rtl';
  setLang: (lang: Lang) => void;
  t: (key: string) => string;
}

const translations: Record<string, Record<Lang, string>> = {
  'app.name': { en: 'ATLAS', fr: 'ATLAS', es: 'ATLAS' },
  'app.subtitle': { en: 'Aerospace Supply Chain Intelligence', fr: 'Intelligence de la chaîne d\'approvisionnement aérospatiale', es: 'Inteligencia de la cadena de suministro aeroespacial' },
  'app.welcome': { en: 'Good morning. Here\'s your daily supply chain briefing.', fr: 'Bonjour. Voici votre briefing quotidien de la chaîne d\'approvisionnement.', es: 'Buenos días. Aquí está su resumen diario de la cadena de suministro.' },

  'nav.dashboard': { en: 'Dashboard', fr: 'Tableau de bord', es: 'Panel de control' },
  'nav.demandForecast': { en: 'Demand Forecast', fr: 'Prévisions de la demande', es: 'Previsión de demanda' },
  'nav.inventoryHealth': { en: 'Inventory Health', fr: 'Santé des stocks', es: 'Salud del inventario' },
  'nav.supplyNetwork': { en: 'Supply Network', fr: 'Réseau d\'approvisionnement', es: 'Red de suministro' },
  'nav.replenishment': { en: 'Replenishment Plan', fr: 'Plan de réapprovisionnement', es: 'Plan de reposición' },
  'nav.production': { en: 'Production Priorities', fr: 'Priorités de production', es: 'Prioridades de producción' },
  'nav.scenarios': { en: 'Scenario Planner', fr: 'Planificateur de scénarios', es: 'Planificador de escenarios' },
  'nav.reports': { en: 'Reports & Exports', fr: 'Rapports et exportations', es: 'Informes y exportaciones' },
  'nav.settings': { en: 'Settings', fr: 'Paramètres', es: 'Configuración' },
  'nav.labor': { en: 'Labor Utilization', fr: 'Utilisation de la main-d\'œuvre', es: 'Utilización de mano de obra' },

  'dashboard.title': { en: 'Supply Chain Dashboard', fr: 'Tableau de bord de la chaîne d\'approvisionnement', es: 'Panel de la cadena de suministro' },
  'dashboard.forecastAccuracy': { en: 'Forecast Accuracy', fr: 'Précision des prévisions', es: 'Precisión de previsiones' },
  'dashboard.inventoryDOS': { en: 'Avg Days of Supply', fr: 'Jours moyens d\'approvisionnement', es: 'Días promedio de suministro' },
  'dashboard.fillRate': { en: 'Fill Rate', fr: 'Taux de remplissage', es: 'Tasa de cumplimiento' },
  'dashboard.stockoutRate': { en: 'Stockout Rate', fr: 'Taux de rupture', es: 'Tasa de rotura de stock' },
  'dashboard.criticalAlerts': { en: 'Critical Alerts', fr: 'Alertes critiques', es: 'Alertas críticas' },
  'dashboard.pendingActions': { en: 'Pending Actions', fr: 'Actions en attente', es: 'Acciones pendientes' },
  'dashboard.demandHeatmap': { en: 'Demand Signals by Category', fr: 'Signaux de demande par catégorie', es: 'Señales de demanda por categoría' },
  'dashboard.riskOverview': { en: 'Inventory Risk Overview', fr: 'Aperçu des risques d\'inventaire', es: 'Resumen de riesgos de inventario' },
  'dashboard.quickActions': { en: 'Quick Actions', fr: 'Actions rapides', es: 'Acciones rápidas' },
  'dashboard.runBrief': { en: 'Morning Brief', fr: 'Briefing matinal', es: 'Resumen matutino' },
  'dashboard.briefDesc': { en: 'Get today\'s supply chain summary', fr: 'Obtenir le résumé quotidien de la chaîne d\'approvisionnement', es: 'Obtener el resumen diario de la cadena de suministro' },
  'dashboard.checkRisks': { en: 'Check Risks', fr: 'Vérifier les risques', es: 'Verificar riesgos' },
  'dashboard.riskDesc': { en: 'Review stockout & excess risks', fr: 'Examiner les risques de rupture et d\'excès', es: 'Revisar riesgos de rotura y exceso' },
  'dashboard.genReport': { en: 'S&OP Report', fr: 'Rapport S&OP', es: 'Informe S&OP' },
  'dashboard.reportDesc': { en: 'Generate weekly S&OP deck', fr: 'Générer le rapport S&OP hebdomadaire', es: 'Generar informe S&OP semanal' },

  'demand.title': { en: 'Demand Forecast', fr: 'Prévisions de la demande', es: 'Previsión de demanda' },
  'demand.subtitle': { en: 'Program-level demand forecasts with confidence intervals and rate overlays.', fr: 'Prévisions de la demande au niveau programme avec intervalles de confiance et superpositions de cadence.', es: 'Previsiones de demanda a nivel de programa con intervalos de confianza y superposiciones de cadencia.' },
  'demand.selectSku': { en: 'Select Part Number', fr: 'Sélectionner le numéro de pièce', es: 'Seleccionar número de pieza' },
  'demand.confidence': { en: 'Confidence', fr: 'Confiance', es: 'Confianza' },
  'demand.accuracy': { en: 'Forecast Accuracy (MAPE)', fr: 'Précision des prévisions (MAPE)', es: 'Precisión de previsiones (MAPE)' },

  'inventory.title': { en: 'Inventory Health', fr: 'Santé des stocks', es: 'Salud del inventario' },
  'inventory.subtitle': { en: 'Stock positions, aging analysis, and risk matrix across all part numbers.', fr: 'Positions de stock, analyse du vieillissement et matrice de risques pour tous les numéros de pièces.', es: 'Posiciones de stock, análisis de antigüedad y matriz de riesgos para todos los números de pieza.' },
  'inventory.riskMatrix': { en: 'Risk Matrix', fr: 'Matrice de risques', es: 'Matriz de riesgos' },
  'inventory.positions': { en: 'Stock Positions', fr: 'Positions de stock', es: 'Posiciones de stock' },
  'inventory.critical': { en: 'Critical', fr: 'Critique', es: 'Crítico' },
  'inventory.warning': { en: 'Warning', fr: 'Avertissement', es: 'Advertencia' },
  'inventory.normal': { en: 'Normal', fr: 'Normal', es: 'Normal' },
  'inventory.excess': { en: 'Excess', fr: 'Excédent', es: 'Exceso' },

  'supply.title': { en: 'Supply Network', fr: 'Réseau d\'approvisionnement', es: 'Red de suministro' },
  'supply.subtitle': { en: 'Supplier performance, lead times, and production capacity.', fr: 'Performance des fournisseurs, délais de livraison et capacité de production.', es: 'Rendimiento de proveedores, plazos de entrega y capacidad de producción.' },
  'supply.suppliers': { en: 'Suppliers', fr: 'Fournisseurs', es: 'Proveedores' },
  'supply.capacity': { en: 'Plant Capacity', fr: 'Capacité de l\'usine', es: 'Capacidad de planta' },
  'supply.openPOs': { en: 'Open Purchase Orders', fr: 'Bons de commande ouverts', es: 'Órdenes de compra abiertas' },

  'replenishment.title': { en: 'Replenishment Plan', fr: 'Plan de réapprovisionnement', es: 'Plan de reposición' },
  'replenishment.subtitle': { en: 'AI-recommended actions with scenario comparison and KPI impact.', fr: 'Actions recommandées par l\'IA avec comparaison de scénarios et impact sur les KPI.', es: 'Acciones recomendadas por IA con comparación de escenarios e impacto en KPI.' },
  'replenishment.approve': { en: 'Approve', fr: 'Approuver', es: 'Aprobar' },
  'replenishment.dismiss': { en: 'Dismiss', fr: 'Rejeter', es: 'Descartar' },
  'replenishment.scenarioCompare': { en: 'Scenario Comparison', fr: 'Comparaison de scénarios', es: 'Comparación de escenarios' },

  'production.title': { en: 'Production Priorities', fr: 'Priorités de production', es: 'Prioridades de producción' },
  'production.subtitle': { en: 'Manufacturing schedule, capacity utilization, and AI recommendations.', fr: 'Calendrier de fabrication, utilisation de la capacité et recommandations de l\'IA.', es: 'Calendario de fabricación, utilización de capacidad y recomendaciones de IA.' },
  'production.schedule': { en: 'Production Schedule', fr: 'Calendrier de production', es: 'Calendario de producción' },
  'production.utilization': { en: 'Capacity Utilization', fr: 'Utilisation de la capacité', es: 'Utilización de capacidad' },

  'labor.title': { en: 'Daily Labor Utilization', fr: 'Utilisation quotidienne de la main-d\'œuvre', es: 'Utilización diaria de mano de obra' },
  'labor.subtitle': { en: 'Shift-level labor tracking, efficiency metrics, and skill allocation.', fr: 'Suivi de la main-d\'œuvre par quart, indicateurs d\'efficacité et allocation des compétences.', es: 'Seguimiento de mano de obra por turno, métricas de eficiencia y asignación de habilidades.' },

  'scenarios.title': { en: 'Scenario Planner', fr: 'Planificateur de scénarios', es: 'Planificador de escenarios' },
  'scenarios.subtitle': { en: 'What-if analysis for program rate increases, forging delays, and AOG emergencies.', fr: 'Analyse de scénarios pour augmentations de cadence, retards de forgeage et urgences AOG.', es: 'Análisis hipotético para aumentos de cadencia, retrasos de forja y emergencias AOG.' },
  'scenarios.demandSpike': { en: 'Program Rate Increase', fr: 'Augmentation de cadence programme', es: 'Aumento de cadencia de programa' },
  'scenarios.supplierDelay': { en: 'Forging Delay', fr: 'Retard de forgeage', es: 'Retraso de forja' },
  'scenarios.promotion': { en: 'AOG Emergency', fr: 'Urgence AOG', es: 'Emergencia AOG' },
  'scenarios.capacityLoss': { en: 'Capacity Loss', fr: 'Perte de capacité', es: 'Pérdida de capacidad' },
  'scenarios.runScenario': { en: 'Run Scenario', fr: 'Exécuter le scénario', es: 'Ejecutar escenario' },
  'scenarios.impactSummary': { en: 'Impact Summary', fr: 'Résumé de l\'impact', es: 'Resumen de impacto' },
  'scenarios.affectedSkus': { en: 'Affected Part Numbers', fr: 'Numéros de pièces affectés', es: 'Números de pieza afectados' },
  'scenarios.mitigation': { en: 'Mitigation & Supply', fr: 'Atténuation et approvisionnement', es: 'Mitigación y suministro' },
  'scenarios.timeline': { en: 'Stock Timeline', fr: 'Chronologie des stocks', es: 'Cronología de stock' },
  'scenarios.kpiComparison': { en: 'KPI Comparison', fr: 'Comparaison des KPI', es: 'Comparación de KPI' },
  'scenarios.riskAssessment': { en: 'Risk Assessment', fr: 'Évaluation des risques', es: 'Evaluación de riesgos' },
  'scenarios.recommendations': { en: 'Recommended Actions', fr: 'Actions recommandées', es: 'Acciones recomendadas' },
  'scenarios.critical': { en: 'Critical', fr: 'Critique', es: 'Crítico' },
  'scenarios.warning': { en: 'Warning', fr: 'Avertissement', es: 'Advertencia' },
  'scenarios.safe': { en: 'Safe', fr: 'Sûr', es: 'Seguro' },

  'reports.title': { en: 'Reports & Exports', fr: 'Rapports et exportations', es: 'Informes y exportaciones' },
  'reports.subtitle': { en: 'Generate S&OP reports in PowerPoint, Word, Excel, or PDF.', fr: 'Générer des rapports S&OP en PowerPoint, Word, Excel ou PDF.', es: 'Generar informes S&OP en PowerPoint, Word, Excel o PDF.' },
  'reports.selectTemplate': { en: 'Select Template', fr: 'Sélectionner le modèle', es: 'Seleccionar plantilla' },
  'reports.generate': { en: 'Generate Report', fr: 'Générer le rapport', es: 'Generar informe' },
  'reports.recent': { en: 'Recent Reports', fr: 'Rapports récents', es: 'Informes recientes' },
  'reports.sections': { en: 'Sections', fr: 'Sections', es: 'Secciones' },
  'reports.config': { en: 'Configuration', fr: 'Configuration', es: 'Configuración' },
  'reports.confirmTitle': { en: 'Confirm Report Generation', fr: 'Confirmer la génération du rapport', es: 'Confirmar generación de informe' },
  'reports.addContext': { en: 'Additional context or instructions (optional)', fr: 'Contexte ou instructions supplémentaires (facultatif)', es: 'Contexto o instrucciones adicionales (opcional)' },
  'reports.contextPlaceholder': { en: 'e.g., Focus on landing gear program, include titanium supply risk...', fr: 'ex. : Se concentrer sur le programme de trains d\'atterrissage, inclure le risque d\'approvisionnement en titane...', es: 'ej.: Enfocarse en el programa de tren de aterrizaje, incluir riesgo de suministro de titanio...' },
  'reports.cancel': { en: 'Cancel', fr: 'Annuler', es: 'Cancelar' },
  'reports.feedbackTitle': { en: 'Regenerate with Feedback', fr: 'Régénérer avec commentaires', es: 'Regenerar con comentarios' },
  'reports.overallChanges': { en: 'Overall changes requested', fr: 'Modifications globales demandées', es: 'Cambios generales solicitados' },
  'reports.sectionFeedback': { en: 'Per-section feedback (optional)', fr: 'Commentaires par section (facultatif)', es: 'Comentarios por sección (opcional)' },
  'reports.sectionPlaceholder': { en: 'What to change in this section...', fr: 'Ce qu\'il faut modifier dans cette section...', es: 'Qué cambiar en esta sección...' },
  'reports.regenerateWithFeedback': { en: 'Regenerate', fr: 'Régénérer', es: 'Regenerar' },

  'settings.title': { en: 'Settings', fr: 'Paramètres', es: 'Configuración' },
  'settings.language': { en: 'Language', fr: 'Langue', es: 'Idioma' },
  'settings.alertPrefs': { en: 'Alert Preferences', fr: 'Préférences d\'alerte', es: 'Preferencias de alertas' },
  'settings.dataSources': { en: 'Data Sources', fr: 'Sources de données', es: 'Fuentes de datos' },

  'common.search': { en: 'Ask Atlas anything... "What\'s the AOG risk?" or "Validate PO pricing"', fr: 'Demandez à Atlas... "Quel est le risque AOG?" ou "Valider les prix PO"', es: 'Pregunte a Atlas... "¿Cuál es el riesgo AOG?" o "Validar precios de OC"' },
  'common.aiAssistant': { en: 'Atlas AI', fr: 'Atlas IA', es: 'Atlas IA' },

  'chat.welcome': { en: 'Hi, I\'m Atlas — your AI aerospace supply chain analyst. I can analyze program demand, check inventory risks, validate contracts and PO pricing, track labor utilization, or generate S&OP reports. What would you like to review?', fr: 'Bonjour, je suis Atlas — votre analyste IA de la chaîne d\'approvisionnement aérospatiale. Je peux analyser la demande des programmes, vérifier les risques d\'inventaire, valider les contrats et les prix des bons de commande, suivre l\'utilisation de la main-d\'œuvre ou générer des rapports S&OP. Que souhaitez-vous examiner ?', es: 'Hola, soy Atlas — su analista IA de la cadena de suministro aeroespacial. Puedo analizar la demanda de programas, verificar riesgos de inventario, validar contratos y precios de órdenes de compra, rastrear la utilización de mano de obra o generar informes S&OP. ¿Qué desea revisar?' },
  'chat.ask': { en: 'Ask Atlas...', fr: 'Demandez à Atlas...', es: 'Pregunte a Atlas...' },
  'chat.newSession': { en: 'New Session', fr: 'Nouvelle session', es: 'Nueva sesión' },

  'ticker.live': { en: 'LIVE', fr: 'EN DIRECT', es: 'EN VIVO' },
  'ticker.supplyAlerts': { en: 'Supply Alerts', fr: 'Alertes d\'approvisionnement', es: 'Alertas de suministro' },

  'actions.title': { en: 'Atlas Recommended Actions', fr: 'Actions recommandées par Atlas', es: 'Acciones recomendadas por Atlas' },
  'actions.approve': { en: 'Approve', fr: 'Approuver', es: 'Aprobar' },
  'actions.dismiss': { en: 'Dismiss', fr: 'Rejeter', es: 'Descartar' },

  // Common table headers & labels
  'common.loading': { en: 'Loading...', fr: 'Chargement...', es: 'Cargando...' },
  'common.sku': { en: 'SKU', fr: 'Réf.', es: 'SKU' },
  'common.category': { en: 'Category', fr: 'Catégorie', es: 'Categoría' },
  'common.date': { en: 'Date', fr: 'Date', es: 'Fecha' },
  'common.facility': { en: 'Facility', fr: 'Site', es: 'Instalación' },
  'common.supplier': { en: 'Supplier', fr: 'Fournisseur', es: 'Proveedor' },
  'common.country': { en: 'Country', fr: 'Pays', es: 'País' },
  'common.leadTime': { en: 'Lead Time', fr: 'Délai', es: 'Plazo' },
  'common.reliability': { en: 'Reliability', fr: 'Fiabilité', es: 'Fiabilidad' },
  'common.orders': { en: 'Orders', fr: 'Commandes', es: 'Pedidos' },
  'common.plant': { en: 'Plant', fr: 'Usine', es: 'Planta' },
  'common.line': { en: 'Line', fr: 'Ligne', es: 'Línea' },
  'common.utilization': { en: 'Utilization', fr: 'Utilisation', es: 'Utilización' },
  'common.capacity': { en: 'Capacity (units/day)', fr: 'Capacité (unités/jour)', es: 'Capacidad (unidades/día)' },
  'common.currentSku': { en: 'Current SKU', fr: 'Réf. en cours', es: 'SKU actual' },
  'common.shifts': { en: 'Shifts', fr: 'Quarts', es: 'Turnos' },
  'common.maintenance': { en: 'Maintenance', fr: 'Maintenance', es: 'Mantenimiento' },
  'common.none': { en: 'None', fr: 'Aucun', es: 'Ninguno' },
  'common.cancel': { en: 'Cancel', fr: 'Annuler', es: 'Cancelar' },
  'common.close': { en: 'Close', fr: 'Fermer', es: 'Cerrar' },
  'common.dos': { en: 'DOS', fr: 'JAS', es: 'DAS' },
  'common.stock': { en: 'Stock', fr: 'Stock', es: 'Stock' },
  'common.risk': { en: 'Risk', fr: 'Risque', es: 'Riesgo' },
  'common.shelfLife': { en: 'Shelf Life', fr: 'Durée de vie', es: 'Vida útil' },
  'common.skus': { en: 'SKUs', fr: 'Réfs', es: 'SKUs' },
  'common.allFacilities': { en: 'All Facilities', fr: 'Tous les sites', es: 'Todas las instalaciones' },
  'common.processing': { en: 'Processing...', fr: 'Traitement...', es: 'Procesando...' },
  'common.connectionError': { en: 'Connection error', fr: 'Erreur de connexion', es: 'Error de conexión' },
  'common.errorOccurred': { en: 'An error occurred', fr: 'Une erreur est survenue', es: 'Se produjo un error' },

  // Dashboard chips & targets
  'dashboard.chip.brief': { en: 'Morning supply brief', fr: 'Briefing matinal', es: 'Resumen matutino' },
  'dashboard.chip.alerts': { en: 'Critical alerts', fr: 'Alertes critiques', es: 'Alertas críticas' },
  'dashboard.chip.kpi': { en: 'Weekly KPI summary', fr: 'Résumé KPI hebdomadaire', es: 'Resumen KPI semanal' },
  'dashboard.chip.risk': { en: 'Inventory risk overview', fr: 'Aperçu des risques', es: 'Resumen de riesgos' },
  'dashboard.target.mape': { en: 'Target: < 15%', fr: 'Cible : < 15%', es: 'Objetivo: < 15%' },
  'dashboard.target.dos': { en: 'Target: 14-21 days', fr: 'Cible : 14-21 jours', es: 'Objetivo: 14-21 días' },
  'dashboard.target.fill': { en: 'Target: > 97%', fr: 'Cible : > 97%', es: 'Objetivo: > 97%' },
  'dashboard.target.stockout': { en: 'Target: < 2%', fr: 'Cible : < 2%', es: 'Objetivo: < 2%' },

  // Demand forecast
  'demand.chip.accuracy': { en: 'Forecast accuracy trends', fr: 'Tendances de précision', es: 'Tendencias de precisión' },
  'demand.chip.spikes': { en: 'Demand spike risks', fr: 'Risques de pics de demande', es: 'Riesgos de picos de demanda' },
  'demand.chip.seasonal': { en: 'Seasonal patterns', fr: 'Schémas saisonniers', es: 'Patrones estacionales' },
  'demand.chip.program': { en: 'A320 program forecast', fr: 'Prévision programme A320', es: 'Previsión programa A320' },
  'demand.viewSkuDetail': { en: 'View SKU Detail', fr: 'Voir détail pièce', es: 'Ver detalle pieza' },
  'demand.chartTitle': { en: '8-Week Forecast with Confidence Bands', fr: 'Prévision 8 semaines avec bandes de confiance', es: 'Previsión 8 semanas con bandas de confianza' },
  'demand.ci95': { en: '95% CI', fr: 'IC 95%', es: 'IC 95%' },
  'demand.ci80': { en: '80% CI', fr: 'IC 80%', es: 'IC 80%' },
  'demand.pointForecast': { en: 'Point Forecast', fr: 'Prévision ponctuelle', es: 'Previsión puntual' },
  'demand.highConfidence': { en: 'High Confidence', fr: 'Confiance élevée', es: 'Confianza alta' },
  'demand.mediumConfidence': { en: 'Medium Confidence', fr: 'Confiance moyenne', es: 'Confianza media' },
  'demand.avgForecast': { en: 'Avg Forecast', fr: 'Prévision moy.', es: 'Previsión prom.' },
  'demand.periods': { en: 'periods', fr: 'périodes', es: 'períodos' },
  'demand.unitsWeek': { en: 'units/week', fr: 'unités/sem.', es: 'unidades/sem.' },

  // Inventory health chips
  'inventory.chip.stockout': { en: 'Stockout risks', fr: 'Risques de rupture', es: 'Riesgos de rotura' },
  'inventory.chip.overstock': { en: 'Overstock analysis', fr: 'Analyse de surstock', es: 'Análisis de exceso' },
  'inventory.chip.aging': { en: 'Aging inventory', fr: 'Inventaire vieillissant', es: 'Inventario envejecido' },
  'inventory.chip.dos': { en: 'DOS by program', fr: 'JAS par programme', es: 'DAS por programa' },

  // Supply network chips
  'supply.chip.reliability': { en: 'Supplier reliability', fr: 'Fiabilité fournisseurs', es: 'Fiabilidad proveedores' },
  'supply.chip.leadTime': { en: 'Lead time risks', fr: 'Risques de délais', es: 'Riesgos de plazos' },
  'supply.chip.singleSource': { en: 'Single-source risks', fr: 'Risques mono-source', es: 'Riesgos fuente única' },
  'supply.chip.capacity': { en: 'Capacity constraints', fr: 'Contraintes de capacité', es: 'Restricciones de capacidad' },

  // Replenishment chips & dialog
  'replenishment.chip.urgent': { en: 'Urgent orders', fr: 'Commandes urgentes', es: 'Pedidos urgentes' },
  'replenishment.chip.status': { en: 'PO status review', fr: 'Suivi des commandes', es: 'Revisión estado PO' },
  'replenishment.chip.safety': { en: 'Safety stock gaps', fr: 'Écarts stock de sécurité', es: 'Brechas stock seguridad' },
  'replenishment.chip.expedite': { en: 'Expedite candidates', fr: 'Candidats à accélérer', es: 'Candidatos a acelerar' },
  'replenishment.qty': { en: 'Qty', fr: 'Qté', es: 'Cant.' },
  'replenishment.confidence': { en: 'Confidence', fr: 'Confiance', es: 'Confianza' },
  'replenishment.scenario': { en: 'Scenario', fr: 'Scénario', es: 'Escenario' },
  'replenishment.allReviewed': { en: 'All actions have been reviewed.', fr: 'Toutes les actions ont été examinées.', es: 'Todas las acciones han sido revisadas.' },
  'replenishment.confirmApproval': { en: 'Confirm Approval', fr: 'Confirmer l\'approbation', es: 'Confirmar aprobación' },
  'replenishment.actionType': { en: 'Action Type', fr: 'Type d\'action', es: 'Tipo de acción' },
  'replenishment.recommendedQty': { en: 'Recommended Quantity', fr: 'Quantité recommandée', es: 'Cantidad recomendada' },
  'replenishment.urgency': { en: 'Urgency', fr: 'Urgence', es: 'Urgencia' },
  'replenishment.kpiImpact': { en: 'KPI Impact', fr: 'Impact KPI', es: 'Impacto KPI' },
  'replenishment.approving': { en: 'Approving...', fr: 'Approbation...', es: 'Aprobando...' },

  // Production chips
  'production.chip.schedule': { en: 'Production schedule', fr: 'Calendrier de production', es: 'Calendario de producción' },
  'production.chip.utilization': { en: 'Line utilization', fr: 'Utilisation des lignes', es: 'Utilización de líneas' },
  'production.chip.bottleneck': { en: 'Bottleneck analysis', fr: 'Analyse des goulots', es: 'Análisis de cuellos' },
  'production.chip.aog': { en: 'AOG priorities', fr: 'Priorités AOG', es: 'Prioridades AOG' },

  // Labor utilization
  'labor.chip.efficiency': { en: 'Efficiency trends', fr: 'Tendances d\'efficacité', es: 'Tendencias de eficiencia' },
  'labor.chip.overtime': { en: 'Overtime patterns', fr: 'Schémas d\'heures sup.', es: 'Patrones de horas extra' },
  'labor.chip.skills': { en: 'Skill gaps', fr: 'Écarts de compétences', es: 'Brechas de habilidades' },
  'labor.chip.shift': { en: 'Shift optimization', fr: 'Optimisation des quarts', es: 'Optimización de turnos' },
  'labor.avgEfficiency': { en: 'Avg Efficiency', fr: 'Efficacité moy.', es: 'Eficiencia prom.' },
  'labor.directLabor': { en: 'Direct Labor %', fr: '% Main-d\'œuvre directe', es: '% Mano de obra directa' },
  'labor.totalHeadcount': { en: 'Total Headcount (period)', fr: 'Effectif total (période)', es: 'Dotación total (período)' },
  'labor.totalOvertime': { en: 'Total Overtime', fr: 'Heures sup. totales', es: 'Horas extra totales' },
  'labor.efficiencyByFacility': { en: 'Efficiency by Facility', fr: 'Efficacité par site', es: 'Eficiencia por instalación' },
  'labor.efficiencyPct': { en: 'Efficiency %', fr: 'Efficacité %', es: 'Eficiencia %' },
  'labor.dailyRecords': { en: 'Daily Records', fr: 'Registres quotidiens', es: 'Registros diarios' },
  'labor.shift': { en: 'Shift', fr: 'Quart', es: 'Turno' },
  'labor.headcount': { en: 'Headcount', fr: 'Effectif', es: 'Dotación' },
  'labor.directHrs': { en: 'Direct Hrs', fr: 'Heures dir.', es: 'Horas dir.' },
  'labor.indirectHrs': { en: 'Indirect Hrs', fr: 'Heures ind.', es: 'Horas ind.' },
  'labor.otHrs': { en: 'OT Hrs', fr: 'Heures sup.', es: 'Horas extra' },
  'labor.efficiency': { en: 'Efficiency', fr: 'Efficacité', es: 'Eficiencia' },
  'labor.skill': { en: 'Skill', fr: 'Compétence', es: 'Habilidad' },

  // Settings
  'settings.interfaceLanguage': { en: 'Interface Language', fr: 'Langue de l\'interface', es: 'Idioma de la interfaz' },
  'settings.stockoutAlerts': { en: 'Stockout Alerts', fr: 'Alertes de rupture', es: 'Alertas de rotura' },
  'settings.excessAlerts': { en: 'Excess Inventory Alerts', fr: 'Alertes de surstock', es: 'Alertas de exceso' },
  'settings.deliveryAlerts': { en: 'Delivery Delay Alerts', fr: 'Alertes de retard', es: 'Alertas de retraso' },
  'settings.capacityAlerts': { en: 'Capacity Constraint Alerts', fr: 'Alertes de capacité', es: 'Alertas de capacidad' },
  'settings.erp': { en: 'ERP Connection', fr: 'Connexion ERP', es: 'Conexión ERP' },
  'settings.pos': { en: 'POS / Sell-Out Feed', fr: 'Flux POS / Ventes', es: 'Flujo POS / Ventas' },
  'settings.pps': { en: 'Production Planning System', fr: 'Système de planification de production', es: 'Sistema de planificación de producción' },
  'settings.connected': { en: 'Connected (Mock)', fr: 'Connecté (Simulé)', es: 'Conectado (Simulado)' },

  // Agent result panel
  'agentResult.title': { en: 'Agent Result', fr: 'Résultat de l\'agent', es: 'Resultado del agente' },
  'agentResult.recommendedActions': { en: 'Recommended Actions', fr: 'Actions recommandées', es: 'Acciones recomendadas' },
  'agentResult.dismiss': { en: 'Dismiss', fr: 'Fermer', es: 'Cerrar' },

  // Scenario planner page
  'scenarios.quickScenarios': { en: 'Quick Scenarios', fr: 'Scénarios rapides', es: 'Escenarios rápidos' },
  'scenarios.customScenario': { en: 'Custom Scenario', fr: 'Scénario personnalisé', es: 'Escenario personalizado' },
  'scenarios.placeholder': { en: 'Describe your scenario... e.g., \'What if titanium supply is disrupted 40% and A320 program rate increases by 25%?\'', fr: 'Décrivez votre scénario... ex. : \'Et si l\'approvisionnement en titane est perturbé de 40% et la cadence A320 augmente de 25% ?\'', es: 'Describa su escenario... ej., \'¿Qué pasa si el suministro de titanio se interrumpe 40% y la cadencia del A320 aumenta 25%?\'' },
  'scenarios.runAnalysis': { en: 'Run Analysis', fr: 'Lancer l\'analyse', es: 'Ejecutar análisis' },
  'scenarios.totalAffected': { en: 'Total Affected SKUs', fr: 'Réfs affectées (total)', es: 'SKUs afectados (total)' },
  'scenarios.avgDemandIncrease': { en: 'Avg Demand Increase', fr: 'Augmentation moy. demande', es: 'Aumento prom. demanda' },
  'scenarios.kpiDeltas': { en: 'KPI Impact Deltas', fr: 'Deltas d\'impact KPI', es: 'Deltas de impacto KPI' },
  'scenarios.targetBreaches': { en: 'Target Breaches', fr: 'Dépassements d\'objectif', es: 'Incumplimientos de objetivo' },
  'scenarios.baseline': { en: 'Baseline', fr: 'Référence', es: 'Base' },
  'scenarios.projected': { en: 'Projected', fr: 'Projeté', es: 'Proyectado' },
  'scenarios.adjusted': { en: 'Adjusted', fr: 'Ajusté', es: 'Ajustado' },
  'scenarios.demandChart': { en: 'Demand: Baseline vs Adjusted (8-Week)', fr: 'Demande : Référence vs Ajustée (8 sem.)', es: 'Demanda: Base vs Ajustada (8 sem.)' },
  'scenarios.inventoryDepletion': { en: 'Inventory Depletion & Stockout Risk', fr: 'Épuisement des stocks et risque de rupture', es: 'Agotamiento de inventario y riesgo de rotura' },
  'scenarios.stockVsDemand': { en: 'Stock vs Demand (Inventory Simulation)', fr: 'Stock vs Demande (Simulation)', es: 'Stock vs Demanda (Simulación)' },
  'scenarios.totalStock': { en: 'Total Stock (MT)', fr: 'Stock total (MT)', es: 'Stock total (MT)' },
  'scenarios.netPosition': { en: 'Net Position', fr: 'Position nette', es: 'Posición neta' },
  'scenarios.skusInStockout': { en: 'SKUs in Stockout', fr: 'Réfs en rupture', es: 'SKUs en rotura' },
  'scenarios.stockMt': { en: 'Stock (MT)', fr: 'Stock (MT)', es: 'Stock (MT)' },
  'scenarios.demandMt': { en: 'Demand (MT)', fr: 'Demande (MT)', es: 'Demanda (MT)' },
  'scenarios.mitigationOptions': { en: 'Mitigation Options', fr: 'Options de mitigation', es: 'Opciones de mitigación' },
  'scenarios.cost': { en: 'Cost', fr: 'Coût', es: 'Costo' },
  'scenarios.fillRateRecovery': { en: 'Fill Rate Recovery', fr: 'Récupération taux service', es: 'Recuperación tasa servicio' },
  'scenarios.leadTimeDays': { en: 'Lead Time', fr: 'Délai', es: 'Plazo' },
  'scenarios.days': { en: 'days', fr: 'jours', es: 'días' },
  'scenarios.altSuppliers': { en: 'Alternative Suppliers', fr: 'Fournisseurs alternatifs', es: 'Proveedores alternativos' },
  'scenarios.capacityMt': { en: 'Capacity (MT)', fr: 'Capacité (MT)', es: 'Capacidad (MT)' },
  'scenarios.premium': { en: 'Premium', fr: 'Prime', es: 'Prima' },
  'scenarios.supplyGap': { en: 'Supply Gap Coverage', fr: 'Couverture écart appro.', es: 'Cobertura brecha suministro' },
  'scenarios.needed': { en: 'Needed', fr: 'Besoin', es: 'Necesidad' },
  'scenarios.available': { en: 'Available', fr: 'Disponible', es: 'Disponible' },
  'scenarios.productionCapacity': { en: 'Production Capacity', fr: 'Capacité de production', es: 'Capacidad de producción' },
  'scenarios.feasibility': { en: 'Feasibility', fr: 'Faisabilité', es: 'Factibilidad' },
  'scenarios.spareMtDay': { en: 'Spare (MT/day)', fr: 'Réserve (MT/jour)', es: 'Reserva (MT/día)' },
  'scenarios.surgeOptions': { en: 'Surge Options', fr: 'Options de montée en charge', es: 'Opciones de aumento' },
  'scenarios.history': { en: 'Scenario History', fr: 'Historique des scénarios', es: 'Historial de escenarios' },
  'scenarios.compareSelected': { en: 'Compare Selected', fr: 'Comparer sélection', es: 'Comparar selección' },
  'scenarios.comparison': { en: 'Scenario Comparison', fr: 'Comparaison de scénarios', es: 'Comparación de escenarios' },
  'scenarios.type': { en: 'Type', fr: 'Type', es: 'Tipo' },
  'scenarios.skusAffected': { en: 'SKUs Affected', fr: 'Réfs affectées', es: 'SKUs afectados' },
  'scenarios.baselineAdj': { en: 'Baseline / Adjusted', fr: 'Référence / Ajusté', es: 'Base / Ajustado' },
  'scenarios.deltaPct': { en: 'Delta %', fr: 'Delta %', es: 'Delta %' },
  'scenarios.weeksToStockout': { en: 'Weeks to Stockout', fr: 'Semaines avant rupture', es: 'Semanas hasta rotura' },
  'scenarios.currentDos': { en: 'Current DOS', fr: 'JAS actuel', es: 'DAS actual' },
  'scenarios.severity': { en: 'Severity', fr: 'Sévérité', es: 'Severidad' },
  'scenarios.scenarioA': { en: 'Scenario A', fr: 'Scénario A', es: 'Escenario A' },
  'scenarios.scenarioB': { en: 'Scenario B', fr: 'Scénario B', es: 'Escenario B' },
  'scenarios.deltaBA': { en: 'Delta (B-A)', fr: 'Delta (B-A)', es: 'Delta (B-A)' },
  'scenarios.chip.rateIncrease': { en: 'Program Rate Increase: A220 +30%', fr: 'Hausse cadence : A220 +30%', es: 'Aumento cadencia: A220 +30%' },
  'scenarios.chip.forgingDelay': { en: 'Forging Supplier Delay: 28 days', fr: 'Retard fournisseur forgeage : 28 jours', es: 'Retraso proveedor forja: 28 días' },
  'scenarios.chip.aog': { en: 'AOG Emergency: 737 NLG', fr: 'Urgence AOG : 737 NLG', es: 'Emergencia AOG: 737 NLG' },
  'scenarios.chip.titanium': { en: 'Titanium Supply Disruption: 60%', fr: 'Perturbation titane : 60%', es: 'Disrupción titanio: 60%' },
  'scenarios.chip.multiFactor': { en: 'Multi-factor: Rate + Delay', fr: 'Multi-facteur : Cadence + Retard', es: 'Multi-factor: Cadencia + Retraso' },
};

const I18nContext = createContext<I18nContextType>({
  lang: 'en',
  dir: 'ltr',
  setLang: () => {},
  t: (key: string) => key,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>('en');

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
  }, []);

  const t = useCallback((key: string) => {
    return translations[key]?.[lang] ?? key;
  }, [lang]);

  const dir = 'ltr' as const;

  return (
    <I18nContext.Provider value={{ lang, dir, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
