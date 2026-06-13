import { useEffect, useState, useRef } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Dropdown, Option, Spinner,
} from '@fluentui/react-components';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';
import { setPendingChatMessage } from '../components/CopilotActions';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '24px' },
  controls: { display: 'flex', gap: '16px', alignItems: 'center' },
  chartCard: { padding: '16px' },
  statsRow: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' },
});

interface Forecast {
  sku_id: string;
  sku_name: string;
  week: string;
  point_forecast: number;
  lower_80: number;
  upper_80: number;
  lower_95: number;
  upper_95: number;
  confidence: string;
}

export default function DemandForecast() {
  const styles = useStyles();
  const { t } = useI18n();
  const { openSkuDetail } = useDetailDrawer();
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [selectedSku, setSelectedSku] = useState('');
  const [skus, setSkus] = useState<Array<{ id: string; name: string }>>([]);
  const [loading, setLoading] = useState(true);
  const pendingCheckRef = useRef(false);

  useEffect(() => {
    const headers = getSessionHeader();
    fetch('/api/skus', { headers }).then(r => r.json()).then(data => {
      const mapped = data.map((s: { id: string; name: string }) => ({ id: s.id, name: s.name }));
      setSkus(mapped);
      if (!selectedSku && mapped.length) setSelectedSku(mapped[0].id);
    });
  }, []);

  // Poll for chat-triggered forecast
  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('/api/reports/latest', { headers: getSessionHeader() });
        const data = await res.json();
        if (data?.result?.pending_forecast) {
          const { sku_id } = data.result.pending_forecast;
          if (sku_id && sku_id !== selectedSku) {
            setSelectedSku(sku_id);
          }
          fetch('/api/reports/latest', { method: 'DELETE', headers: getSessionHeader() }).catch(() => {});
          pendingCheckRef.current = false;
        }
      } catch {}
    };
    const interval = setInterval(check, 2000);
    check();
    return () => clearInterval(interval);
  }, [selectedSku]);

  useEffect(() => {
    if (!selectedSku) return;
    setLoading(true);
    const headers = getSessionHeader();
    fetch(`/api/demand/forecast?sku_id=${selectedSku}`, { headers })
      .then(r => r.json())
      .then(data => { setForecasts(data); setLoading(false); });
  }, [selectedSku]);

  const chartData = forecasts.map(f => ({
    week: f.week,
    forecast: Math.round(f.point_forecast),
    lower80: Math.round(f.lower_80),
    upper80: Math.round(f.upper_80),
    lower95: Math.round(f.lower_95),
    upper95: Math.round(f.upper_95),
  }));

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('demand.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('demand.subtitle')}</Text>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {[
          { label: t('demand.chip.accuracy'), message: 'Analyze demand forecast accuracy trends across all programs' },
          { label: t('demand.chip.spikes'), message: 'Which SKUs show abnormal demand spikes in the next 4 weeks?' },
          { label: t('demand.chip.seasonal'), message: 'Compare seasonal demand patterns for landing gear assemblies' },
          { label: t('demand.chip.program'), message: 'Show demand forecast breakdown for A320 program' },
        ].map((s, i) => (
          <button key={i} onClick={() => setPendingChatMessage(s.message)} style={{
            borderRadius: 18, border: '1px solid #e0d4b0', background: '#fdf8ee',
            padding: '6px 14px', fontSize: 12, color: '#8B6914', cursor: 'pointer',
          }}>{s.label}</button>
        ))}
      </div>

      <div className={styles.controls}>
        <Dropdown
          placeholder={t('demand.selectSku')}
          value={skus.find(s => s.id === selectedSku)?.name || selectedSku}
          onOptionSelect={(_, data) => { if (data.optionValue) setSelectedSku(data.optionValue); }}
        >
          {skus.map(s => <Option key={s.id} value={s.id}>{s.name}</Option>)}
        </Dropdown>
        <Text
          size={200}
          style={{ cursor: 'pointer', color: tokens.colorBrandForeground1 }}
          onClick={() => openSkuDetail(selectedSku)}
        >
          {t('demand.viewSkuDetail')}
        </Text>
      </div>

      {loading ? <Spinner /> : (
        <Card className={styles.chartCard}>
          <CardHeader header={<Text weight="semibold">{t('demand.chartTitle')}</Text>} />
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis domain={[0, (max: number) => Math.ceil(max * 1.1)]} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="upper95" stroke="none" fill="#c8e6c9" fillOpacity={0.4} name={t('demand.ci95')} />
              <Area type="monotone" dataKey="upper80" stroke="none" fill="#81c784" fillOpacity={0.5} name={t('demand.ci80')} />
              <Area type="monotone" dataKey="forecast" stroke="#2e7d32" fill="#388e3c" fillOpacity={0.3} name={t('demand.pointForecast')} strokeWidth={2} />
              <Area type="monotone" dataKey="lower80" stroke="none" fill="#81c784" fillOpacity={0.5} />
              <Area type="monotone" dataKey="lower95" stroke="none" fill="#c8e6c9" fillOpacity={0.4} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}

      <div className={styles.statsRow}>
        <Card style={{ padding: '16px' }}>
          <Text weight="semibold">{t('demand.highConfidence')}</Text>
          <Text size={600} weight="bold">{forecasts.filter(f => f.confidence === 'high').length}</Text>
          <Text size={200}>{t('demand.periods')}</Text>
        </Card>
        <Card style={{ padding: '16px' }}>
          <Text weight="semibold">{t('demand.mediumConfidence')}</Text>
          <Text size={600} weight="bold">{forecasts.filter(f => f.confidence === 'medium').length}</Text>
          <Text size={200}>{t('demand.periods')}</Text>
        </Card>
        <Card style={{ padding: '16px' }}>
          <Text weight="semibold">{t('demand.avgForecast')}</Text>
          <Text size={600} weight="bold">
            {forecasts.length ? Math.round(forecasts.reduce((s, f) => s + f.point_forecast, 0) / forecasts.length) : 0}
          </Text>
          <Text size={200}>{t('demand.unitsWeek')}</Text>
        </Card>
      </div>
    </div>
  );
}
