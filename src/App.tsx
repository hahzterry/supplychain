import { createContext, useContext, useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { FluentProvider, createLightTheme, type BrandVariants } from '@fluentui/react-components';
import { CopilotKit } from '@copilotkit/react-core';
import { I18nProvider, useI18n } from './i18n';
import { Layout } from './components/Layout';
import { DetailDrawerProvider } from './contexts/DetailDrawerContext';
import DetailDrawer from './components/DetailDrawer';
import { ToolEventBridge } from './components/ToolEventBridge';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import DemandForecast from './pages/DemandForecast';
import InventoryHealth from './pages/InventoryHealth';
import SupplyNetwork from './pages/SupplyNetwork';
import ReplenishmentPlan from './pages/ReplenishmentPlan';
import ProductionPriorities from './pages/ProductionPriorities';
import ScenarioPlanner from './pages/ScenarioPlanner';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

const rashidBrand: BrandVariants = {
  10: '#0A2E1A',
  20: '#0F4025',
  30: '#145230',
  40: '#1A6E3D',
  50: '#2D915C',
  60: '#3FA070',
  70: '#52B084',
  80: '#66C498',
  90: '#8AD6B2',
  100: '#66C498',
  110: '#8AD6B2',
  120: '#A8E4C8',
  130: '#C2EEDA',
  140: '#D9F5E9',
  150: '#E9F9F1',
  160: '#F4FCF8',
};

const rashidTheme = createLightTheme(rashidBrand);

const ChatResetContext = createContext<() => void>(() => {});
export const useChatReset = () => useContext(ChatResetContext);

const LogoutContext = createContext<() => void>(() => {});
export const useLogout = () => useContext(LogoutContext);

export function getSessionId(): string {
  let id = sessionStorage.getItem('rashid_session_id');
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem('rashid_session_id', id);
  }
  return id;
}

export function renewSessionId(): string {
  const id = crypto.randomUUID();
  sessionStorage.setItem('rashid_session_id', id);
  return id;
}

export function getSessionHeader(): Record<string, string> {
  return { 'X-Session-Id': getSessionId() };
}

function CopilotWrapper({ children }: { children: React.ReactNode }) {
  const { lang } = useI18n();
  const [sessionId, setSessionId] = useState(() => getSessionId());
  const resetChat = useCallback(() => {
    const newId = renewSessionId();
    setSessionId(newId);
  }, []);

  return (
    <ChatResetContext.Provider value={resetChat}>
      <CopilotKit
        key={sessionId}
        runtimeUrl="/api/copilotkit"
        agent="rashid_orchestrator"
        threadId={sessionId}
        properties={{ language: lang, sessionId }}
        headers={{ 'X-Session-Id': sessionId }}
      >
        {children}
      </CopilotKit>
    </ChatResetContext.Provider>
  );
}

function AppInner() {
  const { dir } = useI18n();

  return (
    <CopilotWrapper>
      <FluentProvider theme={rashidTheme} dir={dir}>
        <DetailDrawerProvider>
          <div dir={dir} style={{ direction: dir }}>
            <Routes>
              <Route element={<Layout />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/demand-forecast" element={<DemandForecast />} />
                <Route path="/inventory-health" element={<InventoryHealth />} />
                <Route path="/supply-network" element={<SupplyNetwork />} />
                <Route path="/replenishment-plan" element={<ReplenishmentPlan />} />
                <Route path="/production-priorities" element={<ProductionPriorities />} />
                <Route path="/scenario-planner" element={<ScenarioPlanner />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/settings" element={<Settings />} />
              </Route>
            </Routes>
            <DetailDrawer />
            <ToolEventBridge />
          </div>
        </DetailDrawerProvider>
      </FluentProvider>
    </CopilotWrapper>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(() => sessionStorage.getItem('rashid_auth') === 'true');

  const logout = useCallback(() => {
    sessionStorage.removeItem('rashid_auth');
    setAuthed(false);
  }, []);

  if (!authed) {
    return (
      <FluentProvider theme={rashidTheme}>
        <Login onLogin={() => setAuthed(true)} />
      </FluentProvider>
    );
  }

  return (
    <LogoutContext.Provider value={logout}>
      <I18nProvider>
        <BrowserRouter>
          <AppInner />
        </BrowserRouter>
      </I18nProvider>
    </LogoutContext.Provider>
  );
}
