import { useState, useEffect, useRef, useCallback } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Button, Textarea, Badge,
  Tab, TabList, Table, TableHeader, TableRow, TableHeaderCell, TableBody, TableCell,
} from '@fluentui/react-components';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  AreaChart, Area, LineChart, Line,
} from 'recharts';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { setPendingChatMessage, TOOL_START_EVENT, TOOL_COMPLETE_EVENT } from '../components/CopilotActions';
import { ScenarioPipelineProgress } from '../components/ScenarioPipelineProgress';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '20px' },
  chips: { display: 'flex', gap: '10px', flexWrap: 'wrap' },
  chip: {
    padding: '8px 14px',
    borderRadius: '18px',
    border: `1px solid ${tokens.colorNeutralStroke1}`,
    background: tokens.colorNeutralBackground1,
    cursor: 'pointer',
    fontSize: '13px',
    transition: 'all 0.2s',
    ':hover': {
      background: tokens.colorBrandBackground2,
      borderColor: tokens.colorBrandStroke1,
    },
  },
  inputCard: { padding: '16px' },
  tabs: { marginTop: '4px' },
  grid2: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' },
  grid3: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' },
  statCard: { padding: '16px', textAlign: 'center' as const },
  riskCard: { padding: '16px' },
  mitigationCard: {
    padding: '12px 16px',
    borderLeft: `4px solid ${tokens.colorBrandBackground}`,
    marginBottom: '8px',
  },
});

const SCENARIO_SUGGESTIONS = [
  { labelKey: 'scenarios.chip.rateIncrease', message: 'Run scenario analysis: Airbus A220 program rate increase of 30% over next 6 months' },
  { labelKey: 'scenarios.chip.forgingDelay', message: 'Run scenario analysis: Primary titanium forging supplier delayed 28 days due to facility maintenance' },
  { labelKey: 'scenarios.chip.aog', message: 'Run scenario analysis: AOG emergency requiring 3 B737 nose landing gear assemblies within 72 hours' },
  { labelKey: 'scenarios.chip.titanium', message: 'Run scenario analysis: Titanium supply disrupted 60% for 3 months due to geopolitical sanctions' },
  { labelKey: 'scenarios.chip.multiFactor', message: 'Run scenario analysis: A320 program rate increase 20% combined with forging supplier delay of 14 days' },
];

interface ScenarioResult {
  scenario_type: string;
  parameters: Record<string, unknown>;
  demand_impact: {
    affected_skus: AffectedSku[];
    weekly_timeline: TimelineWeek[];
    summary_stats: Record<string, number>;
  };
  inventory_impact: {
    sku_projections: SkuProjection[];
    timeline: TimelineEntry[];
    aggregate: Record<string, number>;
  };
  supply_impact: {
    alternative_suppliers: SupplierAlt[];
    supply_gap: Record<string, number>;
  };
  production_impact: {
    affected_lines: ProductionLine[];
    production_options: ProductionOpt[];
    feasibility: string;
  };
  kpi_projection: {
    baseline: Record<string, number>;
    projected: Record<string, number>;
    deltas: Record<string, number>;
    confidence_bands: Record<string, { best: number; expected: number; worst: number }>;
    target_breaches: string[];
    mitigation_options: MitigationOpt[];
  };
  baseline_kpis: Record<string, number>;
  projected_impact: Record<string, number>;
  risk_assessment: string;
  recommended_actions: string[];
  mitigation_options: MitigationOpt[];
}

interface AffectedSku {
  sku_id: string;
  sku_name: string;
  category: string;
  abc_class: string;
  baseline_weekly_demand: number;
  adjusted_weekly_demand: number;
  demand_delta_pct: number;
  weeks_until_stockout: number;
  current_dos: number;
  severity: string;
}

interface TimelineWeek {
  week: number;
  label: string;
  total_baseline_demand: number;
  total_adjusted_demand: number;
  total_stock: number;
  net_position: number;
  skus_below_safety: number;
  skus_stockout: number;
}

