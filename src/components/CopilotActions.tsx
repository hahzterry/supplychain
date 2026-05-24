import { useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export const TOOL_COMPLETE_EVENT = 'rashid:tool-complete';
export const TOOL_START_EVENT = 'rashid:tool-start';
export const ACTIONS_SUGGESTED_EVENT = 'rashid:actions-suggested';
export const SEND_CHAT_MESSAGE_EVENT = 'rashid:send-chat-message';

let _pendingChatMessage: string | null = null;
export function setPendingChatMessage(msg: string) {
  _pendingChatMessage = msg;
  window.dispatchEvent(new CustomEvent(SEND_CHAT_MESSAGE_EVENT, { detail: { message: msg } }));
}
export function consumePendingChatMessage(): string | null {
  const msg = _pendingChatMessage;
  _pendingChatMessage = null;
  return msg;
}

interface ToolCall {
  name: string;
  args: Record<string, unknown>;
}

function resolveNavigation(tools: ToolCall[]): string | null {
  const names = new Set(tools.map(t => t.name));

  if (names.has('get_sku_detail') || names.has('get_supplier_detail') || names.has('get_plant_detail')) {
    return null;
  }

  if (names.has('generate_sop_deck') || names.has('generate_report')) {
    return '/reports';
  }
  if (names.has('scenario_analysis')) {
    return '/scenario-planner';
  }
  if (names.has('check_supply_alerts')) {
    return '/';
  }
  if (names.has('morning_supply_brief')) {
    return '/';
  }
  if (names.has('demand_sensing_agent')) {
    return '/demand-forecast';
  }
  if (names.has('inventory_risk_agent')) {
    return '/inventory-health';
  }
  if (names.has('supply_constraint_agent')) {
    return '/supply-network';
  }
  if (names.has('replenishment_agent')) {
    return '/replenishment-plan';
  }
  if (names.has('get_production_schedule')) {
    return '/production-priorities';
  }

  return null;
}

export function useAgentNavigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const pendingRef = useRef<ToolCall[]>([]);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navigateRef = useRef(navigate);
  const locationRef = useRef(location);
  const navigatedRef = useRef(false);

  useEffect(() => { navigateRef.current = navigate; }, [navigate]);
  useEffect(() => { locationRef.current = location; }, [location]);

  // Reset the navigation lock when user manually navigates (clicks sidebar)
  useEffect(() => {
    navigatedRef.current = false;
  }, [location.pathname]);

  const flush = useCallback(() => {
    const tools = pendingRef.current;
    pendingRef.current = [];
    if (tools.length === 0) return;
    if (navigatedRef.current) return;

    const target = resolveNavigation(tools);
    if (!target) return;

    const loc = locationRef.current;
    const current = loc.pathname + loc.search;
    if (target === current) return;

    navigatedRef.current = true;
    navigateRef.current(target);
  }, []);

  useEffect(() => {
    const completeHandler = (e: Event) => {
      const { name, args } = (e as CustomEvent).detail as ToolCall;
      pendingRef.current.push({ name, args });
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(flush, 600);
    };

    window.addEventListener(TOOL_COMPLETE_EVENT, completeHandler);
    return () => {
      window.removeEventListener(TOOL_COMPLETE_EVENT, completeHandler);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [flush]);
}
