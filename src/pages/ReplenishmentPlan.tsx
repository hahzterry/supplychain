import { useEffect, useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Text, Badge, Button, Spinner,
  Dialog, DialogSurface, DialogTitle, DialogBody, DialogContent, DialogActions,
} from '@fluentui/react-components';
import { useI18n } from '../i18n';
import { getSessionHeader } from '../App';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '24px' },
  actionsList: { display: 'flex', flexDirection: 'column', gap: '12px' },
  actionCard: { padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' },
  actionHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  actionMeta: { display: 'flex', gap: '8px', flexWrap: 'wrap' },
  kpiImpact: { display: 'flex', gap: '12px', marginTop: '4px', flexWrap: 'wrap' },
  kpiChip: { padding: '2px 8px', borderRadius: '4px', backgroundColor: tokens.colorNeutralBackground3, fontSize: '12px' },
  buttons: { display: 'flex', gap: '8px', marginTop: '8px' },
  dialogDetail: { display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' },
  dialogRow: { display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  dialogKpis: { display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' },
  dialogKpiCard: { padding: '8px 12px', borderRadius: '6px', backgroundColor: tokens.colorNeutralBackground3, display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '80px' },
});

interface Action {
  id: string; action_type: string; sku_name: string; sku_id: string;
  recommended_qty: number; urgency: string; rationale: string;
  confidence: string; scenario: string; supplier_id?: string;
  plant?: string; kpi_impact: Record<string, string>;
}

export default function ReplenishmentPlan() {
  const styles = useStyles();
  const { t } = useI18n();
  const { openSkuDetail } = useDetailDrawer();
  const [actions, setActions] = useState<Action[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmAction, setConfirmAction] = useState<Action | null>(null);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    fetch('/api/replenishment/actions', { headers: getSessionHeader() })
      .then(r => r.json())
      .then(data => { setActions(data); setLoading(false); });
  }, []);

  const handleApprove = async (action: Action) => {
    setConfirmAction(action);
  };

  const handleConfirmApprove = async () => {
    if (!confirmAction) return;
    setApproving(true);
    await fetch(`/api/replenishment/actions/${confirmAction.id}/approve`, { method: 'POST', headers: getSessionHeader() });
    setActions(prev => prev.filter(a => a.id !== confirmAction.id));
    setApproving(false);
    setConfirmAction(null);
  };

  const handleDismiss = async (id: string) => {
    await fetch(`/api/replenishment/actions/${id}/dismiss`, { method: 'POST', headers: getSessionHeader() });
    setActions(prev => prev.filter(a => a.id !== id));
  };

  if (loading) return <Spinner label="Loading..." />;

  const urgencyColor = (u: string) => {
    if (u === 'critical') return 'danger' as const;
    if (u === 'high') return 'warning' as const;
    return 'informative' as const;
  };

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('replenishment.title')}</Text>
      <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>{t('replenishment.subtitle')}</Text>

      <div className={styles.actionsList}>
        {actions.map(action => (
          <Card key={action.id} className={styles.actionCard}>
            <div className={styles.actionHeader}>
              <Text weight="semibold" style={{ cursor: 'pointer', color: tokens.colorBrandForeground1 }} onClick={() => openSkuDetail(action.sku_id)}>
                {action.sku_name}
              </Text>
              <Badge color={urgencyColor(action.urgency)}>{action.urgency}</Badge>
            </div>
            <div className={styles.actionMeta}>
              <Badge appearance="outline" size="small">{action.action_type.replace('_', ' ')}</Badge>
              <Badge appearance="outline" size="small">Qty: {action.recommended_qty}</Badge>
              <Badge appearance="outline" size="small">Confidence: {action.confidence}</Badge>
              <Badge appearance="outline" size="small">Scenario: {action.scenario}</Badge>
            </div>
            <Text size={200}>{action.rationale}</Text>
            <div className={styles.kpiImpact}>
              {Object.entries(action.kpi_impact).map(([k, v]) => (
                <span key={k} className={styles.kpiChip}>{k.replace('_', ' ')}: {v}</span>
              ))}
            </div>
            <div className={styles.buttons}>
              <Button appearance="primary" size="small" onClick={() => handleApprove(action)}>
                {t('replenishment.approve')}
              </Button>
              <Button appearance="subtle" size="small" onClick={() => handleDismiss(action.id)}>
                {t('replenishment.dismiss')}
              </Button>
            </div>
          </Card>
        ))}
        {actions.length === 0 && <Text>All actions have been reviewed.</Text>}
      </div>

      <Dialog open={!!confirmAction} onOpenChange={(_, d) => { if (!d.open) setConfirmAction(null); }}>
        <DialogSurface>
          <DialogBody>
            <DialogTitle>Confirm Approval</DialogTitle>
            <DialogContent>
              {confirmAction && (
                <div className={styles.dialogDetail}>
                  <Text weight="semibold" size={400}>{confirmAction.sku_name}</Text>
                  <div className={styles.dialogRow}>
                    <Text size={200}>Action Type</Text>
                    <Text size={200} weight="semibold">{confirmAction.action_type.replace('_', ' ')}</Text>
                  </div>
                  <div className={styles.dialogRow}>
                    <Text size={200}>Recommended Quantity</Text>
                    <Text size={200} weight="semibold">{confirmAction.recommended_qty}</Text>
                  </div>
                  <div className={styles.dialogRow}>
                    <Text size={200}>Urgency</Text>
                    <Badge color={urgencyColor(confirmAction.urgency)} size="small">{confirmAction.urgency}</Badge>
                  </div>
                  <div className={styles.dialogRow}>
                    <Text size={200}>Confidence</Text>
                    <Text size={200} weight="semibold">{confirmAction.confidence}</Text>
                  </div>
                  <Text size={200} style={{ marginTop: '8px' }}>{confirmAction.rationale}</Text>
                  <Text size={200} weight="semibold" style={{ marginTop: '12px' }}>KPI Impact</Text>
                  <div className={styles.dialogKpis}>
                    {Object.entries(confirmAction.kpi_impact).map(([k, v]) => (
                      <div key={k} className={styles.dialogKpiCard}>
                        <Text size={100}>{k.replace('_', ' ')}</Text>
                        <Text size={200} weight="semibold" style={{ color: v.startsWith('+') ? tokens.colorPaletteGreenForeground1 : v.startsWith('-') ? tokens.colorPaletteRedForeground1 : undefined }}>
                          {v}
                        </Text>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </DialogContent>
            <DialogActions>
              <Button appearance="secondary" onClick={() => setConfirmAction(null)}>Cancel</Button>
              <Button appearance="primary" onClick={handleConfirmApprove} disabled={approving}>
                {approving ? 'Approving...' : 'Confirm Approval'}
              </Button>
            </DialogActions>
          </DialogBody>
        </DialogSurface>
      </Dialog>
    </div>
  );
}
