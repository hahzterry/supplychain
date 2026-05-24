import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

export type Lang = 'en' | 'ar';

interface I18nContextType {
  lang: Lang;
  dir: 'ltr' | 'rtl';
  toggle: () => void;
  t: (key: string) => string;
}

const translations: Record<string, Record<Lang, string>> = {
  'app.name': { en: 'RASHID', ar: 'رشيد' },
  'app.subtitle': { en: 'Demand Sensing & Replenishment Platform', ar: 'منصة استشعار الطلب والتجديد' },
  'app.welcome': { en: 'Good morning. Here\'s your daily supply chain briefing.', ar: 'صباح الخير. إليك موجز سلسلة التوريد اليومي.' },

  'nav.dashboard': { en: 'Dashboard', ar: 'لوحة المعلومات' },
  'nav.demandForecast': { en: 'Demand Forecast', ar: 'توقعات الطلب' },
  'nav.inventoryHealth': { en: 'Inventory Health', ar: 'صحة المخزون' },
  'nav.supplyNetwork': { en: 'Supply Network', ar: 'شبكة التوريد' },
  'nav.replenishment': { en: 'Replenishment Plan', ar: 'خطة التجديد' },
  'nav.production': { en: 'Production Priorities', ar: 'أولويات الإنتاج' },
  'nav.scenarios': { en: 'Scenario Planner', ar: 'مخطط السيناريوهات' },
  'nav.reports': { en: 'Reports & Exports', ar: 'التقارير والتصدير' },
  'nav.settings': { en: 'Settings', ar: 'الإعدادات' },

  'dashboard.title': { en: 'Supply Chain Dashboard', ar: 'لوحة معلومات سلسلة التوريد' },
  'dashboard.forecastAccuracy': { en: 'Forecast Accuracy', ar: 'دقة التوقعات' },
  'dashboard.inventoryDOS': { en: 'Avg Days of Supply', ar: 'متوسط أيام التوريد' },
  'dashboard.fillRate': { en: 'Fill Rate', ar: 'معدل التعبئة' },
  'dashboard.stockoutRate': { en: 'Stockout Rate', ar: 'معدل نفاد المخزون' },
  'dashboard.criticalAlerts': { en: 'Critical Alerts', ar: 'تنبيهات حرجة' },
  'dashboard.pendingActions': { en: 'Pending Actions', ar: 'إجراءات معلقة' },
  'dashboard.demandHeatmap': { en: 'Demand Signals by Category', ar: 'إشارات الطلب حسب الفئة' },
  'dashboard.riskOverview': { en: 'Inventory Risk Overview', ar: 'نظرة عامة على مخاطر المخزون' },
  'dashboard.quickActions': { en: 'Quick Actions', ar: 'إجراءات سريعة' },
  'dashboard.runBrief': { en: 'Morning Brief', ar: 'الموجز الصباحي' },
  'dashboard.briefDesc': { en: 'Get today\'s supply chain summary', ar: 'احصل على ملخص سلسلة التوريد اليوم' },
  'dashboard.checkRisks': { en: 'Check Risks', ar: 'فحص المخاطر' },
  'dashboard.riskDesc': { en: 'Review stockout & excess risks', ar: 'مراجعة مخاطر النفاد والفائض' },
  'dashboard.genReport': { en: 'S&OP Report', ar: 'تقرير S&OP' },
  'dashboard.reportDesc': { en: 'Generate weekly S&OP deck', ar: 'إنشاء عرض S&OP الأسبوعي' },

  'demand.title': { en: 'Demand Forecast', ar: 'توقعات الطلب' },
  'demand.subtitle': { en: 'SKU-level demand forecasts with confidence intervals and promotion overlays.', ar: 'توقعات الطلب على مستوى SKU مع فترات الثقة وتراكبات العروض.' },
  'demand.selectSku': { en: 'Select SKU', ar: 'اختيار المنتج' },
  'demand.confidence': { en: 'Confidence', ar: 'الثقة' },
  'demand.accuracy': { en: 'Forecast Accuracy (MAPE)', ar: 'دقة التوقعات (MAPE)' },

  'inventory.title': { en: 'Inventory Health', ar: 'صحة المخزون' },
  'inventory.subtitle': { en: 'Stock positions, aging analysis, and risk matrix across all SKUs.', ar: 'مواقع المخزون وتحليل العمر ومصفوفة المخاطر لجميع المنتجات.' },
  'inventory.riskMatrix': { en: 'Risk Matrix', ar: 'مصفوفة المخاطر' },
  'inventory.positions': { en: 'Stock Positions', ar: 'مواقع المخزون' },
  'inventory.critical': { en: 'Critical', ar: 'حرج' },
  'inventory.warning': { en: 'Warning', ar: 'تحذير' },
  'inventory.normal': { en: 'Normal', ar: 'طبيعي' },
  'inventory.excess': { en: 'Excess', ar: 'فائض' },

  'supply.title': { en: 'Supply Network', ar: 'شبكة التوريد' },
  'supply.subtitle': { en: 'Supplier performance, lead times, and production capacity.', ar: 'أداء الموردين وأوقات التسليم والطاقة الإنتاجية.' },
  'supply.suppliers': { en: 'Suppliers', ar: 'الموردون' },
  'supply.capacity': { en: 'Plant Capacity', ar: 'طاقة المصنع' },
  'supply.openPOs': { en: 'Open Purchase Orders', ar: 'أوامر الشراء المفتوحة' },

  'replenishment.title': { en: 'Replenishment Plan', ar: 'خطة التجديد' },
  'replenishment.subtitle': { en: 'AI-recommended actions with scenario comparison and KPI impact.', ar: 'إجراءات موصى بها بالذكاء الاصطناعي مع مقارنة السيناريوهات وتأثير مؤشرات الأداء.' },
  'replenishment.approve': { en: 'Approve', ar: 'موافقة' },
  'replenishment.dismiss': { en: 'Dismiss', ar: 'رفض' },
  'replenishment.scenarioCompare': { en: 'Scenario Comparison', ar: 'مقارنة السيناريوهات' },

  'production.title': { en: 'Production Priorities', ar: 'أولويات الإنتاج' },
  'production.subtitle': { en: 'Manufacturing schedule, capacity utilization, and AI recommendations.', ar: 'جدول التصنيع واستخدام الطاقة وتوصيات الذكاء الاصطناعي.' },
  'production.schedule': { en: 'Production Schedule', ar: 'جدول الإنتاج' },
  'production.utilization': { en: 'Capacity Utilization', ar: 'استخدام الطاقة' },

  'scenarios.title': { en: 'Scenario Planner', ar: 'مخطط السيناريوهات' },
  'scenarios.subtitle': { en: 'What-if analysis for demand spikes, supplier delays, and promotions.', ar: 'تحليل ماذا لو لارتفاعات الطلب وتأخيرات الموردين والعروض.' },
  'scenarios.demandSpike': { en: 'Demand Spike', ar: 'ارتفاع الطلب' },
  'scenarios.supplierDelay': { en: 'Supplier Delay', ar: 'تأخير المورد' },
  'scenarios.promotion': { en: 'Promotion Impact', ar: 'تأثير العرض' },
  'scenarios.capacityLoss': { en: 'Capacity Loss', ar: 'فقدان الطاقة' },
  'scenarios.runScenario': { en: 'Run Scenario', ar: 'تشغيل السيناريو' },
  'scenarios.impactSummary': { en: 'Impact Summary', ar: 'ملخص التأثير' },
  'scenarios.affectedSkus': { en: 'Affected SKUs', ar: 'المنتجات المتأثرة' },
  'scenarios.mitigation': { en: 'Mitigation & Supply', ar: 'التخفيف والتوريد' },
  'scenarios.timeline': { en: 'Stock Timeline', ar: 'الجدول الزمني للمخزون' },
  'scenarios.kpiComparison': { en: 'KPI Comparison', ar: 'مقارنة المؤشرات' },
  'scenarios.riskAssessment': { en: 'Risk Assessment', ar: 'تقييم المخاطر' },
  'scenarios.recommendations': { en: 'Recommended Actions', ar: 'الإجراءات الموصى بها' },
  'scenarios.critical': { en: 'Critical', ar: 'حرج' },
  'scenarios.warning': { en: 'Warning', ar: 'تحذير' },
  'scenarios.safe': { en: 'Safe', ar: 'آمن' },

  'reports.title': { en: 'Reports & Exports', ar: 'التقارير والتصدير' },
  'reports.subtitle': { en: 'Generate S&OP reports in PowerPoint, Word, Excel, or PDF.', ar: 'إنشاء تقارير S&OP بصيغ PowerPoint أو Word أو Excel أو PDF.' },
  'reports.selectTemplate': { en: 'Select Template', ar: 'اختيار القالب' },
  'reports.generate': { en: 'Generate Report', ar: 'إنشاء التقرير' },
  'reports.recent': { en: 'Recent Reports', ar: 'التقارير الأخيرة' },
  'reports.sections': { en: 'Sections', ar: 'الأقسام' },
  'reports.config': { en: 'Configuration', ar: 'الإعدادات' },
  'reports.confirmTitle': { en: 'Confirm Report Generation', ar: 'تأكيد إنشاء التقرير' },
  'reports.addContext': { en: 'Additional context or instructions (optional)', ar: 'سياق أو تعليمات إضافية (اختياري)' },
  'reports.contextPlaceholder': { en: 'e.g., Focus on flour category, include last 4 weeks trend...', ar: 'مثال: التركيز على فئة الطحين، تضمين اتجاه آخر 4 أسابيع...' },
  'reports.cancel': { en: 'Cancel', ar: 'إلغاء' },
  'reports.feedbackTitle': { en: 'Regenerate with Feedback', ar: 'إعادة الإنشاء مع ملاحظات' },
  'reports.overallChanges': { en: 'Overall changes requested', ar: 'التغييرات المطلوبة بشكل عام' },
  'reports.sectionFeedback': { en: 'Per-section feedback (optional)', ar: 'ملاحظات لكل قسم (اختياري)' },
  'reports.sectionPlaceholder': { en: 'What to change in this section...', ar: 'ما الذي يجب تغييره في هذا القسم...' },
  'reports.regenerateWithFeedback': { en: 'Regenerate', ar: 'إعادة الإنشاء' },

  'settings.title': { en: 'Settings', ar: 'الإعدادات' },
  'settings.language': { en: 'Language', ar: 'اللغة' },
  'settings.alertPrefs': { en: 'Alert Preferences', ar: 'تفضيلات التنبيه' },
  'settings.dataSources': { en: 'Data Sources', ar: 'مصادر البيانات' },

  'common.search': { en: 'Ask Rashid anything... "What\'s the stockout risk?" or "Generate S&OP deck"', ar: 'اسأل رشيد أي شيء... "ما هو خطر نفاد المخزون؟" أو "إنشاء عرض S&OP"' },
  'common.aiAssistant': { en: 'Rashid AI', ar: 'رشيد' },

  'chat.welcome': { en: 'Hi, I\'m Rashid — your AI supply chain analyst. I can analyze demand, check inventory risks, recommend replenishment actions, or generate S&OP reports. What would you like to review?', ar: 'مرحبًا، أنا رشيد — محلل سلسلة التوريد الذكي. يمكنني تحليل الطلب وفحص مخاطر المخزون واقتراح إجراءات التجديد أو إنشاء تقارير S&OP. ماذا تريد مراجعته؟' },
  'chat.ask': { en: 'Ask Rashid...', ar: 'اسأل رشيد...' },
  'chat.newSession': { en: 'New Session', ar: 'جلسة جديدة' },

  'ticker.live': { en: 'LIVE', ar: 'مباشر' },
  'ticker.supplyAlerts': { en: 'Supply Alerts', ar: 'تنبيهات التوريد' },

  'actions.title': { en: 'Rashid Recommended Actions', ar: 'إجراءات رشيد المقترحة' },
  'actions.approve': { en: 'Approve', ar: 'موافقة' },
  'actions.dismiss': { en: 'Dismiss', ar: 'رفض' },
};

const I18nContext = createContext<I18nContextType>({
  lang: 'en',
  dir: 'ltr',
  toggle: () => {},
  t: (key: string) => key,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>('en');

  const toggle = useCallback(() => {
    setLang(prev => prev === 'en' ? 'ar' : 'en');
  }, []);

  const t = useCallback((key: string) => {
    return translations[key]?.[lang] ?? key;
  }, [lang]);

  const dir = lang === 'ar' ? 'rtl' as const : 'ltr' as const;

  return (
    <I18nContext.Provider value={{ lang, dir, toggle, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
