import { createContext, useContext, useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { FluentProvider, createLightTheme, type BrandVariants } from '@fluentui/react-components';
import { I18nProvider } from './i18n';
import { Layout } from './components/Layout';
import { DetailDrawerProvider } from './contexts/DetailDrawerContext';
import { AgentResultProvider } from './contexts/AgentResultContext';
import DetailDrawer from './components/DetailDrawer';
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
import LaborUtilization from './pages/LaborUtilization';

const hdBrand: BrandVariants = {
  10: '#001529',
  20: '#001F3F',
  30: '#002B55',
  40: '#003A75',
  50: '#0C4A8C',
  60: '#1E5FA3',
  70: '#3474B8',
  80: '#D4930D',
  90: '#E8A825',
  100: '#D4930D',
  110: '#F0C050',
  120: '#F5D88A',
  130: '#F9E8B0',
  140: '#FCF2D6',
  150: '#FEF9EE',
  160: '#FFFDF8',
};

const hdTheme = createLightTheme(hdBrand);

const LogoutContext = createContext<() => void>(() => {});
export const useLogout = () => useContext(LogoutContext);

export function getSessionId(): string {
  let id = sessionStorage.getItem('hd_session_id');
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem('hd_session_id', id);
  }
  return id;
}

export function renewSessionId(): string {
  const id = crypto.randomUUID();
  sessionStorage.setItem('hd_session_id', id);
  return id;
}

export function getSessionHeader(): Record<string, string> {
  return { 'X-Session-Id': getSessionId() };
}

function AppInner() {
  return (
    <FluentProvider theme={hdTheme}>
      <AgentResultProvider>
      <DetailDrawerProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/demand-forecast" element={<DemandForecast />} />
            <Route path="/inventory-health" element={<InventoryHealth />} />
            <Route path="/supply-network" element={<SupplyNetwork />} />
            <Route path="/replenishment-plan" element={<ReplenishmentPlan />} />
            <Route path="/production-priorities" element={<ProductionPriorities />} />
            <Route path="/scenario-planner" element={<ScenarioPlanner />} />
            <Route path="/labor-utilization" element={<LaborUtilization />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
        <DetailDrawer />
      </DetailDrawerProvider>
      </AgentResultProvider>
    </FluentProvider>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(() => sessionStorage.getItem('hd_auth') === 'true');

  const logout = useCallback(() => {
    sessionStorage.removeItem('hd_auth');
    setAuthed(false);
  }, []);

  if (!authed) {
    return (
      <FluentProvider theme={hdTheme}>
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
