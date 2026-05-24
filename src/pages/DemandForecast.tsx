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
  const [selectedSku, setSelectedSku] = useState('FL001');
  const [skus, setSkus] = useState<Array<{ id: string; name: string }>>([]);
  const [loading, setLoading] = useState(true);
  const pendingCheckRef = useRef(false);

  useEffect(() => {
    const headers = getSessionHeader();
    fetch('/api/skus', { headers }).then(r => r.json()).then(data => {
      setSkus(data.map((s: { id: string; name: string }) => ({ id: s.id, name: s.name })));
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
          View SKU Detail
        </Text>
      </div>

      {loading ? <Spinner /> : (
        <Card className={styles.chartCard}>
          <CardHeader header={<Text weight="semibold">8-Week Forecast with Confidence Bands</Text>} />
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="upper95" stackId="1" stroke="none" fill="#c8e6c9" name="95% CI" />
              <Area type="monotone" dataKey="upper80" stackId="2" stroke="none" fill="#81c784" name="80% CI" />
              <Area type="monotone" dataKey="forecast" stroke="#2e7d32" fill="#388e3c" fillOpacity={0.3} name="Point Forecast" strokeWidth={2} />
              <Area type="monotone" dataKey="lower80" stackId="3" stroke="none" fill="#81c784" />
              <Area type="monotone" dataKey="lower95" stackId="4" stroke="none" fill="#c8e6c9" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}

      <div className={styles.statsRow}>
        <Card style={{ padding: '16px' }}>
          <Text weight="semibold">High Confidence</Text>
          <Text size={600} weight="bold">{forecasts.filter(f => f.confidence === 'high').length}</Text>
          <Text size={200}>periods</Text>
        </Card>
        <Card style={{ padding: '16px' }}>
          <Text weight="semibold">Medium Confidence</Text>
          <Text size={600} weight="bold">{forecasts.filter(f => f.confidence === 'medium').length}</Text>
          <Text size={200}>periods</Text>
        </Card>
        <Card style={{ padding: '16px' }}>
          <Text weight="semibold">Avg Forecast</Text>
          <Text size={600} weight="bold">
            {forecasts.length ? Math.round(forecasts.reduce((s, f) => s + f.point_forecast, 0) / forecasts.length) : 0}
          </Text>
          <Text size={200}>units/week</Text>
        </Card>
      </div>
    </div>
  );
}