interface TimelineEntry {
  week: number;
  label: string;
  total_stock_mt: number;
  total_demand_mt: number;
  net_position: number;
  skus_below_safety: number;
  skus_stockout: number;
}

interface SkuProjection {
  sku_id: string;
  sku_name: string;
  current_dos: number;
  projected_dos: number;
  stockout_week: number | null;
  safety_stock_breached: boolean;
  projected_lost_sales_cad: number;
}

interface SupplierAlt {
  id: string;
  name: string;
  available_capacity_units: number;
  lead_time_days: number;
  reliability: number;
  cost_premium_pct: number;
}

interface ProductionLine {
  id: string;
  name: string;
  plant: string;
  current_utilization: number;
  spare_capacity_units_day: number;
}

interface ProductionOpt {
  option: string;
  extra_mt_per_day: number;
  duration_days: number;
  impact: string;
}

interface MitigationOpt {
  action: string;
  cost_cad: number;
  fill_rate_recovery: number;
  lead_time_days: number;
  priority: string;
}

const SEVERITY_COLORS: Record<string, { bg: string; text: string }> = {
  critical: { bg: '#fde8e8', text: '#c41e3a' },
  warning: { bg: '#fff3cd', text: '#856404' },
  safe: { bg: '#d4edda', text: '#155724' },
};

interface HistoryEntry {
  id: string;
  name: string;
  scenario_type: string;
  parameters: Record<string, unknown>;
  kpi_impact: Record<string, number>;
  affected_skus: string[];
  risk_assessment: string;
  created_at: string;
}

