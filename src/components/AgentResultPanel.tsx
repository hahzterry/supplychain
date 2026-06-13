import { useAgentResult, type ExecutivePresentation } from '../contexts/AgentResultContext';
import { useI18n } from '../i18n';

const statusColors: Record<string, { bg: string; text: string }> = {
  green: { bg: '#e8f5e9', text: '#2e7d32' },
  amber: { bg: '#fff8e1', text: '#f57c00' },
  red: { bg: '#ffebee', text: '#c62828' },
  blue: { bg: '#e3f2fd', text: '#1565c0' },
};

const priorityDots: Record<string, string> = {
  high: '#d32f2f',
  medium: '#f57c00',
  low: '#388e3c',
};

function ExecutiveView({ presentation }: { presentation: ExecutivePresentation }) {
  const { t } = useI18n();
  const { headline, status, metrics, table, actions, narrative } = presentation;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Headline + Status */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, color: '#1a1a1a', margin: 0 }}>{headline}</h3>
        {status && (
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 4,
            borderRadius: 12, padding: '3px 10px', fontSize: 11, fontWeight: 500,
            background: statusColors[status.color]?.bg || '#f5f5f5',
            color: statusColors[status.color]?.text || '#666',
          }}>
            {status.color === 'green' ? '✓' : status.color === 'red' ? '✕' : status.color === 'amber' ? '⚠' : 'ℹ'}
            {' '}{status.label}
          </span>
        )}
      </div>

      {/* Metrics Grid */}
      {metrics && metrics.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
          {metrics.map((m, i) => (
            <div key={i} style={{
              borderRadius: 8, border: '1px solid #e8e8e8', background: '#fff', padding: '10px 12px',
            }}>
              <div style={{ fontSize: 11, color: '#888', marginBottom: 2 }}>{m.label}</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#1a1a1a' }}>{m.value}</div>
              {m.trend && (
                <div style={{ fontSize: 11, color: m.trendUp ? '#2e7d32' : '#c62828', marginTop: 2 }}>
                  {m.trendUp ? '↑' : '↓'} {m.trend}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Data Table */}
      {table && table.rows && table.rows.length > 0 && (
        <div style={{ borderRadius: 8, border: '1px solid #e8e8e8', overflow: 'hidden' }}>
          <div style={{ background: '#f9f9f9', padding: '6px 12px', fontSize: 11, fontWeight: 600, color: '#666' }}>
            {table.title}
          </div>
          <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #e8e8e8', background: '#f9f9f9' }}>
                {table.headers.map((h, i) => (
                  <th key={i} style={{ padding: '6px 12px', textAlign: 'left', fontWeight: 600, color: '#555' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row, i) => (
                <tr key={i} style={{ borderBottom: i < table.rows.length - 1 ? '1px solid #f0f0f0' : 'none' }}>
                  {row.map((cell, j) => (
                    <td key={j} style={{ padding: '6px 12px', color: '#333' }}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Recommended Actions */}
      {actions && actions.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {t('agentResult.recommendedActions')}
          </div>
          {actions.map((a, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <span style={{
                width: 8, height: 8, borderRadius: '50%', flexShrink: 0, marginTop: 5,
                background: priorityDots[a.priority] || '#888',
              }} />
              <span style={{ fontSize: 13, color: '#333' }}>{a.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* Narrative */}
      {narrative && (
        <p style={{ fontSize: 13, color: '#555', lineHeight: 1.6, margin: 0 }}>{narrative}</p>
      )}
    </div>
  );
}

export function AgentResultPanel() {
  const { t } = useI18n();
  const { presentation, showResult, dismiss } = useAgentResult();

  if (!showResult || !presentation) return null;

  return (
    <div style={{
      margin: '0 0 20px 0',
      borderRadius: 10,
      border: '1px solid #e0d4b0',
      background: '#fffdf8',
      padding: 16,
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <span style={{ fontSize: 10, fontWeight: 600, color: '#B8860B', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
          {t('agentResult.title')}
        </span>
        <button
          onClick={dismiss}
          style={{
            border: 'none', background: 'transparent', cursor: 'pointer',
            fontSize: 16, color: '#999', padding: '2px 6px', borderRadius: 4,
          }}
          title={t('agentResult.dismiss')}
        >
          ✕
        </button>
      </div>
      <ExecutiveView presentation={presentation} />
    </div>
  );
}
