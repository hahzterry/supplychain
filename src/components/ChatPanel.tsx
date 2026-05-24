import { useEffect, useRef, useCallback } from 'react';
import { CopilotChat, AssistantMessage as DefaultAssistantMessage } from '@copilotkit/react-ui';
import { useRenderToolCall } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import '../copilotkit-overrides.css';
import { useI18n, type Lang } from '../i18n';
import { SEND_CHAT_MESSAGE_EVENT, consumePendingChatMessage, TOOL_COMPLETE_EVENT, TOOL_START_EVENT } from './CopilotActions';
import { ScenarioPipelineProgress } from './ScenarioPipelineProgress';

const CITATION_RE = /citeturn\d+\w*\d*/g;

function CleanAssistantMessage(props: any) {
  if (props.message?.content) {
    const cleaned = { ...props.message, content: props.message.content.replace(CITATION_RE, '') };
    return <DefaultAssistantMessage {...props} message={cleaned} />;
  }
  return <DefaultAssistantMessage {...props} />;
}

function RashidSuggestions({ suggestions, onSuggestionClick, isLoading }: any) {
  if (!suggestions?.length || isLoading) return null;
  return (
    <div className="rashid-suggestions">
      {suggestions.map((s: any, i: number) => (
        <button
          key={i}
          className="rashid-suggestion-chip"
          onClick={() => onSuggestionClick(s.message)}
        >
          {s.title}
        </button>
      ))}
    </div>
  );
}

interface AgentTool {
  name: string;
  description: string;
  agent: Record<Lang, string>;
  label: Record<Lang, string>;
  color: { bg: string; accent: string };
}

