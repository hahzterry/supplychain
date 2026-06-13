import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Spinner, Badge,
  Table, TableHeader, TableRow, TableHeaderCell, TableBody, TableCell,
} from '@fluentui/react-components';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';
import { setPendingChatMessage } from '../components/CopilotActions';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '24px' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' },
});

interface SupplierData {
  id: string; name: string; country: string;
  avg_lead_time_days: number; reliability_score: number;
  quality_score: number; current_orders: number;
}

interface LineData {
  id: string; line_name: string; plant: string; current_utilization_pct: number;
}

export default function SupplyNetwork() {
  const styles = useStyles();
  const { t } = useI18n();
  const { openSupplierDetail, openLineDetail } = useDetailDrawer();
  const [suppliers, setSuppliers] = useState<SupplierData[]>([]);
  const [lines, setLines] = useState<LineData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const headers = getSessionHeader();
    Promise.all([
      fetch('/api/suppliers', { headers }).then(r => r.json()),
      fetch('/api/production/schedule', { headers }).then(r => r.json()),
    ]).then(([s, l]) => {
      setSuppliers(s);
      setLines(l);
      setLoading(false);
    });
  }, []);

  if (loading) return <Spinner label={t('common.loading')} />;

  const capacityData = lines.map(l => ({ name: l.line_name.replace('Line ', 'L'), utilization: l.current_utilization_pct }));

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('supply.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('supply.subtitle')}</Text>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {[
          { label: t('supply.chip.reliability'), message: 'Which suppliers have reliability below 90% this quarter?' },
          { label: t('supply.chip.leadTime'), message: 'Identify suppliers with increasing lead times' },
          { label: t('supply.chip.singleSource'), message: 'Which critical parts have single-source suppliers?' },
          { label: t('supply.chip.capacity'), message: 'Show current capacity utilization and bottlenecks' },
        ].map((s, i) => (
          <button key={i} onClick={() => setPendingChatMessage(s.message)} style={{
            borderRadius: 18, border: '1px solid #e0d4b0', background: '#fdf8ee',
            padding: '6px 14px', fontSize: 12, color: '#8B6914', cursor: 'pointer',
          }}>{s.label}</button>
        ))}
      </div>

      <div className={styles.grid}>
        <Card>
          <CardHeader header={<Text weight="semibold">{t('supply.suppliers')}</Text>} />
          <Table size="small">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>{t('common.supplier')}</TableHeaderCell>
                <TableHeaderCell>{t('common.country')}</TableHeaderCell>
                <TableHeaderCell>{t('common.leadTime')}</TableHeaderCell>
                <TableHeaderCell>{t('common.reliability')}</TableHeaderCell>
                <TableHeaderCell>{t('common.orders')}</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {suppliers.map(s => (
                <TableRow key={s.id}>
                  <TableCell>
                    <Text style={{ cursor: 'pointer', color: tokens.colorBrandForeground1 }} onClick={() => openSupplierDetail(s.id)}>
                      {s.name}
                    </Text>
                  </TableCell>
                  <TableCell>{s.country}</TableCell>
                  <TableCell>{s.avg_lead_time_days}d</TableCell>
                  <TableCell>
                    <Badge color={s.reliability_score >= 90 ? 'success' : s.reliability_score >= 80 ? 'warning' : 'danger'} size="small">
                      {s.reliability_score}%
                    </Badge>
                  </TableCell>
                  <TableCell>{s.current_orders}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>

        <Card>
          <CardHeader header={<Text weight="semibold">{t('supply.capacity')}</Text>} />
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={capacityData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} unit="%" />
              <YAxis type="category" dataKey="name" width={120} />
              <Tooltip />
              <Bar dataKey="utilization" fill="#2e7d32" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
