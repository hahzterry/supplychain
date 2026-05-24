import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Badge, Button,
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
  quickActions: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginTop: '12px' },
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

  if (!kpis) return <Spinner label="Loading..." />;

  const riskData = Object.entries(riskMatrix).map(([name, value]) => ({ name, value }));

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('dashboard.title')}</Text>

      <div className={styles.kpiRow}>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.forecast_accuracy_mape}%</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.forecastAccuracy')} (MAPE)</Text>
          <Text className={styles.kpiTarget}>Target: &lt; 15%</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.inventory_dos}</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.inventoryDOS')}</Text>
          <Text className={styles.kpiTarget}>Target: 14-21 days</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.fill_rate}%</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.fillRate')}</Text>
          <Text className={styles.kpiTarget}>Target: &gt; 97%</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{kpis.stockout_rate}%</Text>
          <Text className={styles.kpiLabel}>{t('dashboard.stockoutRate')}</Text>
          <Text className={styles.kpiTarget}>Target: &lt; 2%</Text>
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

      <Card>
        <CardHeader header={<Text weight="semibold">{t('dashboard.quickActions')}</Text>} />
        <div className={styles.quickActions}>
          <Button appearance="outline" onClick={() => setPendingChatMessage('Give me the morning supply brief')}>{t('dashboard.runBrief')}</Button>
          <Button appearance="outline" onClick={() => setPendingChatMessage('Check inventory stockout risks')}>{t('dashboard.checkRisks')}</Button>
          <Button appearance="outline" onClick={() => setPendingChatMessage('Generate S&OP report')}>{t('dashboard.genReport')}</Button>
        </div>
      </Card>
    </div>
  );
}
