import { useState, useEffect, useCallback, useRef } from 'react';
import {
  makeStyles, shorthands, tokens,
  Text, Card, Badge, Button, Checkbox, Dropdown, Option,
  Spinner, Textarea,
  Dialog, DialogSurface, DialogBody, DialogTitle, DialogContent, DialogActions,
} from '@fluentui/react-components';
import {
  ArrowDownload24Regular, ArrowReset24Regular,
} from '@fluentui/react-icons';
import { useI18n } from '../i18n';
import { setPendingChatMessage, TOOL_COMPLETE_EVENT } from '../components/CopilotActions';
import { getSessionHeader } from '../App';
import { renderDeck } from '../pptx/renderer';
import { renderDoc } from '../docx/renderer';
import { renderSheet } from '../xlsx/renderer';
import { renderPDF } from '../pdf/renderer';
import { fetchReports } from '../reports';
import type { DeckSpec, DocSpec, SheetSpec, ReportResult, ReportRecord } from '../reports';

const useStyles = makeStyles({
  templates: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', ...shorthands.gap('12px'), marginBottom: '24px' },
  templateCard: {
    ...shorthands.padding('20px'),
    cursor: 'pointer',
    textAlign: 'center',
    ':hover': { boxShadow: tokens.shadow8 },
  },
  templateSelected: { ...shorthands.border('2px', 'solid', tokens.colorBrandStroke1) },
  configGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', ...shorthands.gap('16px'), marginBottom: '16px' },
  preview: {
    ...shorthands.padding('24px'),
    backgroundColor: '#fff',
    ...shorthands.border('1px', 'solid', tokens.colorNeutralStroke2),
    ...shorthands.borderRadius('8px'),
    minHeight: '400px',
  },
  slidePreview: {
    ...shorthands.padding('12px', '16px'),
    ...shorthands.borderBottom('1px', 'solid', tokens.colorNeutralStroke2),
    ':hover': { backgroundColor: tokens.colorNeutralBackground2 },
  },
  slideNumber: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '24px',
    height: '24px',
    ...shorthands.borderRadius('4px'),
    backgroundColor: tokens.colorBrandBackground,
    color: '#fff',
    fontSize: '11px',
    fontWeight: '600' as any,
    marginRight: '12px',
  },
  recentReport: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    ...shorthands.padding('10px', '14px'),
    ...shorthands.borderBottom('1px', 'solid', tokens.colorNeutralStroke2),
    ':hover': { backgroundColor: tokens.colorNeutralBackground3 },
  },
  generatingCard: {
    ...shorthands.padding('32px'),
    textAlign: 'center',
    backgroundColor: tokens.colorNeutralBackground2,
    ...shorthands.border('1px', 'dashed', tokens.colorBrandStroke1),
    ...shorthands.borderRadius('12px'),
  },
});

const TEMPLATES = [
  { id: 'weekly_sop', name: 'Weekly S&OP Review', desc: 'KPIs, alerts, actions, demand outlook', format: 'pptx' },
  { id: 'inventory_review', name: 'Inventory Status', desc: 'Stock positions, risk matrix, aging analysis', format: 'pptx' },
  { id: 'demand_review', name: 'Demand Accuracy', desc: 'MAPE trends, bias, forecast vs actuals', format: 'pptx' },
  { id: 'executive_sop_summary', name: 'Executive S&OP Summary', desc: 'High-level performance, decisions & risk outlook', format: 'docx' },
  { id: 'inventory_deep_dive', name: 'Inventory Deep-Dive', desc: 'Portfolio health, stockout risk, safety stock optimization', format: 'docx' },
  { id: 'replenishment_plan', name: 'Replenishment Plan', desc: 'Recommended orders & production priorities', format: 'xlsx' },
  { id: 'supplier_scorecard', name: 'Supplier Scorecard', desc: 'Lead times, reliability, quality scores', format: 'xlsx' },
];

