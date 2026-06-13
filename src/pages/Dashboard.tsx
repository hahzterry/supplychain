import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Badge,
  Spinner,
} from '@fluentui/react-components';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { setPendingChatMessage } from '../components/CopilotActions';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '24px' },
  kpiRow: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' },
  kpiCard: { padding: '16px' },
  kpiValue: { fontSize: '28px', fontWeight: tokens.fontWeightBold },
  kpiLabel: { color: tokens.colorNeutralForeground3, fontSize: '13px' },
  kpiTarget: { color: tokens.colorNeutralForeground4, fontSize: '11px' },
  chartsRow: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' },
  alertsList: { display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' },
  alertItem: { display: 'flex', alignItems: 'center', gap: '8px', padding: '8px', borderRadius: '4px', backgroundColor: tokens.colorNeutralBackground3 },
});

const RISK_COLORS = { critical: '#d32f2f', warning: '#f57c00', normal: '#388e3c', excess: '#1565c0' };

interface KPIs {
  forecast_accuracy_mape: number;
  inventory_dos: number;
  fill_rate: number;
  stockout_rate: number;
  obsolescence_rate: number;
  alerts_open: number;
  pending_actions: number;
  production_utilization: number;
}

export default function Dashboard() {
  const styles = useStyles();
  const { t } = useI18n();
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [riskMatrix, setRiskMatrix] = useState<Record<string, number>>({});
  const [alerts, setAlerts] = useState<Array<{ id: string; title: string; severity: string }>>([]);

  useEffect(() => {
    const headers = getSessionHeader();
    fetch('/api/kpis', { headers }).then(r => r.json()).then(setKpis);
    fetch('/api/inventory/risk-matrix', { headers }).then(r => r.json()).then(setRiskMatrix);
    fetch('/api/alerts?severity=critical', { headers }).then(r => r.json()).then(setAlerts);
  }, []);

  if (!kpis) return <Spinner label={t('common.loading')} />;

  const riskData = Object.entries(riskMatrix).map(([name, value]) => ({ name, value }));

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('dashboard.title')}</Text>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {[
          { label: t('dashboard.chip.brief'), message: 'Give me the morning supply brief' },
          { label: t('dashboard.chip.alerts'), message: 'Show me all critical supply chain alerts' },
          { label: t('dashboard.chip.kpi'), message: 'Summarize this week\'s KPI performance' },
          { label: t('dashboard.chip.risk'), message: 'Which SKUs are at highest risk of stockout?' },
        ].map((s, i) => (
          <button key={i} onClick={() => setPendingChatMessage(s.message)} style={{
            borderRadius: 18, border: '1px solid #e0d4b0', background: '#fdf8ee',
            padding: '6px 14px', fontSize: 12, color: '#8B6914', cursor: 'pointer',
          }}>{s.label}</button>
        ))}
      </div>

      <div className={styles.kpiRow}>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.forecast_accuracy_mape}%</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.forecastAccuracy')} (MAPE)</Text>
          <Text className={styles.kpiTarget}>{t('dashboard.target.mape')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.inventory_dos}</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.inventoryDOS')}</Text>
          <Text className={styles.kpiTarget}>{t('dashboard.target.dos')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.fill_rate}%</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.fillRate')}</Text>
          <Text className={styles.kpiTarget}>{t('dashboard.target.fill')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.stockout_rate}%</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.stockoutRate')}</Text>
          <Text className={styles.kpiTarget}>{t('dashboard.target.stockout')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.alerts_open}</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.criticalAlerts')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.pending_actions}</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.pendingActions')}</Text>
        </Card>
      </div>

      <div className={styles.chartsRow}>
        <Card>
          <CardHeader header={<Text weight="semibold">{t('dashboard.riskOverview')}</Text>} />
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                {riskData.map((entry) => (
                  <Cell key={entry.name} fill={RISK_COLORS[entry.name as keyof typeof RISK_COLORS] || '#999'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <CardHeader header={<Text weight="semibold">{t('dashboard.criticalAlerts')}</Text>} />
          <div className={styles.alertsList}>
            {alerts.slice(0, 4).map(alert => (
              <div key={alert.id} className={styles.alertItem}>
                <Badge color="danger" size="small" />
                <Text size={200}>{alert.title}</Text>
              </div>
            ))}
          </div>
        </Card>
      </div>

    </div>
  );
}
