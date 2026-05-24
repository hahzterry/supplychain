import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Spinner, Badge,
  Table, TableHeader, TableRow, TableHeaderCell, TableBody, TableCell,
} from '@fluentui/react-components';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';

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

  if (loading) return <Spinner label="Loading..." />;

  const capacityData = lines.map(l => ({ name: l.line_name.replace('Line ', 'L'), utilization: l.current_utilization_pct }));

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('supply.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('supply.subtitle')}</Text>

      <div className={styles.grid}>
        <Card>
          <CardHeader header={<Text weight="semibold">{t('supply.suppliers')}</Text>} />
          <Table size="small">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>Supplier</TableHeaderCell>
                <TableHeaderCell>Country</TableHeaderCell>
                <TableHeaderCell>Lead Time</TableHeaderCell>
                <TableHeaderCell>Reliability</TableHeaderCell>
                <TableHeaderCell>Orders</TableHeaderCell>
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
