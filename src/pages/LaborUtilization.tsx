import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Spinner,
  Select, Option,
} from '@fluentui/react-components';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { setPendingChatMessage } from '../components/CopilotActions';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '24px' },
  kpiRow: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' },
  kpiCard: { padding: '16px' },
  kpiValue: { fontSize: '28px', fontWeight: tokens.fontWeightBold },
  kpiLabel: { color: tokens.colorNeutralForeground3, fontSize: '13px' },
  filters: { display: 'flex', gap: '16px', alignItems: 'center' },
  tableWrap: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '13px' },
  th: { textAlign: 'left', padding: '8px 12px', borderBottom: `2px solid ${tokens.colorNeutralStroke1}`, fontWeight: tokens.fontWeightSemibold },
  td: { padding: '8px 12px', borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
});

interface LaborRecord {
  id: string;
  facility: string;
  date: string;
  shift: string;
  headcount: number;
  direct_hours: number;
  indirect_hours: number;
  overtime_hours: number;
  efficiency_pct: number;
  skill_category: string;
  production_line_id: string | null;
}

export default function LaborUtilization() {
  const styles = useStyles();
  const { t } = useI18n();
  const [records, setRecords] = useState<LaborRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [facilityFilter, setFacilityFilter] = useState('');

  useEffect(() => {
    const headers = getSessionHeader();
    fetch(`/api/labor?days=14&facility=${facilityFilter}`, { headers })
      .then(r => r.json())
      .then(data => { setRecords(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [facilityFilter]);

  if (loading) return <Spinner label={t('common.loading')} />;

  const avgEfficiency = records.length
    ? (records.reduce((sum, r) => sum + r.efficiency_pct, 0) / records.length).toFixed(1)
    : '0';
  const totalHeadcount = records.reduce((sum, r) => sum + r.headcount, 0);
  const totalOvertime = records.reduce((sum, r) => sum + r.overtime_hours, 0).toFixed(0);
  const totalDirect = records.reduce((sum, r) => sum + r.direct_hours, 0);
  const totalIndirect = records.reduce((sum, r) => sum + r.indirect_hours, 0);
  const utilization = totalDirect + totalIndirect > 0
    ? ((totalDirect / (totalDirect + totalIndirect)) * 100).toFixed(1)
    : '0';

  const facilityMap: Record<string, { efficiency: number; count: number }> = {};
  for (const r of records) {
    if (!facilityMap[r.facility]) facilityMap[r.facility] = { efficiency: 0, count: 0 };
    facilityMap[r.facility].efficiency += r.efficiency_pct;
    facilityMap[r.facility].count += 1;
  }
  const chartData = Object.entries(facilityMap).map(([name, v]) => ({
    name: name.split(',')[0],
    efficiency: parseFloat((v.efficiency / v.count).toFixed(1)),
  }));

  const facilities = [...new Set(records.map(r => r.facility))];

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('labor.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('labor.subtitle')}</Text>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {[
          { label: t('labor.chip.efficiency'), message: 'Analyze labor efficiency trends across all facilities' },
          { label: t('labor.chip.overtime'), message: 'Show overtime patterns and cost impact this month' },
          { label: t('labor.chip.skills'), message: 'Identify facilities with skill allocation gaps' },
          { label: t('labor.chip.shift'), message: 'Recommend shift pattern optimizations for peak demand' },
        ].map((s, i) => (
          <button key={i} onClick={() => setPendingChatMessage(s.message)} style={{
            borderRadius: 18, border: '1px solid #e0d4b0', background: '#fdf8ee',
            padding: '6px 14px', fontSize: 12, color: '#8B6914', cursor: 'pointer',
          }}>{s.label}</button>
        ))}
      </div>

      <div className={styles.kpiRow}>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{avgEfficiency}%</Text>
          <Text className={styles.kpiLabel}>{t('labor.avgEfficiency')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{utilization}%</Text>
          <Text className={styles.kpiLabel}>{t('labor.directLabor')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{totalHeadcount.toLocaleString()}</Text>
          <Text className={styles.kpiLabel}>{t('labor.totalHeadcount')}</Text>
        </Card>
        <Card className={styles.kpiCard}>
          <Text className={styles.kpiValue}>{Number(totalOvertime).toLocaleString()}h</Text>
          <Text className={styles.kpiLabel}>{t('labor.totalOvertime')}</Text>
        </Card>
      </div>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('labor.efficiencyByFacility')}</Text>} />
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData} margin={{ left: 10, right: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" fontSize={12} />
            <YAxis domain={[70, 100]} fontSize={12} />
            <Tooltip />
            <Legend />
            <Bar dataKey="efficiency" fill="#001F3F" name={t('labor.efficiencyPct')} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('labor.dailyRecords')}</Text>} />
        <div className={styles.filters}>
          <Select value={facilityFilter} onChange={(_, d) => setFacilityFilter(d.value)}>
            <Option value="">{t('common.allFacilities')}</Option>
            {facilities.map(f => <Option key={f} value={f}>{f}</Option>)}
          </Select>
        </div>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.th}>{t('common.date')}</th>
                <th className={styles.th}>{t('common.facility')}</th>
                <th className={styles.th}>{t('labor.shift')}</th>
                <th className={styles.th}>{t('labor.headcount')}</th>
                <th className={styles.th}>{t('labor.directHrs')}</th>
                <th className={styles.th}>{t('labor.indirectHrs')}</th>
                <th className={styles.th}>{t('labor.otHrs')}</th>
                <th className={styles.th}>{t('labor.efficiency')}</th>
                <th className={styles.th}>{t('labor.skill')}</th>
              </tr>
            </thead>
            <tbody>
              {records.slice(0, 50).map(r => (
                <tr key={r.id}>
                  <td className={styles.td}>{r.date}</td>
                  <td className={styles.td}>{r.facility.split(',')[0]}</td>
                  <td className={styles.td}>{r.shift}</td>
                  <td className={styles.td}>{r.headcount}</td>
                  <td className={styles.td}>{r.direct_hours}</td>
                  <td className={styles.td}>{r.indirect_hours}</td>
                  <td className={styles.td}>{r.overtime_hours}</td>
                  <td className={styles.td}>{r.efficiency_pct}%</td>
                  <td className={styles.td}>{r.skill_category}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
