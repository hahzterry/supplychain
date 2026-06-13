import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { useLocation } from 'react-router-dom';
import { useI18n } from '../i18n';
import { getSessionId, renewSessionId, getSessionHeader } from '../App';
import { getPageContext } from '../lib/chatPageContext';
import { SEND_CHAT_MESSAGE_EVENT, TOOL_START_EVENT, TOOL_COMPLETE_EVENT } from './CopilotActions';
import { useAgentResult } from '../contexts/AgentResultContext';

interface PlanningInfo {
  agent: string;
  tool: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  planning?: PlanningInfo[];
}

function PlanningBlock({ planning }: { planning: PlanningInfo[] }) {
  return (
    <div style={{
      marginBottom: 8,
      borderRadius: 6,
      border: '1px solid #f0e6cc',
      background: '#fdf8ee',
      padding: '6px 10px',
    }}>
      {planning.map((p, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
          <span style={{ color: '#B8860B', fontWeight: 600 }}>⚙</span>
          <span style={{ fontWeight: 600, color: '#8B6914' }}>{p.agent}</span>
          <span style={{
            background: '#f0e6cc',
            borderRadius: 3,
            padding: '1px 5px',
            fontSize: 10,
            fontFamily: 'monospace',
            color: '#6b5300',
          }}>{p.tool}</span>
        </div>
      ))}
    </div>
  );
}

function predictPlan(message: string): PlanningInfo | null {
  const lower = message.toLowerCase();
  if (lower.match(/morning|brief|daily/)) return { agent: 'Atlas AI', tool: 'morning_supply_brief' };
  if (lower.match(/alert|warning|stockout/)) return { agent: 'Atlas AI', tool: 'check_supply_alerts' };
  if (lower.match(/inventory|stock|dos|risk/)) return { agent: 'Inventory Risk', tool: 'inventory_risk_agent' };
  if (lower.match(/demand|forecast/)) return { agent: 'Demand Sensing', tool: 'demand_sensing_agent' };
  if (lower.match(/supplier|supply.*constraint|titanium|forging/)) return { agent: 'Supply Constraint', tool: 'supply_constraint_agent' };
  if (lower.match(/replenish|order|purchase/)) return { agent: 'Replenishment', tool: 'replenishment_agent' };
  if (lower.match(/scenario|what.?if|disrupt/)) return { agent: 'Scenario Planner', tool: 'scenario_analysis' };
  if (lower.match(/kpi|dashboard|fill rate|service level/)) return { agent: 'Atlas AI', tool: 'kpi_dashboard' };
  if (lower.match(/deck|ppt|presentation|s&op/)) return { agent: 'Deck Generator', tool: 'generate_sop_deck' };
  if (lower.match(/report|excel|word/)) return { agent: 'Report Generator', tool: 'generate_report' };
  if (lower.match(/labor|utiliz|overtime/)) return { agent: 'Atlas AI', tool: 'labor_utilization_dashboard' };
  if (lower.match(/production|schedule|capacity|line/)) return { agent: 'Atlas AI', tool: 'get_production_schedule' };
  return null;
}

