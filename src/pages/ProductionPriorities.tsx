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

interface Line {
  id: string; plant: string; line_name: string;
  product_categories: string[]; capacity_units_per_day: number;
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

  if (loading) return <Spinner label={t('common.loading')} />;

  const chartData = lines.map(l => ({
    name: l.line_name,
    utilization: l.current_utilization_pct,
    capacity: l.capacity_units_per_day,
  }));

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('production.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('production.subtitle')}</Text>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {[
          { label: t('production.chip.schedule'), message: 'Show this week\'s production schedule and priorities' },
          { label: t('production.chip.utilization'), message: 'Analyze production line utilization and idle capacity' },
          { label: t('production.chip.bottleneck'), message: 'Which production lines are capacity constrained?' },
          { label: t('production.chip.aog'), message: 'List current AOG and priority production orders' },
        ].map((s, i) => (
          <button key={i} onClick={() => setPendingChatMessage(s.message)} style={{
            borderRadius: 18, border: '1px solid #e0d4b0', background: '#fdf8ee',
            padding: '6px 14px', fontSize: 12, color: '#8B6914', cursor: 'pointer',
          }}>{s.label}</button>
        ))}
      </div>

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
              <TableHeaderCell>{t('common.line')}</TableHeaderCell>
              <TableHeaderCell>{t('common.plant')}</TableHeaderCell>
              <TableHeaderCell>{t('common.capacity')}</TableHeaderCell>
              <TableHeaderCell>{t('common.utilization')}</TableHeaderCell>
              <TableHeaderCell>{t('common.currentSku')}</TableHeaderCell>
              <TableHeaderCell>{t('common.shifts')}</TableHeaderCell>
              <TableHeaderCell>{t('common.maintenance')}</TableHeaderCell>
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
                <TableCell>{l.capacity_units_per_day}</TableCell>
                <TableCell>
                  <Badge color={l.current_utilization_pct > 85 ? 'danger' : l.current_utilization_pct > 70 ? 'warning' : 'success'}>
                    {l.current_utilization_pct}%
                  </Badge>
                </TableCell>
                <TableCell>{l.current_sku || '—'}</TableCell>
                <TableCell>{l.shift_pattern}</TableCell>
                <TableCell>{l.planned_maintenance.length > 0 ? l.planned_maintenance.join(', ') : t('common.none')}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
