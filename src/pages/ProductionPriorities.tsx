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

interface Line {
  id: string; plant: string; line_name: string;
  product_categories: string[]; capacity_mt_per_day: number;
  current_utilization_pct: number; current_sku: string | null;
  shift_pattern: string; planned_maintenance: string[];
}

export default function ProductionPriorities() {
  const styles = useStyles();
  const { t } = useI18n();
  const { openLineDetail } = useDetailDrawer();
  const [lines, setLines] = useState<Line[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/production/schedule', { headers: getSessionHeader() })
      .then(r => r.json())
      .then(data => { setLines(data); setLoading(false); });
  }, []);

  if (loading) return <Spinner label="Loading..." />;

  const chartData = lines.map(l => ({
    name: l.line_name,
    utilization: l.current_utilization_pct,
    capacity: l.capacity_mt_per_day,
  }));

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('production.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('production.subtitle')}</Text>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('production.utilization')}</Text>} />
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-15} textAnchor="end" height={60} />
            <YAxis domain={[0, 100]} unit="%" />
            <Tooltip />
            <Bar dataKey="utilization" fill="#2e7d32" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('production.schedule')}</Text>} />
        <Table size="small">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>Line</TableHeaderCell>
              <TableHeaderCell>Plant</TableHeaderCell>
              <TableHeaderCell>Capacity (MT/day)</TableHeaderCell>
              <TableHeaderCell>Utilization</TableHeaderCell>
              <TableHeaderCell>Current SKU</TableHeaderCell>
              <TableHeaderCell>Shifts</TableHeaderCell>
              <TableHeaderCell>Maintenance</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {lines.map(l => (
              <TableRow key={l.id}>
                <TableCell>
                  <Text style={{ cursor: 'pointer', color: tokens.colorBrandForeground1 }} onClick={() => openLineDetail(l.id)}>
                    {l.line_name}
                  </Text>
                </TableCell>
                <TableCell>{l.plant}</TableCell>
                <TableCell>{l.capacity_mt_per_day}</TableCell>
                <TableCell>
                  <Badge color={l.current_utilization_pct > 85 ? 'danger' : l.current_utilization_pct > 70 ? 'warning' : 'success'}>
                    {l.current_utilization_pct}%
                  </Badge>
                </TableCell>
                <TableCell>{l.current_sku || '—'}</TableCell>
                <TableCell>{l.shift_pattern}</TableCell>
                <TableCell>{l.planned_maintenance.length > 0 ? l.planned_maintenance.join(', ') : 'None'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