function MessageActions({ content, onRegenerate }: { content: string; onRegenerate: () => void }) {
  const [copied, setCopied] = useState(false);
  const [vote, setVote] = useState<'up' | 'down' | null>(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const btnStyle = (active?: boolean): React.CSSProperties => ({
    background: 'none', border: 'none', cursor: 'pointer', padding: '3px 6px',
    borderRadius: 4, fontSize: 13, lineHeight: 1, color: active ? '#B8860B' : '#999',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  });

  return (
    <div style={{ display: 'flex', gap: 2, marginTop: 4, marginLeft: 34 }}>
      <button onClick={handleCopy} style={btnStyle()} title="Copy">
        {copied ? '✓' : '⧉'}
      </button>
      <button onClick={() => setVote(vote === 'up' ? null : 'up')} style={btnStyle(vote === 'up')} title="Good response">
        ▲
      </button>
      <button onClick={() => setVote(vote === 'down' ? null : 'down')} style={btnStyle(vote === 'down')} title="Bad response">
        ▼
      </button>
      <button onClick={onRegenerate} style={btnStyle()} title="Regenerate">
        ↻
      </button>
    </div>
  );
}

export function ChatPanel() {
  const { t, lang } = useI18n();
  const location = useLocation();
  const pageContext = getPageContext(location.pathname);
  const { setPresentation } = useAgentResult();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [predictedPlan, setPredictedPlan] = useState<PlanningInfo | null>(null);
  const [dynamicSuggestions, setDynamicSuggestions] = useState<Array<{ id: string; label: string; message: string }> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const sendMessageRef = useRef<(text: string) => void>(() => {});

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    setDynamicSuggestions(null);
  }, [location.pathname]);

  // Listen for messages dispatched from other pages (Reports, ScenarioPlanner, etc.)
  useEffect(() => {
    const handler = (e: Event) => {
      const msg = (e as CustomEvent).detail?.message;
      if (msg) sendMessageRef.current(msg);
    };
    window.addEventListener(SEND_CHAT_MESSAGE_EVENT, handler);
    return () => window.removeEventListener(SEND_CHAT_MESSAGE_EVENT, handler);
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setPredictedPlan(predictPlan(text));

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getSessionHeader() },
        body: JSON.stringify({
          message: text,
          session_id: getSessionId(),
          language: lang,
        }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = '';
      let planningItems: PlanningInfo[] = [];
      let buffer = '';
      let currentEvent = '';

      const assistantMsg: ChatMessage = { role: 'assistant', content: '', planning: [] };
      setMessages(prev => [...prev, assistantMsg]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim();
            continue;
          }
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);

              if (currentEvent === 'delta') {
                assistantContent += data.content || '';
                setMessages(prev => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.role === 'assistant') {
                    updated[updated.length - 1] = { ...last, content: assistantContent, planning: planningItems.length > 0 ? [...planningItems] : undefined };
                  }
                  return updated;
                });
              } else if (currentEvent === 'planning') {
                planningItems.push({ agent: data.agent, tool: data.tool || '' });
                setPredictedPlan(null);
                window.dispatchEvent(new CustomEvent(TOOL_START_EVENT, { detail: { name: data.tool, args: {} } }));
                window.dispatchEvent(new CustomEvent(TOOL_COMPLETE_EVENT, { detail: { name: data.tool, args: {} } }));
                setMessages(prev => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.role === 'assistant') {
                    updated[updated.length - 1] = { ...last, planning: [...planningItems] };
                  }
                  return updated;
                });
              } else if (currentEvent === 'done') {
                if (data.suggestions) {
                  setDynamicSuggestions(data.suggestions.map((s: any, i: number) => ({
                    id: `sug_${i}`,
                    label: s.title,
                    message: s.message,
                  })));
                }
              } else if (currentEvent === 'presentation') {
                setPresentation(data);
              } else if (currentEvent === 'error') {
                assistantContent += `\n\n⚠️ ${data.message || t('common.errorOccurred')}`;
                setMessages(prev => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.role === 'assistant') {
                    updated[updated.length - 1] = { ...last, content: assistantContent };
                  }
                  return updated;
                });
              }
            } catch {}
            currentEvent = '';
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ ${t('common.connectionError')}: ${e.message}` }]);
      }
    } finally {
      setLoading(false);
      setPredictedPlan(null);
      abortRef.current = null;
    }
  }, [lang, loading]);

  sendMessageRef.current = sendMessage;

  const clearChat = useCallback(() => {
    const sid = getSessionId();
    fetch(`/api/chat/${sid}`, { method: 'DELETE' }).catch(() => {});
    renewSessionId();
    setMessages([]);
    setDynamicSuggestions(null);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#fff' }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '10px 14px', borderBottom: '1px solid #e5e5e5',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 16 }}>✦</span>
          <span style={{ fontSize: 13, fontWeight: 600, color: '#333' }}>Atlas AI</span>
          {loading && <span style={{ fontSize: 11, color: '#888' }}>●</span>}
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            style={{
              display: 'flex', alignItems: 'center', gap: 4,
              border: '1px solid #ddd', borderRadius: 6, padding: '4px 8px',
              fontSize: 11, color: '#666', background: 'transparent', cursor: 'pointer',
            }}
          >
            ↺ {t('chat.newSession')}
          </button>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 14, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.length === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1, gap: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, marginBottom: 8 }}>✦</div>
              <p style={{ fontSize: 13, color: '#888', margin: 0, maxWidth: 280, lineHeight: 1.5 }}>{pageContext.welcome[lang]}</p>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 6, maxWidth: 320 }}>
              {pageContext.chips.map(action => (
                <button
                  key={action.id}
                  onClick={() => sendMessage(action.message)}
                  style={{
                    borderRadius: 20, border: '1px solid #e8d5a0', background: '#fdf8ee',
                    padding: '5px 12px', fontSize: 11, color: '#8B6914', cursor: 'pointer',
                  }}
                >
                  {action.label[lang]}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i}>
            <div style={{ display: 'flex', gap: 8, justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {msg.role === 'assistant' && (
                <div style={{
                  width: 26, height: 26, borderRadius: '50%', background: '#fdf8ee',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, flexShrink: 0,
                }}>✦</div>
              )}
              <div style={{
                maxWidth: '82%', borderRadius: 10, padding: '8px 12px', fontSize: 13, lineHeight: 1.5,
                ...(msg.role === 'user'
                  ? { background: '#B8860B', color: '#fff' }
                  : { background: '#f5f5f5', color: '#333' }),
              }}>
                {msg.planning && msg.planning.length > 0 && <PlanningBlock planning={msg.planning} />}
                {msg.role === 'assistant' ? (
                  <div className="chat-markdown">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                )}
              </div>
              {msg.role === 'user' && (
                <div style={{
                  width: 26, height: 26, borderRadius: '50%', background: '#e5e5e5',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, flexShrink: 0,
                }}>👤</div>
              )}
            </div>
            {msg.role === 'assistant' && msg.content && !loading && (
              <MessageActions
                content={msg.content}
                onRegenerate={() => {
                  const userMsg = messages.slice(0, i).reverse().find(m => m.role === 'user');
                  if (userMsg) {
                    setMessages(prev => prev.slice(0, i));
                    sendMessage(userMsg.content);
                  }
                }}
              />
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', gap: 8 }}>
            <div style={{
              width: 26, height: 26, borderRadius: '50%', background: '#fdf8ee',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, flexShrink: 0,
            }}>✦</div>
            <div style={{ borderRadius: 10, padding: '8px 12px', background: '#f5f5f5' }}>
              {predictedPlan ? (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#B8860B', fontWeight: 600, marginBottom: 4 }}>
                    <span className="spin-slow">⏳</span> {predictedPlan.agent}
                  </div>
                  <span style={{
                    background: '#f0e6cc', borderRadius: 3, padding: '1px 5px',
                    fontSize: 10, fontFamily: 'monospace', color: '#6b5300',
                  }}>{predictedPlan.tool}</span>
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#888' }}>
                  <span className="spin-slow">⏳</span> {t('common.processing')}
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion chips */}
      {messages.length > 0 && !loading && (() => {
        const chips = dynamicSuggestions || pageContext.chips.map(c => ({ id: c.id, label: c.label[lang], message: c.message }));
        return chips.length > 0 ? (
          <div style={{ borderTop: '1px solid #f0f0f0', padding: '8px 12px', display: 'flex', flexWrap: 'wrap', gap: 5 }}>
            <span style={{ fontSize: 11, color: '#B8860B', marginTop: 3 }}>✨</span>
            {chips.map(action => (
              <button
                key={action.id}
                onClick={() => sendMessage(action.message)}
                style={{
                  borderRadius: 16, border: '1px solid #e8d5a0', background: '#fdf8ee',
                  padding: '3px 10px', fontSize: 11, color: '#8B6914', cursor: 'pointer',
                }}
              >
                {action.label}
              </button>
            ))}
          </div>
        ) : null;
      })()}

      {/* Input */}
      <div style={{ borderTop: '1px solid #e5e5e5', padding: 12 }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8 }}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={t('chat.ask') || 'Ask Atlas AI...'}
            disabled={loading}
            style={{
              flex: 1, borderRadius: 8, border: '1px solid #ddd', padding: '8px 12px',
              fontSize: 13, outline: 'none',
            }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            style={{
              borderRadius: 8, background: '#B8860B', color: '#fff', border: 'none',
              padding: '8px 14px', fontSize: 13, cursor: 'pointer', opacity: loading || !input.trim() ? 0.5 : 1,
            }}
          >
            ↑
          </button>
        </form>
      </div>
    </div>
  );
}
