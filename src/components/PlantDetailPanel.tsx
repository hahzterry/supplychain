import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Text, Badge, Spinner, Divider, ProgressBar,
} from '@fluentui/react-components';
import { getSessionHeader } from '../App';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '16px', paddingBottom: '24px' },
  header: { display: 'flex', flexDirection: 'column', gap: '4px' },
  badges: { display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '4px' },
  section: { display: 'flex', flexDirection: 'column', gap: '8px' },
  sectionTitle: { marginTop: '4px' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' },
  metricCard: { padding: '8px 12px', backgroundColor: tokens.colorNeutralBackground3, borderRadius: '6px' },
  metricLabel: { fontSize: '11px', color: tokens.colorNeutralForeground3 },
  metricValue: { fontSize: '14px', fontWeight: 600 },
  lineCard: { padding: '12px', backgroundColor: tokens.colorNeutralBackground3, borderRadius: '6px', display: 'flex', flexDirection: 'column', gap: '6px' },
  lineHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  maintenanceRow: { display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  runRow: { display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: '12px' },
});

interface LineDetail {
  line: Record<string, any>;
  maintenance_events: Array<Record<string, any>>;
  production_runs: Array<Record<string, any>>;
}

interface PlantDetail {
  plant_name: string;
  total_capacity_mt_per_day: number;
  avg_utilization_pct: number;
  line_count: number;
  lines: LineDetail[];
}

export default function PlantDetailPanel({ plantId }: { plantId: string }) {
  const styles = useStyles();
  const [data, setData] = useState<PlantDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [isLine, setIsLine] = useState(false);

  useEffect(() => {
    setLoading(true);
    // Try line endpoint first (PL01, PL02...), fallback to plant
    const endpoint = plantId.startsWith('PL') ? `/api/lines/${plantId}/detail` : `/api/plants/${plantId}/detail`;
    fetch(endpoint, { headers: getSessionHeader() })
      .then(r => { if (!r.ok) throw new Error('not found'); return r.json(); })
      .then(d => {
        if (d.line) {
          // Single line response — wrap into plant-like structure
          setIsLine(true);
          setData({
            plant_name: d.line.plant,
            total_capacity_mt_per_day: d.line.capacity_mt_per_day,
            avg_utilization_pct: d.line.current_utilization_pct,
            line_count: 1,
            lines: [{ line: d.line, maintenance_events: d.maintenance_events, production_runs: d.production_runs }],
          });
        } else {
          setData(d);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [plantId]);

  if (loading) return <Spinner label="Loading details..." />;
  if (!data) return <Text>Not found.</Text>;

  const utilColor = data.avg_utilization_pct >= 90 ? 'error' : data.avg_utilization_pct >= 75 ? 'warning' : 'success';

  return (
    <div className={styles.root}>
      {/* Header */}
      <div className={styles.header}>
        <Text size={400} weight="bold">{isLine && data.lines[0] ? data.lines[0].line.line_name : data.plant_name}</Text>
        {!isLine && <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>{data.line_count} production lines</Text>}
        <div className={styles.badges}>
          <Badge appearance="outline">Capacity: {data.total_capacity_mt_per_day} MT/day</Badge>
          <Badge color={utilColor as any}>Utilization: {data.avg_utilization_pct}%</Badge>
        </div>
      </div>

      <Divider />

      {/* Lines */}
      {data.lines.map(({ line, maintenance_events, production_runs }) => (
        <div key={line.id} className={styles.section}>
          <div className={styles.lineCard}>
            <div className={styles.lineHeader}>
              <Text weight="semibold" size={300}>{line.line_name}</Text>
              <Badge size="small" appearance="outline">{line.shift_pattern}</Badge>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ProgressBar value={line.current_utilization_pct / 100} color={line.current_utilization_pct >= 90 ? 'error' : line.current_utilization_pct >= 75 ? 'warning' : 'success'} style={{ flex: 1 }} />
              <Text size={200}>{line.current_utilization_pct}%</Text>
            </div>
            {line.current_sku && <Text size={200}>Current: {line.current_sku}</Text>}
            <div className={styles.badges}>
              {line.product_categories?.map((c: string) => (
                <Badge key={c} appearance="outline" size="small">{c}</Badge>
              ))}
            </div>
          </div>

          {/* Maintenance */}
          {maintenance_events.length > 0 && (
            <div className={styles.section}>
              <Text weight="semibold" size={200}>Maintenance History</Text>
              {maintenance_events.slice(-5).map((evt, i) => (
                <div key={i} className={styles.maintenanceRow}>
                  <div>
                    <Badge size="small" color={evt.type === 'breakdown' ? 'danger' : evt.type === 'unplanned' ? 'warning' : 'informative'}>
                      {evt.type}
                    </Badge>
                    <Text size={200} style={{ marginLeft: '6px' }}>{evt.root_cause}</Text>
                  </div>
                  <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                    <Text size={100}>{evt.date} | {evt.duration_hours}h | AED {evt.cost_aed?.toLocaleString()}</Text>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recent Production Runs */}
          {production_runs.length > 0 && (
            <div className={styles.section}>
              <Text weight="semibold" size={200}>Recent Production Runs</Text>
              {production_runs.slice(-5).map((run, i) => (
                <div key={i} className={styles.runRow}>
                  <Text size={200}>{run.date} | {run.sku_id} | {run.shift}</Text>
                  <Text size={200}>
                    {run.actual_qty}/{run.planned_qty} ({run.yield_pct}% yield)
                  </Text>
                </div>
              ))}
            </div>
          )}

          {data.lines.length > 1 && <Divider />}
        </div>
      ))}
    </div>
  );
}