const TEMPLATE_SECTIONS: Record<string, string[]> = {
  weekly_sop: ['Executive KPIs', 'Key Highlights', 'Inventory Positions', 'Demand Forecast', 'Fill Rate Trends', 'Supply Risks', 'Supplier Performance', 'Replenishment Actions', 'Critical Alerts', 'Next Steps'],
  inventory_review: ['Inventory KPIs', 'Positions by SKU', 'Days of Supply', 'At-Risk Items', 'Trends', 'Recommendations'],
  demand_review: ['Forecast Accuracy KPIs', 'Forecast vs Actuals', 'SKU Breakdown', 'Confidence Intervals', 'Market Factors', 'Recommendations'],
  executive_sop_summary: ['Executive Overview', 'Performance Highlights', 'Critical Decisions Required', 'KPI Summary & Trends', 'Risk Outlook', 'Next Steps & Action Items'],
  inventory_deep_dive: ['Executive Summary', 'Portfolio Health Assessment', 'Category Analysis', 'Stockout Exposure & Impact', 'Obsolescence Risk', 'Safety Stock Optimization', 'Recommendations'],
  replenishment_plan: ['Summary', 'Priority Orders', 'Production Schedule', 'Safety Stock Status', 'Cost Analysis'],
  supplier_scorecard: ['Summary', 'Supplier Rankings', 'On-Time Delivery', 'Quality Scores', 'Risk Assessment'],
};

const LAYOUT_LABELS: Record<string, string> = {
  title: 'Title Slide',
  section_header: 'Section Header',
  bullets: 'Bullets',
  two_column: 'Two Columns',
  data_table: 'Data Table',
  kpi_cards: 'KPI Cards',
  chart: 'Chart',
  bullets_with_kpis: 'KPIs + Bullets',
  chart_with_bullets: 'Chart + Bullets',
  table_with_bullets: 'Table + Bullets',
};

const EMPHASIS_COLORS: Record<string, string> = {
  positive: '#4CAF50',
  negative: '#C41E3A',
  alert: '#FF8C00',
  neutral: tokens.colorNeutralForeground1,
};

