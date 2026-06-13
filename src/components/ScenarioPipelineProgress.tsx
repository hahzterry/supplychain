import { useEffect, useRef, useState } from 'react';
import { useI18n, type Lang } from '../i18n';
import { getSessionHeader } from '../App';

const STEPS = [
  { key: 'demand_analysis', en: 'Demand Analyzer', fr: 'Analyseur de demande', es: 'Analizador de demanda' },
  { key: 'inventory_simulation', en: 'Inventory Simulator', fr: 'Simulateur d\'inventaire', es: 'Simulador de inventario' },
  { key: 'supply_evaluation', en: 'Supply Evaluator', fr: 'Évaluateur d\'approvisionnement', es: 'Evaluador de suministro' },
  { key: 'production_check', en: 'Production Checker', fr: 'Vérificateur de production', es: 'Verificador de producción' },
  { key: 'kpi_projection', en: 'KPI Projector', fr: 'Projecteur d\'indicateurs', es: 'Proyector de indicadores' },
  { key: 'analysis', en: 'Risk Analyst', fr: 'Analyste de risque', es: 'Analista de riesgo' },
];

interface Props {
  isComplete?: boolean;
  onResult?: (result: any) => void;
}

export function ScenarioPipelineProgress({ isComplete, onResult }: Props) {
  const { lang } = useI18n();
  const [stepProgress, setStepProgress] = useState<Record<string, string>>({});
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (isComplete) {
      if (pollRef.current) clearInterval(pollRef.current);
      const allDone: Record<string, string> = {};
      STEPS.forEach(s => { allDone[s.key] = 'done'; });
      setStepProgress(allDone);
      return;
    }

    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch('/api/reports/latest', { headers: getSessionHeader() });
        const data = await res.json();
        const r = data?.result;
        if (!r) return;

        if (r.scenario_progress?.step) {
          setStepProgress(prev => ({ ...prev, [r.scenario_progress.step]: r.scenario_progress.status }));
        }

        if (r.pending_scenario) {
          if (pollRef.current) clearInterval(pollRef.current);
          const allDone: Record<string, string> = {};
          STEPS.forEach(s => { allDone[s.key] = 'done'; });
          setStepProgress(allDone);
          onResult?.(r.pending_scenario);
        }
      } catch {}
    }, 1000);

    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [isComplete, onResult]);

  const allDone = STEPS.every(s => stepProgress[s.key] === 'done');

  return (
    <div style={{
      border: '1px solid #e0e0e0',
      borderRadius: 10,
      padding: '14px 18px',
      background: '#fafbfc',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <span style={{ fontSize: 16 }}>🔬</span>
        <span style={{ fontWeight: 600, fontSize: 14, color: '#1565c0' }}>
          {lang === 'fr' ? 'Pipeline d\'analyse de scénario' : lang === 'es' ? 'Pipeline de análisis de escenario' : 'Scenario Analysis Pipeline'}
        </span>
        {!allDone && (
          <span style={{ marginLeft: 'auto', fontSize: 11, color: '#666' }}>
            {lang === 'fr' ? 'Agents en cours...' : lang === 'es' ? 'Agentes en ejecución...' : 'Running agents...'}
          </span>
        )}
        {allDone && (
          <span style={{ marginLeft: 'auto', fontSize: 11, color: '#2e7d32', fontWeight: 600 }}>
            {lang === 'fr' ? 'Terminé' : lang === 'es' ? 'Completado' : 'Complete'}
          </span>
        )}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        {STEPS.map((step, idx) => {
          const status = stepProgress[step.key];
          const isDone = status === 'done';
          const isRunning = status === 'running';
          return (
            <div key={step.key} style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '6px 12px',
              borderRadius: 6,
              background: isDone ? '#e8f5e9' : isRunning ? '#e3f2fd' : '#f5f5f5',
              transition: 'all 0.3s ease',
            }}>
              <span style={{ fontSize: 13, minWidth: 18, textAlign: 'center' }}>
                {isDone ? '✓' : isRunning ? '⏳' : '○'}
              </span>
              <span style={{ fontSize: 11, color: '#888', minWidth: 16 }}>{idx + 1}.</span>
              <span style={{
                fontSize: 12,
                fontWeight: isDone || isRunning ? 600 : 400,
                color: isDone ? '#2e7d32' : isRunning ? '#1565c0' : '#999',
              }}>
                {step[lang]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
