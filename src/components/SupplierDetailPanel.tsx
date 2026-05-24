import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Text, Badge, Spinner, Divider,
} from '@fluentui/react-components';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
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
  contactRow: { display: 'flex', justifyContent: 'space-between', padding: '4px 0' },
  poRow: { display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  certBadge: { display: 'inline-flex', padding: '4px 8px', borderRadius: '4px', backgroundColor: tokens.colorNeutralBackground3, marginRight: '6px', marginBottom: '6px' },
  chartContainer: { width: '100%', height: 160 },
});

interface SupplierDetail {
  supplier: Record<string, any>;
  contact: Record<string, any> | null;
  performance_history: Array<Record<string, any>>;
  certifications: Array<Record<string, any>>;
  purchase_orders: Array<Record<string, any>>;
}

export default function SupplierDetailPanel({ supplierId }: { supplierId: string }) {
  const styles = useStyles();
  const [data, setData] = useState<SupplierDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setData(null);
    fetch(`/api/suppliers/${encodeURIComponent(supplierId)}/detail`, { headers: getSessionHeader() })
      .then(r => { if (!r.ok) throw new Error('not found'); return r.json(); })
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [supplierId]);

  if (loading) return <Spinner label="Loading supplier details..." />;
  if (!data || !data.supplier) return <Text>Supplier not found.</Text>;

  const { supplier, contact, performance_history, certifications, purchase_orders } = data;

  const reliabilityColor = (supplier.reliability_score || 0) >= 90 ? 'success' : (supplier.reliability_score || 0) >= 80 ? 'warning' : 'danger';

  const perfChart = performance_history.map(p => ({
    month: p.month.replace('2026-', '').replace('2025-', ''),
    otd: p.on_time_delivery_pct,
    quality: p.quality_pass_rate,
  }));

  return (
    <div className={styles.root}>
      {/* Header */}
      <div className={styles.header}>
        <Text size={400} weight="bold">{supplier.name}</Text>
        <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>{supplier.name_ar} — {supplier.country}</Text>
        <div className={styles.badges}>
          <Badge color={reliabilityColor as any}>Reliability: {supplier.reliability_score}%</Badge>
          <Badge appearance="outline">Quality: {supplier.quality_score}</Badge>
          <Badge appearance="outline">{supplier.payment_terms}</Badge>
        </div>
      </div>

      <Divider />

      {/* Key Metrics */}
      <div className={styles.section}>
        <Text weight="semibold" className={styles.sectionTitle}>Performance</Text>
        <div className={styles.grid}>
          <div className={styles.metricCard}>
            <div className={styles.metricLabel}>Avg Lead Time</div>
            <div className={styles.metricValue}>{supplier.avg_lead_time_days} days</div>
          </div>
          <div className={styles.metricCard}>
            <div className={styles.metricLabel}>Lead Time Range</div>
            <div className={styles.metricValue}>{supplier.min_lead_time_days}–{supplier.max_lead_time_days}d</div>
          </div>
          <div className={styles.metricCard}>
            <div className={styles.metricLabel}>Active Orders</div>
            <div className={styles.metricValue}>{supplier.current_orders}</div>
          </div>
          <div className={styles.metricCard}>
            <div className={styles.metricLabel}>Total Capacity</div>
            <div className={styles.metricValue}>{(supplier.total_capacity_mt / 1000).toFixed(0)}K MT</div>
          </div>
        </div>
      </div>

      {/* Performance Chart */}
      {perfChart.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>6-Month Trend</Text>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={perfChart} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={tokens.colorNeutralStroke2} />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis domain={[60, 100]} tick={{ fontSize: 10 }} width={35} />
                <Tooltip />
                <Line type="monotone" dataKey="otd" name="On-Time Delivery %" stroke="#2D915C" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="quality" name="Quality Pass %" stroke="#3FA070" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <Divider />

      {/* Contact */}
      {contact && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Contact</Text>
          <div className={styles.contactRow}>
            <Text size={200}>{contact.name}</Text>
            <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>{contact.role}</Text>
          </div>
          <Text size={200}>{contact.email}</Text>
          <Text size={200}>{contact.phone}</Text>
        </div>
      )}

      {/* Materials */}
      <div className={styles.section}>
        <Text weight="semibold" className={styles.sectionTitle}>Materials</Text>
        <div className={styles.badges}>
          {supplier.material_types?.map((m: string) => (
            <Badge key={m} appearance="outline" size="small">{m}</Badge>
          ))}
        </div>
      </div>

      <Divider />

      {/* Certifications */}
      {certifications.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Certifications</Text>
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {certifications.map((cert, i) => (
              <span key={i} className={styles.certBadge}>
                <Text size={200}>
                  {cert.name}
                  {cert.status === 'expiring' && ' ⚠️'}
                  {cert.status === 'expired' && ' ❌'}
                </Text>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Purchase Orders */}
      {purchase_orders.length > 0 && (
        <div className={styles.section}>
          <Text weight="semibold" className={styles.sectionTitle}>Active Orders</Text>
          {purchase_orders.map(po => (
            <div key={po.id} className={styles.poRow}>
              <div>
                <Text size={200} weight="semibold">{po.id}</Text>
                <Text size={200} style={{ display: 'block' }}>{po.sku_name} — {po.qty} units</Text>
              </div>
              <div style={{ textAlign: 'right' }}>
                <Badge size="small" color={po.status === 'delayed' ? 'danger' : po.status === 'in_transit' ? 'warning' : 'informative'}>
                  {po.status}
                </Badge>
                <Text size={100} style={{ display: 'block' }}>Due: {po.expected_delivery}</Text>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
