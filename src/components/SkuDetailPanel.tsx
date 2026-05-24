import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Text, Badge, Spinner, Card, Divider,
} from '@fluentui/react-components';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { getSessionHeader } from '../App';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';

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
  alertCard: { padding: '8px', borderLeft: `3px solid ${tokens.colorPaletteRedBorder2}`, backgroundColor: tokens.colorNeutralBackground3, borderRadius: '4px' },
  poRow: { display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: '12px' },
  altRow: { display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  qualityRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 0' },
  chartContainer: { width: '100%', height: 140 },
});

interface SkuDetail {
  sku: Record<string, any>;
  inventory: Record<string, any> | null;
  forecasts: Array<Record<string, any>>;
  alternatives: Array<Record<string, any>>;
  quality_results: Array<Record<string, any>>;
  alerts: Array<Record<string, any>>;
  purchase_orders: Array<Record<string, any>>;
  production_lines: Array<Record<string, any>>;
}

export default function SkuDetailPanel({ skuId }: { skuId: string }) {
  const styles = useStyles();
  const { openSupplierDetail } = useDetailDrawer();
  const [data, setData] = useState<SkuDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/skus/${skuId}/detail`, { headers: getSessionHeader() })
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [skuId]);

  if (loading) return <Spinner label="Loading SKU details..." />;
  if (!data) return <Text>SKU not found.</Text>;

  const { sku, inventory, forecasts, alternatives, quality_results, alerts, purchase_orders, production_lines } = data;

  const riskColor = (level: string) => {
    if (level === 'critical') return 'danger' as const;
    if (level === 'warning') return 'warning' as const;
    if (level === 'excess') return 'important' as const;
    return 'success' as const;
  };

  const chartData = forecasts.map(f => ({
    week: f.week?.replace('2026-', ''),
    forecast: Math.round(f.point_forecast),
    lower: Math.round(f.lower_80),
    upper: Math.round(f.upper_80),
  }));

  return (
    <div className={styles.root}>
      {/* Header */}
      <div className={styles.header}>
        <Text size={400} weight="bold">{sku.name}</Text>
        <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>{sku.id} — {sku.name_ar}</Text>
        <div className={styles.badges}>
          <Badge appearance="filled" color="brand">{sku.category}</Badge>
          <Badge appearance="outline">{sku.brand}</Badge>
          <Badge appearance="outline">ABC: {sku.abc_class}</Badge>
          <Badge appearance="outline">XYZ: {sku.xyz_class}</Badge>
          {sku.active ? <Badge color="success">Active</Badge> : <Badge color="danger">Inactive</Badge>}
        </div>
      </div>

      <Divider />

      {/* Inventory */}
      {inventory && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Inventory Position</Text>
          <div className={styles.grid}>
            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>Current Stock</div>
              <div className={styles.metricValue}>{inventory.current_stock?.toLocaleString()}</div>
            </div>
            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>Available</div>
              <div className={styles.metricValue}>{inventory.available_stock?.toLocaleString()}</div>
            </div>
            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>In Transit</div>
              <div className={styles.metricValue}>{inventory.in_transit?.toLocaleString()}</div>
            </div>
            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>Days of Supply</div>
              <div className={styles.metricValue}>{inventory.days_of_supply}</div>
            </div>
            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>Batch Age</div>
              <div className={styles.metricValue}>{inventory.batch_age_days} days</div>
            </div>
            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>Shelf Life</div>
              <div className={styles.metricValue}>{inventory.shelf_life_remaining_pct}%</div>
            </div>
          </div>
          <Badge color={riskColor(inventory.risk_level)} size="small">Risk: {inventory.risk_level}</Badge>
        </div>
      )}

      <Divider />

      {/* Forecast Chart */}
      {chartData.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>8-Week Forecast</Text>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <XAxis dataKey="week" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} width={40} />
                <Tooltip />
                <Area type="monotone" dataKey="upper" stroke="none" fill="#c2eeda" />
                <Area type="monotone" dataKey="lower" stroke="none" fill="#ffffff" />
                <Area type="monotone" dataKey="forecast" stroke="#2D915C" fill="#8AD6B2" fillOpacity={0.4} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <Divider />

      {/* Suppliers & Sourcing */}
      {alternatives.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Alternative Suppliers</Text>
          {alternatives.map((alt, i) => (
            <div key={i} className={styles.altRow}>
              <div>
                <Text size={200} weight="semibold" style={{ cursor: 'pointer', color: tokens.colorBrandForeground1 }}
                  onClick={() => openSupplierDetail(alt.supplier_id)}>
                  {alt.supplier_name}
                </Text>
                <Text size={100} style={{ display: 'block', color: tokens.colorNeutralForeground3 }}>{alt.notes}</Text>
              </div>
              <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                <Text size={100}>{alt.lead_time_days}d | {alt.unit_cost_premium_pct > 0 ? '+' : ''}{alt.unit_cost_premium_pct}%</Text>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Purchase Orders */}
      {purchase_orders.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Active Purchase Orders</Text>
          {purchase_orders.map(po => (
            <div key={po.id} className={styles.poRow}>
              <Text size={200}>{po.id} — {po.supplier_name}</Text>
              <div>
                <Badge size="small" appearance="outline">{po.status}</Badge>
                <Text size={200}> {po.qty} units</Text>
              </div>
            </div>
          ))}
        </div>
      )}

      <Divider />

      {/* Quality Results */}
      {quality_results.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Quality & Compliance</Text>
          {quality_results.slice(0, 4).map((q, i) => (
            <div key={i} className={styles.qualityRow}>
              <Text size={200}>{q.batch_id} ({q.test_date})</Text>
              <Badge size="small" color={q.overall_result === 'pass' ? 'success' : q.overall_result === 'hold' ? 'warning' : 'danger'}>
                {q.overall_result}
              </Badge>
            </div>
          ))}
        </div>
      )}

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Active Alerts</Text>
          {alerts.map(alert => (
            <div key={alert.id} className={styles.alertCard}>
              <Text size={200} weight="semibold">{alert.title}</Text>
              <Text size={200} style={{ display: 'block', color: tokens.colorNeutralForeground3 }}>{alert.description}</Text>
            </div>
          ))}
        </div>
      )}

      {/* Production */}
      {production_lines.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Production</Text>
          {production_lines.map(line => (
            <div key={line.id} className={styles.poRow}>
              <Text size={200}>{line.line_name} ({line.plant})</Text>
              <Text size={200}>{line.current_utilization_pct}% util</Text>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