export default function ScenarioPlanner() {
  const styles = useStyles();
  const { t } = useI18n();
  const [scenarioText, setScenarioText] = useState('');
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [running, setRunning] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [compareIds, setCompareIds] = useState<Set<string>>(new Set());
  const [showComparison, setShowComparison] = useState(false);

  const loadHistory = useCallback(() => {
    fetch('/api/scenarios', { headers: getSessionHeader() })
      .then(r => r.json())
      .then(data => { if (Array.isArray(data)) setHistory(data); })
      .catch(() => {});
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  const handleResult = useCallback((data: ScenarioResult) => {
    setResult(data);
    setRunning(false);
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    fetch('/api/reports/latest', { method: 'DELETE', headers: getSessionHeader() }).catch(() => {});
    loadHistory();
  }, [loadHistory]);

  const startPolling = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch('/api/reports/latest', { headers: getSessionHeader() });
        const data = await res.json();
        if (data?.result?.pending_scenario) {
          handleResult(data.result.pending_scenario);
        }
      } catch {}
    }, 1000);
  }, [handleResult]);

  useEffect(() => {
    const checkForResult = async () => {
      try {
        const res = await fetch('/api/reports/latest', { headers: getSessionHeader() });
        const data = await res.json();
        if (data?.result?.pending_scenario) {
          handleResult(data.result.pending_scenario);
        } else if (data?.result?.scenario_progress) {
          setRunning(true);
          startPolling();
        }
      } catch {}
    };
    checkForResult();
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [handleResult, startPolling]);

  useEffect(() => {
    const handler = (e: Event) => {
      const { name } = (e as CustomEvent).detail;
      if (name === 'scenario_analysis') {
        setRunning(true);
        setResult(null);
        startPolling();
      }
    };
    window.addEventListener(TOOL_START_EVENT, handler);
    return () => window.removeEventListener(TOOL_START_EVENT, handler);
  }, [startPolling]);

  useEffect(() => {
    const handler = (e: Event) => {
      const { name } = (e as CustomEvent).detail;
      if (name === 'scenario_analysis') {
        setTimeout(async () => {
          try {
            const res = await fetch('/api/reports/latest', { headers: getSessionHeader() });
            const json = await res.json();
            if (json?.result?.pending_scenario) {
              handleResult(json.result.pending_scenario);
            }
          } catch {}
        }, 500);
      }
    };
    window.addEventListener(TOOL_COMPLETE_EVENT, handler);
    return () => window.removeEventListener(TOOL_COMPLETE_EVENT, handler);
  }, [handleResult]);

  const sendToAgent = (message: string) => {
    setRunning(true);
    setResult(null);
    startPolling();
    setPendingChatMessage(message);
  };

  const handleChipClick = (message: string) => {
    setScenarioText('');
    sendToAgent(message);
  };

  const handleSubmit = () => {
    if (!scenarioText.trim()) return;
    const msg = scenarioText.trim().toLowerCase().startsWith('run scenario')
      ? scenarioText.trim()
      : `Run scenario analysis: ${scenarioText.trim()}`;
    sendToAgent(msg);
  };

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('scenarios.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('scenarios.subtitle')}</Text>

      <Card className={styles.inputCard}>
        <Text weight="semibold" size={300} style={{ marginBottom: 10, display: 'block' }}>
          {t('scenarios.quickScenarios')}
        </Text>
        <div className={styles.chips}>
          {SCENARIO_SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              className={styles.chip}
              onClick={() => handleChipClick(s.message)}
              disabled={running}
            >
              {t(s.labelKey)}
            </button>
          ))}
        </div>

        <div style={{ marginTop: 16 }}>
          <Text weight="semibold" size={300} style={{ marginBottom: 6, display: 'block' }}>
            {t('scenarios.customScenario')}
          </Text>
          <Textarea
            placeholder={t('scenarios.placeholder')}
            value={scenarioText}
            onChange={(_, d) => setScenarioText(d.value)}
            style={{ width: '100%', minHeight: 80 }}
            disabled={running}
          />
          <Button
            appearance="primary"
            onClick={handleSubmit}
            disabled={running || !scenarioText.trim()}
            style={{ marginTop: 8 }}
          >
            {t('scenarios.runAnalysis')}
          </Button>
        </div>
      </Card>

      {running && (
        <ScenarioPipelineProgress onResult={handleResult} />
      )}

      {result && (
        <>
          <TabList selectedValue={activeTab} onTabSelect={(_, d) => setActiveTab(d.value as string)} className={styles.tabs}>
            <Tab value="summary">{t('scenarios.impactSummary')}</Tab>
            <Tab value="skus">{t('scenarios.affectedSkus')}</Tab>
            <Tab value="timeline">{t('scenarios.timeline')}</Tab>
            <Tab value="mitigation">{t('scenarios.mitigation')}</Tab>
          </TabList>

          {activeTab === 'summary' && <SummaryTab result={result} styles={styles} t={t} />}
          {activeTab === 'skus' && <AffectedSkusTab result={result} t={t} />}
          {activeTab === 'timeline' && <TimelineTab result={result} t={t} />}
          {activeTab === 'mitigation' && <MitigationTab result={result} styles={styles} t={t} />}
        </>
      )}

      {/* Scenario History */}
      {history.length > 0 && (
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <Text weight="semibold" size={400}>{t('scenarios.history')}</Text>
            {compareIds.size === 2 && (
              <Button appearance="primary" size="small" onClick={() => setShowComparison(true)}>
                {t('scenarios.compareSelected')} ({compareIds.size})
              </Button>
            )}
          </div>
          <Table size="small">
            <TableHeader>
              <TableRow>
                <TableHeaderCell style={{ width: 40 }}></TableHeaderCell>
                <TableHeaderCell>{t('nav.scenarios')}</TableHeaderCell>
                <TableHeaderCell>{t('scenarios.type')}</TableHeaderCell>
                <TableHeaderCell>{t('scenarios.skusAffected')}</TableHeaderCell>
                <TableHeaderCell>{t('common.date')}</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.map(h => (
                <TableRow key={h.id}>
                  <TableCell>
                    <input
                      type="checkbox"
                      checked={compareIds.has(h.id)}
                      onChange={(e) => {
                        const next = new Set(compareIds);
                        if (e.target.checked) {
                          if (next.size >= 2) return;
                          next.add(h.id);
                        } else {
                          next.delete(h.id);
                        }
                        setCompareIds(next);
                      }}
                    />
                  </TableCell>
                  <TableCell><Text size={200} weight="semibold">{h.name || h.scenario_type}</Text></TableCell>
                  <TableCell><Badge appearance="outline" size="small">{h.scenario_type}</Badge></TableCell>
                  <TableCell><Text size={200}>{h.affected_skus?.length || 0}</Text></TableCell>
                  <TableCell><Text size={200}>{h.created_at?.slice(0, 10)}</Text></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* Comparison View */}
      {showComparison && compareIds.size === 2 && (
        <ScenarioComparison
          scenarios={history.filter(h => compareIds.has(h.id))}
          onClose={() => setShowComparison(false)}
          t={t}
        />
      )}
    </div>
  );
}

function ScenarioComparison({ scenarios, onClose, t }: { scenarios: HistoryEntry[]; onClose: () => void; t: (k: string) => string }) {
  if (scenarios.length < 2) return null;
  const [a, b] = scenarios;
  const allKpiKeys = [...new Set([...Object.keys(a.kpi_impact || {}), ...Object.keys(b.kpi_impact || {})])];

  return (
    <Card style={{ padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Text weight="semibold" size={400}>{t('scenarios.comparison')}</Text>
        <Button appearance="subtle" size="small" onClick={onClose}>{t('common.close')}</Button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card style={{ padding: 12, background: tokens.colorNeutralBackground3 }}>
          <Text weight="semibold" size={300}>A: {a.name || a.scenario_type}</Text>
          <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3 }}>{a.created_at?.slice(0, 10)} | {a.affected_skus?.length} SKUs</Text>
        </Card>
        <Card style={{ padding: 12, background: tokens.colorNeutralBackground3 }}>
          <Text weight="semibold" size={300}>B: {b.name || b.scenario_type}</Text>
          <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3 }}>{b.created_at?.slice(0, 10)} | {b.affected_skus?.length} SKUs</Text>
        </Card>
      </div>
      <Table size="small">
        <TableHeader>
          <TableRow>
            <TableHeaderCell>KPI</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.scenarioA')}</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.scenarioB')}</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.deltaBA')}</TableHeaderCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {allKpiKeys.map(key => {
            const valA = (a.kpi_impact || {})[key] ?? 0;
            const valB = (b.kpi_impact || {})[key] ?? 0;
            const delta = Number(valB) - Number(valA);
            return (
              <TableRow key={key}>
                <TableCell><Text size={200}>{key.replace(/_/g, ' ')}</Text></TableCell>
                <TableCell><Text size={200}>{valA}</Text></TableCell>
                <TableCell><Text size={200}>{valB}</Text></TableCell>
                <TableCell>
                  <Text size={200} weight="semibold" style={{ color: delta > 0 ? '#4CAF50' : delta < 0 ? '#c41e3a' : undefined }}>
                    {delta > 0 ? '+' : ''}{delta.toFixed(2)}
                  </Text>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}