const TOOLS: AgentTool[] = [
  {
    name: 'demand_sensing_agent',
    description: 'Delegate to Demand Sensing Specialist',
    agent: { en: 'Demand Sensing', ar: 'استشعار الطلب' },
    label: { en: 'Analyzing demand patterns & forecasts...', ar: 'جارٍ تحليل أنماط الطلب والتوقعات...' },
    color: { bg: '#eef3ff', accent: '#3b6dd6' },
  },
  {
    name: 'inventory_risk_agent',
    description: 'Delegate to Inventory Risk Specialist',
    agent: { en: 'Inventory Risk', ar: 'مخاطر المخزون' },
    label: { en: 'Evaluating stock positions & risk levels...', ar: 'جارٍ تقييم مستويات المخزون والمخاطر...' },
    color: { bg: '#fff8ee', accent: '#c97a1a' },
  },
  {
    name: 'supply_constraint_agent',
    description: 'Delegate to Supply Constraint Specialist',
    agent: { en: 'Supply Constraint', ar: 'قيود التوريد' },
    label: { en: 'Checking supplier capacity & constraints...', ar: 'جارٍ فحص قدرات الموردين والقيود...' },
    color: { bg: '#f5f0ff', accent: '#6b47b8' },
  },
  {
    name: 'replenishment_agent',
    description: 'Delegate to Replenishment Specialist',
    agent: { en: 'Replenishment', ar: 'التجديد' },
    label: { en: 'Generating replenishment recommendations...', ar: 'جارٍ إنشاء توصيات التجديد...' },
    color: { bg: '#f0f7f0', accent: '#2e7d32' },
  },
  {
    name: 'morning_supply_brief',
    description: 'Generate morning supply brief',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Preparing morning supply brief...', ar: 'جارٍ إعداد موجز التوريد الصباحي...' },
    color: { bg: '#fff5f0', accent: '#c45a2c' },
  },
  {
    name: 'check_supply_alerts',
    description: 'Check supply chain alerts',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Checking supply chain alerts...', ar: 'جارٍ فحص تنبيهات سلسلة التوريد...' },
    color: { bg: '#fff0f0', accent: '#c41e3a' },
  },
  {
    name: 'scenario_analysis',
    description: 'Run scenario what-if analysis',
    agent: { en: 'Scenario Planner', ar: 'مخطط السيناريوهات' },
    label: { en: 'Running scenario analysis...', ar: 'جارٍ تشغيل تحليل السيناريو...' },
    color: { bg: '#f0f5ff', accent: '#1565c0' },
  },
  {
    name: 'kpi_dashboard',
    description: 'Retrieve KPI metrics',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Retrieving KPI dashboard data...', ar: 'جارٍ استرجاع بيانات لوحة المؤشرات...' },
    color: { bg: '#f0f7f0', accent: '#388e3c' },
  },
  {
    name: 'get_sku_detail',
    description: 'Get SKU details',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Looking up SKU details...', ar: 'جارٍ البحث عن تفاصيل المنتج...' },
    color: { bg: '#eef3ff', accent: '#3b6dd6' },
  },
  {
    name: 'get_supplier_detail',
    description: 'Get supplier details',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Looking up supplier details...', ar: 'جارٍ البحث عن تفاصيل المورد...' },
    color: { bg: '#f5f0ff', accent: '#6b47b8' },
  },
  {
    name: 'get_plant_detail',
    description: 'Get plant details',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Looking up plant details...', ar: 'جارٍ البحث عن تفاصيل المصنع...' },
    color: { bg: '#fff8ee', accent: '#c97a1a' },
  },
  {
    name: 'compare_scenarios',
    description: 'Compare scenarios',
    agent: { en: 'Scenario Planner', ar: 'مخطط السيناريوهات' },
    label: { en: 'Comparing scenario outcomes...', ar: 'جارٍ مقارنة نتائج السيناريوهات...' },
    color: { bg: '#f0f5ff', accent: '#1565c0' },
  },
  {
    name: 'get_production_schedule',
    description: 'Get production schedule',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Retrieving production schedule...', ar: 'جارٍ استرجاع جدول الإنتاج...' },
    color: { bg: '#fff8ee', accent: '#c97a1a' },
  },
  {
    name: 'generate_sop_deck',
    description: 'Generate S&OP presentation',
    agent: { en: 'Deck Generator', ar: 'مُنشئ العرض' },
    label: { en: 'Generating S&OP presentation...', ar: 'جارٍ إنشاء عرض S&OP...' },
    color: { bg: '#f5f0ff', accent: '#6B47B8' },
  },
  {
    name: 'generate_report',
    description: 'Generate report document',
    agent: { en: 'Report Generator', ar: 'مُنشئ التقرير' },
    label: { en: 'Generating report...', ar: 'جارٍ إنشاء التقرير...' },
    color: { bg: '#f0f7f0', accent: '#2e7d32' },
  },
  {
    name: 'suggest_actions',
    description: 'Suggest follow-up actions',
    agent: { en: 'Rashid AI', ar: 'رشيد' },
    label: { en: 'Preparing recommended actions...', ar: 'جارٍ إعداد الإجراءات المقترحة...' },
    color: { bg: '#f0f5ff', accent: '#0d47a1' },
  },
];


const _dispatchedStarts = new Set<string>();
const _dispatchedCompletes = new Set<string>();

function dispatchToolStart(toolCallId: string, name: string, args: Record<string, unknown>) {
  if (_dispatchedStarts.has(toolCallId)) return;
  _dispatchedStarts.add(toolCallId);
  window.dispatchEvent(new CustomEvent(TOOL_START_EVENT, { detail: { toolCallId, name, args } }));
}

function dispatchToolComplete(toolCallId: string, name: string, args: Record<string, unknown>) {
  if (_dispatchedCompletes.has(toolCallId)) return;
  _dispatchedCompletes.add(toolCallId);
  window.dispatchEvent(new CustomEvent(TOOL_COMPLETE_EVENT, { detail: { toolCallId, name, args } }));
}

