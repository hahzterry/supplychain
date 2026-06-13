import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Badge, Spinner,
  Table, TableHeader, TableRow, TableHeaderCell, TableBody, TableCell,
} from '@fluentui/react-components';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';
import { setPendingChatMessage } from '../components/CopilotActions';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '24px' },
  topRow: { display: 'grid', gridTemplateColumns: '300px 1fr', gap: '16px' },
  riskCard: { padding: '16px' },
  riskStats: { display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' },
  riskItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
});

const RISK_COLORS: Record<string, string> = {
  critical: '#d32f2f', warning: '#f57c00', normal: '#388e3c', excess: '#1565c0',
};

interface Position {
  sku_id: string;
  sku_name: string;
  category: string;
  warehouse: string;
  current_stock: number;
  available_stock: number;
  days_of_supply: number;
  risk_level: string;
  cert_expiry_remaining_pct: number;
}

export default function InventoryHealth() {
  const styles = useStyles();
  const { t } = useI18n();
  const { openSkuDetail } = useDetailDrawer();
  const [positions, setPositions] = useState<Position[]>([]);
  const [riskMatrix, setRiskMatrix] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const headers = getSessionHeader();
    Promise.all([
      fetch('/api/inventory', { headers }).then(r => r.json()),
      fetch('/api/inventory/risk-matrix', { headers }).then(r => r.json()),
    ]).then(([pos, risk]) => {
      setPositions(pos);
      setRiskMatrix(risk);
      setLoading(false);
    });
  }, []);

  if (loading) return <Spinner label={t('common.loading')} />;

  const riskData = Object.entries(riskMatrix).map(([name, value]) => ({ name, value }));

  const severityColor = (risk: string) => {
    if (risk === 'critical') return 'danger';
    if (risk === 'warning') return 'warning';
    if (risk === 'excess') return 'informative';
    return 'success';
  };

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('inventory.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('inventory.subtitle')}</Text>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {[
          { label: t('inventory.chip.stockout'), message: 'Which SKUs are at risk of stockout in the next 2 weeks?' },
          { label: t('inventory.chip.overstock'), message: 'Identify overstocked items with more than 90 days of supply' },
          { label: t('inventory.chip.aging'), message: 'Review inventory aging for critical MRO parts' },
          { label: t('inventory.chip.dos'), message: 'Show days-of-supply breakdown by aircraft program' },
        ].map((s, i) => (
          <button key={i} onClick={() => setPendingChatMessage(s.message)} style={{
            borderRadius: 18, border: '1px solid #e0d4b0', background: '#fdf8ee',
            padding: '6px 14px', fontSize: 12, color: '#8B6914', cursor: 'pointer',
          }}>{s.label}</button>
        ))}
      </div>

      <div className={styles.topRow}>
        <Card className={styles.riskCard}>
          <CardHeader header={<Text weight="semibold">{t('inventory.riskMatrix')}</Text>} />
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65} label>
                {riskData.map(entry => (
                  <Cell key={entry.name} fill={RISK_COLORS[entry.name] || '#999'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className={styles.riskStats}>
            {riskData.map(r => (
              <div key={r.name} className={styles.riskItem}>
                <Text size={200} style={{ textTransform: 'capitalize' }}>{r.name}</Text>
                <Badge appearance="filled" color={severityColor(r.name)}>{r.value} {t('common.skus')}</Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <CardHeader header={<Text weight="semibold">{t('inventory.positions')}</Text>} />
          <div style={{ maxHeight: '400px', overflow: 'auto' }}>
            <Table size="small">
              <TableHeader>
                <TableRow>
                  <TableHeaderCell>{t('common.sku')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.category')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.dos')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.stock')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.risk')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.shelfLife')}</TableHeaderCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {positions.sort((a, b) => a.days_of_supply - b.days_of_supply).map(p => (
                  <TableRow key={p.sku_id}>
                    <TableCell>
                      <Text style={{ cursor: 'pointer', color: tokens.colorBrandForeground1 }} onClick={() => openSkuDetail(p.sku_id)}>
                        {p.sku_name}
                      </Text>
                    </TableCell>
                    <TableCell>{p.category}</TableCell>
                    <TableCell><Text weight="semibold">{p.days_of_supply}</Text></TableCell>
                    <TableCell>{p.current_stock.toLocaleString()}</TableCell>
                    <TableCell><Badge color={severityColor(p.risk_level)} size="small">{p.risk_level}</Badge></TableCell>
                    <TableCell>{p.cert_expiry_remaining_pct}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      </div>
    </div>
  );
}