function SummaryTab({ result, styles, t }: { result: ScenarioResult; styles: any; t: (k: string) => string }) {
  const stats = result.demand_impact.summary_stats;
  const kpi = result.kpi_projection;

  const kpiChartData = Object.keys(kpi.baseline).map(key => ({
    name: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    Baseline: kpi.baseline[key],
    Projected: kpi.projected[key],
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className={styles.grid3}>
        <Card className={styles.statCard}>
          <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>{t('scenarios.totalAffected')}</Text>
          <Text size={700} weight="bold" style={{ display: 'block', marginTop: 4 }}>{stats.total_affected_skus}</Text>
        </Card>
        <Card className={styles.statCard}>
          <Text size={200} style={{ color: '#c41e3a' }}>{t('scenarios.critical')}</Text>
          <Text size={700} weight="bold" style={{ display: 'block', marginTop: 4, color: '#c41e3a' }}>{stats.critical_skus}</Text>
        </Card>
        <Card className={styles.statCard}>
          <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>{t('scenarios.avgDemandIncrease')}</Text>
          <Text size={700} weight="bold" style={{ display: 'block', marginTop: 4 }}>{stats.avg_demand_increase_pct}%</Text>
        </Card>
      </div>

      <div className={styles.grid2}>
        <Card style={{ padding: 16 }}>
          <Text weight="semibold" size={400}>{t('scenarios.kpiComparison')}</Text>
          <div style={{ height: 280, marginTop: 12 }}>
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <BarChart data={kpiChartData} margin={{ top: 10, right: 10, left: 0, bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-20} textAnchor="end" fontSize={10} height={60} />
                <YAxis fontSize={11} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Baseline" fill="#90caf9" radius={[3, 3, 0, 0]} name={t('scenarios.baseline')} />
                <Bar dataKey="Projected" fill="#1565c0" radius={[3, 3, 0, 0]} name={t('scenarios.projected')} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className={styles.riskCard}>
          <Text weight="semibold" size={400}>{t('scenarios.riskAssessment')}</Text>
          <Text size={300} style={{ marginTop: 12, display: 'block', lineHeight: '1.5' }}>{result.risk_assessment}</Text>

          {kpi.target_breaches.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <Text weight="semibold" size={200} style={{ color: '#c41e3a' }}>{t('scenarios.targetBreaches')}:</Text>
              <ul style={{ margin: '4px 0', paddingLeft: 16 }}>
                {kpi.target_breaches.map((b, i) => (
                  <li key={i}><Text size={200} style={{ color: '#c41e3a' }}>{b}</Text></li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ marginTop: 16 }}>
            <Text weight="semibold" size={300}>{t('scenarios.recommendations')}</Text>
            <ul style={{ margin: '8px 0', paddingLeft: 16 }}>
              {result.recommended_actions.map((a, i) => (
                <li key={i} style={{ marginBottom: 4 }}><Text size={200}>{a}</Text></li>
              ))}
            </ul>
          </div>
        </Card>
      </div>

      <Card style={{ padding: 16 }}>
        <Text weight="semibold" size={400}>{t('scenarios.kpiDeltas')}</Text>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 12 }}>
          {Object.entries(kpi.deltas).map(([key, val]) => (
            <div key={key} style={{
              padding: '8px 14px',
              borderRadius: 8,
              background: val < 0 && (key === 'fill_rate' || key === 'on_time_delivery' || key === 'inventory_dos') ? '#fde8e8'
                : val > 0 && (key === 'stockout_rate' || key === 'working_capital_mm' || key === 'forecast_accuracy_mape') ? '#fde8e8'
                : '#e8f5e9',
              minWidth: 120,
            }}>
              <Text size={200} style={{ color: '#666', display: 'block' }}>{key.replace(/_/g, ' ')}</Text>
              <Text weight="bold" size={300} style={{ color: val < 0 && key.includes('rate') ? '#c41e3a' : val > 0 && key === 'stockout_rate' ? '#c41e3a' : '#333' }}>
                {val > 0 ? '+' : ''}{val}
              </Text>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function AffectedSkusTab({ result, t }: { result: ScenarioResult; t: (k: string) => string }) {
  const skus = result.demand_impact.affected_skus;

  return (
    <Card style={{ padding: 16, overflow: 'auto' }}>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <Badge color="danger" appearance="filled">{result.demand_impact.summary_stats.critical_skus} {t('scenarios.critical')}</Badge>
        <Badge color="warning" appearance="filled">{result.demand_impact.summary_stats.warning_skus} {t('scenarios.warning')}</Badge>
        <Badge color="success" appearance="filled">{result.demand_impact.summary_stats.safe_skus} {t('scenarios.safe')}</Badge>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHeaderCell>{t('common.sku')}</TableHeaderCell>
            <TableHeaderCell>{t('common.category')}</TableHeaderCell>
            <TableHeaderCell>ABC</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.baselineAdj')}</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.deltaPct')}</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.weeksToStockout')}</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.currentDos')}</TableHeaderCell>
            <TableHeaderCell>{t('scenarios.severity')}</TableHeaderCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {skus.map(sku => {
            const sev = SEVERITY_COLORS[sku.severity] || SEVERITY_COLORS.safe;
            return (
              <TableRow key={sku.sku_id}>
                <TableCell><Text size={200} weight="semibold">{sku.sku_name}</Text></TableCell>
                <TableCell><Text size={200}>{sku.category}</Text></TableCell>
                <TableCell><Text size={200}>{sku.abc_class}</Text></TableCell>
                <TableCell><Text size={200}>{sku.baseline_weekly_demand} / {sku.adjusted_weekly_demand}</Text></TableCell>
                <TableCell><Text size={200} weight="semibold" style={{ color: '#c41e3a' }}>+{sku.demand_delta_pct}%</Text></TableCell>
                <TableCell><Text size={200} weight="semibold" style={{ color: sku.weeks_until_stockout < 2 ? '#c41e3a' : sku.weeks_until_stockout < 4 ? '#856404' : '#155724' }}>{sku.weeks_until_stockout}</Text></TableCell>
                <TableCell><Text size={200}>{sku.current_dos}</Text></TableCell>
                <TableCell>
                  <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600, background: sev.bg, color: sev.text }}>
                    {t(`scenarios.${sku.severity}`).toUpperCase()}
                  </span>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}

function TimelineTab({ result, t }: { result: ScenarioResult; t: (k: string) => string }) {
  const demandTimeline = result.demand_impact.weekly_timeline;
  const inventoryTimeline = result.inventory_impact.timeline;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card style={{ padding: 16 }}>
        <Text weight="semibold" size={400}>{t('scenarios.demandChart')}</Text>
        <div style={{ height: 250, marginTop: 12 }}>
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <AreaChart data={demandTimeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" fontSize={11} />
              <YAxis fontSize={11} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="total_baseline_demand" name={t('scenarios.baseline')} stroke="#90caf9" fill="#e3f2fd" />
              <Area type="monotone" dataKey="total_adjusted_demand" name={t('scenarios.adjusted')} stroke="#1565c0" fill="#bbdefb" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card style={{ padding: 16 }}>
        <Text weight="semibold" size={400}>{t('scenarios.inventoryDepletion')}</Text>
        <div style={{ height: 250, marginTop: 12 }}>
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <LineChart data={inventoryTimeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" fontSize={11} />
              <YAxis yAxisId="left" fontSize={11} />
              <YAxis yAxisId="right" orientation="right" fontSize={11} />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="total_stock_mt" name={t('scenarios.totalStock')} stroke="#2e7d32" strokeWidth={2} />
              <Line yAxisId="left" type="monotone" dataKey="net_position" name={t('scenarios.netPosition')} stroke="#c41e3a" strokeWidth={2} strokeDasharray="5 5" />
              <Line yAxisId="right" type="monotone" dataKey="skus_stockout" name={t('scenarios.skusInStockout')} stroke="#ff6f00" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card style={{ padding: 16 }}>
        <Text weight="semibold" size={400}>{t('scenarios.stockVsDemand')}</Text>
        <div style={{ height: 220, marginTop: 12 }}>
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <BarChart data={inventoryTimeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" fontSize={11} />
              <YAxis fontSize={11} />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_stock_mt" name={t('scenarios.stockMt')} fill="#66bb6a" radius={[3, 3, 0, 0]} />
              <Bar dataKey="total_demand_mt" name={t('scenarios.demandMt')} fill="#ef5350" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}

function MitigationTab({ result, styles, t }: { result: ScenarioResult; styles: any; t: (k: string) => string }) {
  const mitigations = result.mitigation_options || result.kpi_projection.mitigation_options || [];
  const supply = result.supply_impact;
  const production = result.production_impact;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card style={{ padding: 16 }}>
        <Text weight="semibold" size={400}>{t('scenarios.mitigationOptions')}</Text>
        <div style={{ marginTop: 12 }}>
          {mitigations.map((m, i) => (
            <div key={i} className={styles.mitigationCard} style={{
              borderLeftColor: m.priority === 'critical' ? '#c41e3a' : m.priority === 'high' ? '#ff6f00' : '#1565c0',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <span style={{
                    fontSize: 10, fontWeight: 700, textTransform: 'uppercase' as const,
                    padding: '2px 6px', borderRadius: 3, marginRight: 8,
                    background: m.priority === 'critical' ? '#fde8e8' : m.priority === 'high' ? '#fff3e0' : '#e3f2fd',
                    color: m.priority === 'critical' ? '#c41e3a' : m.priority === 'high' ? '#e65100' : '#1565c0',
                  }}>
                    {m.priority}
                  </span>
                  <Text size={300} weight="semibold">{m.action}</Text>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 20, marginTop: 8 }}>
                <Text size={200} style={{ color: '#666' }}>{t('scenarios.cost')}: CAD {m.cost_cad.toLocaleString()}</Text>
                <Text size={200} style={{ color: '#666' }}>{t('scenarios.fillRateRecovery')}: +{m.fill_rate_recovery}%</Text>
                <Text size={200} style={{ color: '#666' }}>{t('scenarios.leadTimeDays')}: {m.lead_time_days} {t('scenarios.days')}</Text>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className={styles.grid2}>
        <Card style={{ padding: 16 }}>
          <Text weight="semibold" size={400}>{t('scenarios.altSuppliers')}</Text>
          <div style={{ marginTop: 12 }}>
            <Table size="small">
              <TableHeader>
                <TableRow>
                  <TableHeaderCell>{t('common.supplier')}</TableHeaderCell>
                  <TableHeaderCell>{t('scenarios.capacityMt')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.leadTime')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.reliability')}</TableHeaderCell>
                  <TableHeaderCell>{t('scenarios.premium')}</TableHeaderCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {supply.alternative_suppliers.map(s => (
                  <TableRow key={s.id}>
                    <TableCell><Text size={200}>{s.name}</Text></TableCell>
                    <TableCell><Text size={200}>{s.available_capacity_units}</Text></TableCell>
                    <TableCell><Text size={200}>{s.lead_time_days}d</Text></TableCell>
                    <TableCell><Text size={200}>{s.reliability}%</Text></TableCell>
                    <TableCell><Text size={200}>+{s.cost_premium_pct}%</Text></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <div style={{ marginTop: 8, padding: '6px 10px', background: '#f5f5f5', borderRadius: 6 }}>
              <Text size={200}>
                {t('scenarios.supplyGap')}: <strong>{supply.supply_gap.coverage_pct}%</strong> |
                {t('scenarios.needed')}: {supply.supply_gap.total_needed_mt} MT |
                {t('scenarios.available')}: {supply.supply_gap.available_mt} MT
              </Text>
            </div>
          </div>
        </Card>

        <Card style={{ padding: 16 }}>
          <Text weight="semibold" size={400}>{t('scenarios.productionCapacity')}</Text>
          <div style={{ marginTop: 8, marginBottom: 12 }}>
            <Badge
              color={production.feasibility === 'full' ? 'success' : production.feasibility === 'partial' ? 'warning' : 'danger'}
              appearance="filled"
            >
              {t('scenarios.feasibility')}: {production.feasibility.toUpperCase()}
            </Badge>
          </div>
          <Table size="small">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>{t('common.line')}</TableHeaderCell>
                <TableHeaderCell>{t('common.plant')}</TableHeaderCell>
                <TableHeaderCell>{t('common.utilization')}</TableHeaderCell>
                <TableHeaderCell>{t('scenarios.spareMtDay')}</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {production.affected_lines.map(line => (
                <TableRow key={line.id}>
                  <TableCell><Text size={200}>{line.name}</Text></TableCell>
                  <TableCell><Text size={200}>{line.plant}</Text></TableCell>
                  <TableCell><Text size={200}>{line.current_utilization}%</Text></TableCell>
                  <TableCell><Text size={200}>{line.spare_capacity_units_day}</Text></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {production.production_options.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <Text size={200} weight="semibold">{t('scenarios.surgeOptions')}:</Text>
              <ul style={{ margin: '4px 0', paddingLeft: 16 }}>
                {production.production_options.map((opt, i) => (
                  <li key={i}><Text size={200}>{opt.option} (+{opt.extra_mt_per_day} MT/day for {opt.duration_days}d)</Text></li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