export default function Reports() {
  const styles = useStyles();
  const { t } = useI18n();

  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [sections, setSections] = useState<Set<string>>(new Set());
  const [audience, setAudience] = useState('S&OP Committee');

  const availableSections = selectedTemplate ? (TEMPLATE_SECTIONS[selectedTemplate] || []) : [];
  const [deck, setDeck] = useState<DeckSpec | null>(null);
  const [report, setReport] = useState<ReportResult | null>(null);
  const [generating, setGenerating] = useState(false);
  const [pipelineSteps, setPipelineSteps] = useState<Record<string, string>>({});
  const [recentReports, setRecentReports] = useState<ReportRecord[]>([]);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [additionalContext, setAdditionalContext] = useState('');
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);
  const [overallFeedback, setOverallFeedback] = useState('');
  const [sectionFeedback, setSectionFeedback] = useState<Record<number, string>>({});

  const consumedStateRef = useRef<string | null>(null);

  useEffect(() => {
    if (selectedTemplate) {
      setSections(new Set(TEMPLATE_SECTIONS[selectedTemplate] || []));
    }
  }, [selectedTemplate]);

  const loadReports = useCallback(() => {
    fetchReports().then(setRecentReports).catch(() => {});
  }, []);

  useEffect(() => { loadReports(); }, [loadReports]);

  const applyResult = useCallback((result: { pending_deck?: DeckSpec; pending_report?: ReportResult }) => {
    if (result.pending_deck) {
      const key = result.pending_deck.title + '|' + (result.pending_deck.slides?.length ?? 0);
      if (key === consumedStateRef.current) return false;
      consumedStateRef.current = key;
      setDeck(result.pending_deck);
      setReport(null);
      setGenerating(false);
      loadReports();
      return true;
    } else if (result.pending_report) {
      const key = (result.pending_report.spec as any)?.title + '|' + result.pending_report.type;
      if (key === consumedStateRef.current) return false;
      consumedStateRef.current = key;
      setReport(result.pending_report);
      setDeck(null);
      setGenerating(false);
      loadReports();
      return true;
    }
    return false;
  }, [loadReports]);

  const fetchLatestSpec = useCallback(async () => {
    try {
      const headers = getSessionHeader();
      const res = await fetch('/api/reports/latest', { headers });
      const json = await res.json();
      if (!json.result) return false;
      const applied = applyResult(json.result);
      if (applied) {
        fetch('/api/reports/latest', { method: 'DELETE', headers }).catch(() => {});
      }
      return applied;
    } catch { /* ignore */ }
    return false;
  }, [applyResult]);

  // Listen for tool completion events
  useEffect(() => {
    const handler = (e: Event) => {
      const { name } = (e as CustomEvent).detail || {};
      if (name === 'generate_sop_deck' || name === 'generate_report') {
        setTimeout(() => fetchLatestSpec(), 500);
      }
    };
    window.addEventListener(TOOL_COMPLETE_EVENT, handler);
    return () => window.removeEventListener(TOOL_COMPLETE_EVENT, handler);
  }, [fetchLatestSpec]);

  // Poll while generating
  useEffect(() => {
    if (!generating || deck || report) return;
    const interval = setInterval(async () => {
      try {
        const headers = getSessionHeader();
        const res = await fetch('/api/reports/latest', { headers });
        const json = await res.json();
        if (json.result?.pending_deck || json.result?.pending_report) {
          const applied = applyResult(json.result);
          if (applied) {
            fetch('/api/reports/latest', { method: 'DELETE', headers }).catch(() => {});
          }
        } else if (json.result?.report_progress) {
          const { step, status } = json.result.report_progress;
          setPipelineSteps(prev => ({ ...prev, [step]: status }));
        }
      } catch { /* ignore */ }
    }, 1500);
    return () => clearInterval(interval);
  }, [generating, deck, report, applyResult]);

  // Stop generating spinner if no progress arrives in 5 minutes
  const lastProgressRef = useRef(Date.now());
  useEffect(() => {
    if (!generating) return;
    lastProgressRef.current = Date.now();
  }, [generating, pipelineSteps]);

  useEffect(() => {
    if (!generating) return;
    const timer = setInterval(() => {
      if (Date.now() - lastProgressRef.current > 300000) {
        fetchLatestSpec().then(found => { if (!found && !deck && !report) setGenerating(false); });
      }
    }, 30000);
    return () => clearInterval(timer);
  }, [generating, deck, report, fetchLatestSpec]);

  // On mount, check for pending result
  useEffect(() => { fetchLatestSpec(); }, [fetchLatestSpec]);

  const toggleSection = (s: string) => {
    setSections(prev => {
      const next = new Set(prev);
      next.has(s) ? next.delete(s) : next.add(s);
      return next;
    });
  };

  const getOutputFormat = (id: string) => TEMPLATES.find(t => t.id === id)?.format || 'pptx';

  const generate = useCallback((extraContext?: string) => {
    if (!selectedTemplate) return;
    consumedStateRef.current = null;
    setGenerating(true);
    setPipelineSteps({});
    setDeck(null);
    setReport(null);

    const format = getOutputFormat(selectedTemplate);
    const templateName = TEMPLATES.find(t => t.id === selectedTemplate)?.name || 'report';
    const selectedSections = [...sections].join(', ');
    const contextSuffix = extraContext?.trim() ? ` Additional instructions: ${extraContext.trim()}` : '';

    if (format === 'pptx') {
      const msg = `Generate ${templateName} deck in PPTX format for ${audience}. Focus on: ${selectedSections}. Template: ${selectedTemplate}.${contextSuffix}`;
      setPendingChatMessage(msg);
    } else {
      const msg = `Generate ${templateName} report in ${format.toUpperCase()} format for ${audience}. Focus on: ${selectedSections}. Template: ${selectedTemplate}, format: ${format}.${contextSuffix}`;
      setPendingChatMessage(msg);
    }
  }, [selectedTemplate, audience, sections]);

  const handleDownloadDeck = useCallback(async () => {
    if (!deck) return;
    await renderDeck(deck);
  }, [deck]);

  const handleDownloadDoc = useCallback(async () => {
    if (!report || report.type !== 'doc') return;
    await renderDoc(report.spec as DocSpec);
  }, [report]);

  const handleDownloadPdf = useCallback(async () => {
    if (!report || report.type !== 'doc') return;
    await renderPDF(report.spec as DocSpec);
  }, [report]);

  const handleDownloadSheet = useCallback(async () => {
    if (!report || report.type !== 'sheet') return;
    await renderSheet(report.spec as SheetSpec);
  }, [report]);

  const handleRegenerate = useCallback(() => {
    setShowFeedbackDialog(true);
  }, []);

  const getSectionTitles = useCallback((): string[] => {
    if (deck) return deck.slides.map(s => s.title);
    if (report?.type === 'doc') return (report.spec as DocSpec).sections.map(s => s.title);
    if (report?.type === 'sheet') return [(report.spec as SheetSpec).title];
    return [];
  }, [deck, report]);

  const confirmRegenerate = useCallback(() => {
    setShowFeedbackDialog(false);
    const title = deck?.title || (report?.spec as any)?.title || 'the report';
    const titles = getSectionTitles();

    let msg = `Regenerate the report "${title}" with the following changes:\n`;
    if (overallFeedback.trim()) {
      msg += `\nOverall: ${overallFeedback.trim()}`;
    }
    const notes = Object.entries(sectionFeedback)
      .filter(([_, text]) => text.trim())
      .map(([idx, text]) => `- ${titles[Number(idx)] || `Section ${Number(idx) + 1}`}: ${text.trim()}`);
    if (notes.length > 0) {
      msg += `\n\nPer-section feedback:\n${notes.join('\n')}`;
    }
    if (!overallFeedback.trim() && notes.length === 0) {
      msg = `Regenerate the report "${title}" with improvements.`;
    }

    consumedStateRef.current = null;
    setDeck(null);
    setReport(null);
    setGenerating(true);
    setPipelineSteps({});
    setOverallFeedback('');
    setSectionFeedback({});
    setPendingChatMessage(msg);
  }, [deck, report, overallFeedback, sectionFeedback, getSectionTitles]);

  const handleDownloadRecent = (r: ReportRecord) => {
    if (r.download_url) window.open(r.download_url, '_blank');
  };

  // ─── Feedback Dialog ────────────────────────────────────────────────────────
  const feedbackDialog = (
    <Dialog open={showFeedbackDialog} onOpenChange={(_, d) => { if (!d.open) setShowFeedbackDialog(false); }}>
      <DialogSurface style={{ maxWidth: 640 }}>
        <DialogBody>
          <DialogTitle>{t('reports.feedbackTitle')}</DialogTitle>
          <DialogContent>
            <Text size={300} weight="semibold" style={{ display: 'block', marginBottom: 6 }}>
              {t('reports.overallChanges')}
            </Text>
            <Textarea
              value={overallFeedback}
              onChange={(_, d) => setOverallFeedback(d.value)}
              placeholder="e.g., Make it more concise, add more data, focus on different areas..."
              rows={2}
              style={{ width: '100%', marginBottom: 16 }}
            />
            <Text size={300} weight="semibold" style={{ display: 'block', marginBottom: 8 }}>
              {t('reports.sectionFeedback')}
            </Text>
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
              {getSectionTitles().map((title, idx) => (
                <div key={idx} style={{ marginBottom: 10, padding: '8px 12px', background: tokens.colorNeutralBackground2, borderRadius: 4 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <Badge size="small" color="brand">{idx + 1}</Badge>
                    <Text size={200} weight="semibold">{title}</Text>
                  </div>
                  <Textarea
                    value={sectionFeedback[idx] || ''}
                    onChange={(_, d) => setSectionFeedback(prev => ({ ...prev, [idx]: d.value }))}
                    placeholder={t('reports.sectionPlaceholder')}
                    rows={1}
                    style={{ width: '100%' }}
                  />
                </div>
              ))}
            </div>
          </DialogContent>
          <DialogActions>
            <Button appearance="secondary" onClick={() => { setShowFeedbackDialog(false); setOverallFeedback(''); setSectionFeedback({}); }}>
              {t('reports.cancel')}
            </Button>
            <Button appearance="primary" onClick={confirmRegenerate}>
              {t('reports.regenerateWithFeedback')}
            </Button>
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );

  // ─── PPTX Preview ─────────────────────────────────────────────────────────
  if (deck) {
    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <Text size={600} weight="bold">{deck.title}</Text>
            <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3, marginTop: '4px' }}>
              {deck.slides.length} slides · {deck.audience} · {deck.date}
            </Text>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button appearance="outline" onClick={() => setDeck(null)}>Back to Builder</Button>
            <Button icon={<ArrowReset24Regular />} appearance="outline" onClick={handleRegenerate}>
              Regenerate
            </Button>
            <Button icon={<ArrowDownload24Regular />} appearance="primary" onClick={handleDownloadDeck}>
              Download PPTX
            </Button>
          </div>
        </div>

        <div className={styles.preview}>
          <div style={{ textAlign: 'center', marginBottom: '20px', paddingBottom: '16px', borderBottom: `2px solid ${tokens.colorBrandStroke1}` }}>
            <Text size={700} weight="bold" style={{ display: 'block', margin: '8px 0' }}>
              {deck.title}
            </Text>
            {deck.subtitle && (
              <Text size={400} style={{ color: tokens.colorNeutralForeground3 }}>{deck.subtitle}</Text>
            )}
            <Text size={200} style={{ display: 'block', marginTop: '8px', color: tokens.colorNeutralForeground4 }}>
              {deck.metadata?.classification || 'Internal — Confidential'} · Generated by {deck.metadata?.generated_by || 'Atlas AI'}
            </Text>
          </div>

          {deck.slides.map((slide, idx) => (
            <div key={slide.id || idx} className={styles.slidePreview} style={{
              borderLeft: `3px solid ${EMPHASIS_COLORS[slide.emphasis || 'neutral'] || EMPHASIS_COLORS.neutral}`,
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                <span className={styles.slideNumber}>{idx + 1}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <Text weight="semibold" size={400}>{slide.title}</Text>
                    <Badge appearance="outline" size="small" color="informative">
                      {LAYOUT_LABELS[slide.layout] || slide.layout}
                    </Badge>
                  </div>
                  {slide.subtitle && (
                    <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3, marginBottom: '4px' }}>{slide.subtitle}</Text>
                  )}
                  {slide.content.bullets && slide.content.bullets.length > 0 && (
                    <div style={{ marginTop: '4px' }}>
                      {slide.content.bullets.slice(0, 3).map((b, i) => (
                        <Text key={i} size={200} style={{ display: 'block', color: tokens.colorNeutralForeground2, padding: '1px 0' }}>• {b}</Text>
                      ))}
                      {slide.content.bullets.length > 3 && (
                        <Text size={200} style={{ color: tokens.colorNeutralForeground4 }}>+{slide.content.bullets.length - 3} more</Text>
                      )}
                    </div>
                  )}
                  {slide.content.kpis && slide.content.kpis.length > 0 && (
                    <div style={{ display: 'flex', gap: '12px', marginTop: '4px', flexWrap: 'wrap' }}>
                      {slide.content.kpis.map((kpi, i) => (
                        <Badge key={i} appearance="filled" size="medium" color={kpi.trend === 'up' ? 'success' : kpi.trend === 'down' ? 'danger' : 'informative'}>
                          {kpi.label}: {kpi.value}
                        </Badge>
                      ))}
                    </div>
                  )}
                  {slide.content.table && (
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginTop: '4px', display: 'block' }}>
                      Table: {slide.content.table.headers.join(' | ')} ({slide.content.table.rows.length} rows)
                    </Text>
                  )}
                  {slide.content.chart_data && (
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginTop: '4px', display: 'block' }}>
                      {slide.content.chart_data.chart_type} chart: {slide.content.chart_data.labels.length} data points
                    </Text>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        {feedbackDialog}
      </div>
    );
  }

  // ─── DOCX/PDF Preview ─────────────────────────────────────────────────────
  if (report && report.type === 'doc') {
    const docSpec = report.spec as DocSpec;
    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <Text size={600} weight="bold">{docSpec.title}</Text>
            <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3, marginTop: '4px' }}>
              {docSpec.sections.length} sections · {docSpec.date}
            </Text>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button appearance="outline" onClick={() => setReport(null)}>Back to Builder</Button>
            <Button icon={<ArrowReset24Regular />} appearance="outline" onClick={handleRegenerate}>
              Regenerate
            </Button>
            <Button appearance="outline" onClick={handleDownloadPdf}>Export PDF</Button>
            <Button icon={<ArrowDownload24Regular />} appearance="primary" onClick={handleDownloadDoc}>
              Download Word
            </Button>
          </div>
        </div>

        <div className={styles.preview}>
          <div style={{ textAlign: 'center', marginBottom: '20px', paddingBottom: '16px', borderBottom: `2px solid ${tokens.colorBrandStroke1}` }}>
            <Text size={700} weight="bold" style={{ display: 'block', margin: '8px 0' }}>
              {docSpec.title}
            </Text>
            {docSpec.subtitle && <Text size={400} style={{ color: tokens.colorNeutralForeground3 }}>{docSpec.subtitle}</Text>}
            <Text size={200} style={{ display: 'block', marginTop: '8px', color: tokens.colorNeutralForeground4 }}>
              {docSpec.footer_text} · Generated by {docSpec.author}
            </Text>
          </div>

          {docSpec.executive_summary && (
            <div style={{ padding: '12px 16px', backgroundColor: tokens.colorNeutralBackground2, borderRadius: '8px', marginBottom: '16px', borderLeft: `3px solid ${tokens.colorBrandStroke1}` }}>
              <Text size={200} weight="semibold" style={{ display: 'block', marginBottom: '4px' }}>
                Executive Summary
              </Text>
              <Text size={300} style={{ fontStyle: 'italic' }}>{docSpec.executive_summary}</Text>
            </div>
          )}

          {docSpec.sections.map((section, idx) => (
            <div key={idx} className={styles.slidePreview} style={{ borderLeft: `3px solid ${tokens.colorNeutralStroke1}` }}>
              <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                <span className={styles.slideNumber}>{idx + 1}</span>
                <div style={{ flex: 1 }}>
                  <Text weight="semibold" size={400} style={{ display: 'block', marginBottom: '4px' }}>{section.title}</Text>
                  {section.paragraphs.length > 0 && (
                    <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground2, marginBottom: '4px' }}>
                      {section.paragraphs[0].substring(0, 150)}{section.paragraphs[0].length > 150 ? '...' : ''}
                    </Text>
                  )}
                  {section.bullets.length > 0 && (
                    <div>
                      {section.bullets.slice(0, 2).map((b, i) => (
                        <Text key={i} size={200} style={{ display: 'block', color: tokens.colorNeutralForeground2 }}>• {b}</Text>
                      ))}
                      {section.bullets.length > 2 && (
                        <Text size={200} style={{ color: tokens.colorNeutralForeground4 }}>+{section.bullets.length - 2} more</Text>
                      )}
                    </div>
                  )}
                  {section.table && (
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3, display: 'block' }}>
                      Table: {section.table.headers.join(' | ')} ({section.table.rows.length} rows)
                    </Text>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        {feedbackDialog}
      </div>
    );
  }

  // ─── XLSX Preview ─────────────────────────────────────────────────────────
  if (report && report.type === 'sheet') {
    const sheetSpec = report.spec as SheetSpec;
    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <Text size={600} weight="bold">{sheetSpec.title}</Text>
            <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3, marginTop: '4px' }}>
              {sheetSpec.rows.length} rows · {sheetSpec.columns.length} columns
            </Text>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button appearance="outline" onClick={() => setReport(null)}>Back to Builder</Button>
            <Button icon={<ArrowReset24Regular />} appearance="outline" onClick={handleRegenerate}>
              Regenerate
            </Button>
            <Button icon={<ArrowDownload24Regular />} appearance="primary" onClick={handleDownloadSheet}>
              Download Excel
            </Button>
          </div>
        </div>

        <div className={styles.preview}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ backgroundColor: tokens.colorBrandBackground, color: '#fff' }}>
                  {sheetSpec.columns.map((col, i) => (
                    <th key={i} style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 600 }}>{col.header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sheetSpec.rows.slice(0, 10).map((row, idx) => (
                  <tr key={idx} style={{
                    backgroundColor: row.highlight === 'green' ? '#E8F5E9' :
                      row.highlight === 'yellow' ? '#FFF8E1' :
                      row.highlight === 'red' ? '#FCE4EC' :
                      idx % 2 === 1 ? tokens.colorNeutralBackground2 : '#fff',
                  }}>
                    {row.values.map((val, i) => (
                      <td key={i} style={{ padding: '6px 12px', borderBottom: `1px solid ${tokens.colorNeutralStroke2}` }}>{val ?? ''}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {sheetSpec.rows.length > 10 && (
              <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground4, marginTop: '8px', textAlign: 'center' }}>
                +{sheetSpec.rows.length - 10} more rows in download
              </Text>
            )}
          </div>

          {sheetSpec.notes.length > 0 && (
            <div style={{ marginTop: '16px', padding: '12px', backgroundColor: tokens.colorNeutralBackground2, borderRadius: '6px' }}>
              {sheetSpec.notes.map((note, i) => (
                <Text key={i} size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3, fontStyle: 'italic' }}>{note}</Text>
              ))}
            </div>
          )}
        </div>
        {feedbackDialog}
      </div>
    );
  }

  // ─── Builder View ─────────────────────────────────────────────────────────
  return (
    <div>
      <Text size={600} weight="bold">{t('reports.title')}</Text>
      <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3, marginBottom: '16px' }}>
        {t('reports.subtitle')}
      </Text>

      {generating && (() => {
        const fmt = selectedTemplate ? getOutputFormat(selectedTemplate) : 'pptx';
        const DECK_AGENTS = [
          { key: 'planner', name: 'Planner', desc: 'Creating slide outline' },
          { key: 'content', name: 'Content Writer', desc: 'Filling slides with data & analysis' },
          { key: 'designer', name: 'Designer', desc: 'Assigning layouts & visual design' },
          { key: 'critic', name: 'Critic', desc: 'Reviewing quality & compliance' },
          { key: 'repair', name: 'Repair', desc: 'Fixing issues from review' },
        ];
        const DOC_AGENTS = [
          { key: 'doc_planner', name: 'Planner', desc: 'Creating section outline' },
          { key: 'doc_content', name: 'Content Writer', desc: 'Writing section content' },
        ];
        const SHEET_AGENTS = [
          { key: 'sheet_generator', name: 'Sheet Generator', desc: 'Generating data rows' },
        ];
        const agents = fmt === 'pptx' ? DECK_AGENTS : fmt === 'xlsx' ? SHEET_AGENTS : DOC_AGENTS;

        return (
          <div className={styles.generatingCard} style={{ marginBottom: '20px' }}>
            <Text weight="semibold" size={400} style={{ display: 'block', marginBottom: 16 }}>
              Generating Report...
            </Text>
            <div style={{ textAlign: 'left', maxWidth: 480, margin: '0 auto' }}>
              {agents.map((agent) => {
                const status = pipelineSteps[agent.key];
                const isDone = status === 'done';
                const isRunning = status === 'running';
                return (
                  <div key={agent.key} style={{
                    display: 'flex', alignItems: 'center', gap: 12,
                    padding: '10px 14px', marginBottom: 6, borderRadius: 8,
                    borderLeft: `3px solid ${isDone ? '#2e7d32' : isRunning ? '#e65100' : '#ccc'}`,
                    background: isDone ? '#f0f7f0' : isRunning ? '#fff5ee' : '#fafafa',
                    transition: 'all 0.3s ease',
                  }}>
                    <span style={{ fontSize: 16, width: 20, textAlign: 'center' }}>
                      {isDone ? '✓' : isRunning ? '⏳' : '○'}
                    </span>
                    <div style={{ flexGrow: 1 }}>
                      <span style={{ fontWeight: 600, fontSize: 13, color: isDone ? '#2e7d32' : isRunning ? '#e65100' : '#888' }}>
                        {agent.name}
                      </span>
                      <span style={{ fontSize: 12, color: '#666', marginLeft: 8 }}>
                        {agent.desc}
                      </span>
                    </div>
                    {isRunning && <Spinner size="tiny" />}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })()}

      <Text weight="semibold" size={400} style={{ display: 'block', marginBottom: '12px' }}>{t('reports.selectTemplate')}</Text>
      <div className={styles.templates}>
        {TEMPLATES.map(tpl => (
          <Card
            key={tpl.id}
            className={`${styles.templateCard} ${selectedTemplate === tpl.id ? styles.templateSelected : ''}`}
            onClick={() => setSelectedTemplate(tpl.id)}
          >
            <Text weight="semibold" size={300} style={{ display: 'block' }}>{tpl.name}</Text>
            <Badge appearance="outline" size="small" style={{ marginTop: '4px' }}>{tpl.format.toUpperCase()}</Badge>
            <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3, marginTop: '4px' }}>{tpl.desc}</Text>
          </Card>
        ))}
      </div>

      {selectedTemplate && (
        <div className={styles.configGrid}>
          <Card style={{ padding: '16px' }}>
            <Text weight="semibold" size={400} style={{ display: 'block', marginBottom: '12px' }}>{t('reports.sections')}</Text>
            {availableSections.map(s => (
              <div key={s} style={{ padding: '4px 0' }}>
                <Checkbox label={s} checked={sections.has(s)} onChange={() => toggleSection(s)} />
              </div>
            ))}
          </Card>
          <Card style={{ padding: '16px' }}>
            <Text weight="semibold" size={400} style={{ display: 'block', marginBottom: '12px' }}>{t('reports.config')}</Text>
            <div style={{ marginBottom: '12px' }}>
              <Text size={200} style={{ display: 'block', marginBottom: '4px', color: tokens.colorNeutralForeground3 }}>Audience</Text>
              <Dropdown value={audience} onOptionSelect={(_, d) => setAudience(d.optionValue || audience)} style={{ width: '100%' }}>
                <Option>S&OP Committee</Option>
                <Option>Executive Leadership</Option>
                <Option>Operations Team</Option>
                <Option>Supply Chain Director</Option>
              </Dropdown>
            </div>
            <div style={{ padding: '12px', backgroundColor: tokens.colorNeutralBackground2, borderRadius: '6px', marginBottom: '12px' }}>
              <Text size={200} weight="semibold" style={{ display: 'block', marginBottom: '4px' }}>
                Output Format: {getOutputFormat(selectedTemplate).toUpperCase()}
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                {getOutputFormat(selectedTemplate) === 'pptx' && 'PowerPoint deck with branded slide master, KPI cards, charts, and professional layouts.'}
                {getOutputFormat(selectedTemplate) === 'xlsx' && 'Excel spreadsheet with data tables, conditional formatting, and summary notes.'}
                {getOutputFormat(selectedTemplate) === 'docx' && 'Word document with executive sections, data tables, and branded headers.'}
              </Text>
            </div>
            <Button appearance="primary" onClick={() => setShowConfirmDialog(true)} style={{ width: '100%' }} disabled={generating}>
              {generating ? 'Generating...' : t('reports.generate')}
            </Button>
          </Card>
        </div>
      )}

      <div style={{ marginTop: '24px' }}>
        <Text weight="semibold" size={400} style={{ display: 'block', marginBottom: '12px' }}>{t('reports.recent')}</Text>
        <Card style={{ padding: '0' }}>
          {recentReports.length === 0 && (
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                No reports generated yet. Select a template above to get started.
              </Text>
            </div>
          )}
          {recentReports.map((r) => (
            <div key={r.id} className={styles.recentReport}>
              <div>
                <Text weight="semibold" size={300}>{r.name}</Text>
                <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3 }}>{r.template} · {r.date}</Text>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <Badge appearance="outline" size="small">{r.format.toUpperCase()}</Badge>
                {r.pages > 0 && <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>{r.pages} pages</Text>}
                {r.file_size > 0 && <Text size={200} style={{ color: tokens.colorNeutralForeground4 }}>{(r.file_size / 1024).toFixed(0)} KB</Text>}
                <Button
                  icon={<ArrowDownload24Regular />}
                  appearance="subtle"
                  size="small"
                  disabled={!r.download_url}
                  onClick={() => handleDownloadRecent(r)}
                />
              </div>
            </div>
          ))}
        </Card>
      </div>

      {/* Generate Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={(_, d) => { if (!d.open) setShowConfirmDialog(false); }}>
        <DialogSurface style={{ maxWidth: 520 }}>
          <DialogBody>
            <DialogTitle>{t('reports.confirmTitle')}</DialogTitle>
            <DialogContent>
              <div style={{ marginBottom: 16, padding: 12, background: tokens.colorNeutralBackground2, borderRadius: 6, lineHeight: 1.8 }}>
                <Text weight="semibold" size={200}>Template:</Text>{' '}
                {TEMPLATES.find(tp => tp.id === selectedTemplate)?.name || ''}<br />
                <Text weight="semibold" size={200}>Format:</Text>{' '}
                {selectedTemplate ? getOutputFormat(selectedTemplate).toUpperCase() : ''}<br />
                <Text weight="semibold" size={200}>Audience:</Text>{' '}
                {audience}<br />
                <Text weight="semibold" size={200}>Sections:</Text>{' '}
                {[...sections].join(', ') || 'All'}
              </div>
              <Text size={300} weight="semibold" style={{ display: 'block', marginBottom: 6 }}>
                {t('reports.addContext')}
              </Text>
              <Textarea
                value={additionalContext}
                onChange={(_, d) => setAdditionalContext(d.value)}
                placeholder={t('reports.contextPlaceholder')}
                rows={3}
                style={{ width: '100%' }}
              />
            </DialogContent>
            <DialogActions>
              <Button appearance="secondary" onClick={() => { setShowConfirmDialog(false); setAdditionalContext(''); }}>
                {t('reports.cancel')}
              </Button>
              <Button appearance="primary" onClick={() => { setShowConfirmDialog(false); generate(additionalContext); setAdditionalContext(''); }}>
                {t('reports.generate')}
              </Button>
            </DialogActions>
          </DialogBody>
        </DialogSurface>
      </Dialog>

      {feedbackDialog}
    </div>
  );
}