function ToolRenderers() {
  const { lang } = useI18n();

  for (const tool of TOOLS) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    useRenderToolCall({
      name: tool.name,
      description: tool.description,
      render: (props: any) => {
        const status = props.status as string;
        const args = (props.args || {}) as Record<string, unknown>;
        const toolCallId = (props.toolCallId || props.name || '') as string;
        const done = status === 'complete';

        if (!done && toolCallId) {
          dispatchToolStart(toolCallId, tool.name, args);
        }
        if (done && toolCallId) {
          dispatchToolComplete(toolCallId, tool.name, args);
        }

        if (tool.name === 'scenario_analysis') {
          return <ScenarioPipelineProgress isComplete={done} />;
        }

        const agentName = tool.agent[lang];
        const label = tool.label[lang];
        const { bg, accent } = tool.color;

        return (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '7px 12px',
            margin: '3px 0',
            borderRadius: 8,
            borderLeft: `3px solid ${done ? '#2e7d32' : accent}`,
            background: done ? '#f0f7f0' : bg,
            fontSize: 13,
            color: done ? '#2e7d32' : '#444',
            transition: 'all 0.3s ease',
          }}>
            <span style={{ fontSize: 14, minWidth: 18, textAlign: 'center' }}>
              {done ? '✓' : '⏳'}
            </span>
            <span style={{
              fontWeight: 600,
              fontSize: 11,
              textTransform: 'uppercase',
              color: done ? '#2e7d32' : accent,
              letterSpacing: '0.4px',
              minWidth: 110,
              whiteSpace: 'nowrap',
            }}>
              {agentName}
            </span>
            <span style={{ color: done ? '#2e7d32' : '#555' }}>{label}</span>
          </div>
        );
      },
    });
  }

  return null;
}

export function ChatPanel() {
  const { t, dir } = useI18n();
  const containerRef = useRef<HTMLDivElement>(null);

  const submitMessage = useCallback((message: string) => {
    const trySubmit = (attempts: number) => {
      if (attempts <= 0) return;
      const container = containerRef.current;
      if (!container) {
        setTimeout(() => trySubmit(attempts - 1), 300);
        return;
      }

      const textarea = container.querySelector('textarea') as HTMLTextAreaElement | null;
      if (!textarea) {
        setTimeout(() => trySubmit(attempts - 1), 300);
        return;
      }

      const nativeSetter = Object.getOwnPropertyDescriptor(
        HTMLTextAreaElement.prototype, 'value'
      )?.set;
      nativeSetter?.call(textarea, message);

      const tracker = (textarea as any)._valueTracker;
      if (tracker) tracker.setValue('');

      textarea.dispatchEvent(new Event('input', { bubbles: true }));

      setTimeout(() => {
        const form = textarea.closest('form');
        if (form) {
          form.requestSubmit();
        } else {
          textarea.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13,
            bubbles: true,
            cancelable: true,
          }));
        }
      }, 300);
    };

    trySubmit(30);
  }, []);

  useEffect(() => {
    const pending = consumePendingChatMessage();
    if (pending) submitMessage(pending);
  }, [submitMessage]);

  useEffect(() => {
    const handler = (e: Event) => {
      const msg = (e as CustomEvent).detail?.message;
      if (msg) submitMessage(msg);
    };
    window.addEventListener(SEND_CHAT_MESSAGE_EVENT, handler);
    return () => window.removeEventListener(SEND_CHAT_MESSAGE_EVENT, handler);
  }, [submitMessage]);

  return (
    <div ref={containerRef} style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, overflow: 'hidden', direction: dir, height: '100%' }}>
      <ToolRenderers />
      <CopilotChat
        labels={{
          title: t('common.aiAssistant'),
          placeholder: t('chat.ask'),
          initial: t('chat.welcome'),
        }}
        className="rashid-chat"
        AssistantMessage={CleanAssistantMessage}
        suggestions="auto"
        RenderSuggestionsList={RashidSuggestions}
      />
    </div>
  );
}
