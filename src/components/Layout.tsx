import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  makeStyles, tokens, Button, Text, Tooltip,
} from '@fluentui/react-components';
import {
  BoardRegular, ChartMultipleRegular, BoxRegular,
  VehicleTruckProfileRegular, CartRegular, BuildingFactoryRegular,
  BranchCompareRegular, DocumentRegular, SettingsRegular,
  SignOutRegular, LocalLanguageRegular, ChatRegular, DismissRegular,
} from '@fluentui/react-icons';
import { useI18n } from '../i18n';
import { useLogout } from '../App';
import { ChatPanel } from './ChatPanel';
import { useAgentNavigation } from './CopilotActions';

const useStyles = makeStyles({
  root: { display: 'flex', height: '100vh', overflow: 'hidden' },
  sidebar: {
    width: '56px',
    backgroundColor: tokens.colorNeutralBackground1,
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    paddingTop: '12px',
    paddingBottom: '12px',
    gap: '4px',
    flexShrink: 0,
  },
  logo: {
    width: '36px',
    height: '36px',
    marginBottom: '12px',
    borderRadius: '6px',
    objectFit: 'contain' as const,
  },
  navBtn: { minWidth: '40px', width: '40px', height: '40px' },
  navBtnActive: {
    minWidth: '40px', width: '40px', height: '40px',
    backgroundColor: tokens.colorBrandBackground2,
  },
  spacer: { flex: 1 },
  main: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  topbar: {
    height: '48px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingLeft: '16px',
    paddingRight: '16px',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  content: { flex: 1, overflow: 'auto', padding: '24px' },
  chatPanel: {
    width: '380px',
    borderLeft: `1px solid ${tokens.colorNeutralStroke2}`,
    flexShrink: 0,
    overflow: 'hidden',
  },
});

const navItems = [
  { path: '/', icon: <BoardRegular />, labelKey: 'nav.dashboard' },
  { path: '/demand-forecast', icon: <ChartMultipleRegular />, labelKey: 'nav.demandForecast' },
  { path: '/inventory-health', icon: <BoxRegular />, labelKey: 'nav.inventoryHealth' },
  { path: '/supply-network', icon: <VehicleTruckProfileRegular />, labelKey: 'nav.supplyNetwork' },
  { path: '/replenishment-plan', icon: <CartRegular />, labelKey: 'nav.replenishment' },
  { path: '/production-priorities', icon: <BuildingFactoryRegular />, labelKey: 'nav.production' },
  { path: '/scenario-planner', icon: <BranchCompareRegular />, labelKey: 'nav.scenarios' },
  { path: '/reports', icon: <DocumentRegular />, labelKey: 'nav.reports' },
  { path: '/settings', icon: <SettingsRegular />, labelKey: 'nav.settings' },
];

export function Layout() {
  const styles = useStyles();
  const navigate = useNavigate();
  const location = useLocation();
  const { t, toggle } = useI18n();
  const logout = useLogout();
  const [chatOpen, setChatOpen] = useState(true);
  useAgentNavigation();

  return (
    <div className={styles.root}>
      <nav className={styles.sidebar}>
        <img src="/agi-logo.png" alt="AGI" className={styles.logo} />
        {navItems.map(item => (
          <Tooltip key={item.path} content={t(item.labelKey)} relationship="label" positioning="after">
            <Button
              appearance="subtle"
              icon={item.icon}
              className={location.pathname === item.path ? styles.navBtnActive : styles.navBtn}
              onClick={() => navigate(item.path)}
            />
          </Tooltip>
        ))}
        <div className={styles.spacer} />
        <Tooltip content="Toggle Language" relationship="label" positioning="after">
          <Button appearance="subtle" icon={<LocalLanguageRegular />} className={styles.navBtn} onClick={toggle} />
        </Tooltip>
        <Tooltip content="Logout" relationship="label" positioning="after">
          <Button appearance="subtle" icon={<SignOutRegular />} className={styles.navBtn} onClick={logout} />
        </Tooltip>
      </nav>

      <div className={styles.main}>
        <header className={styles.topbar}>
          <Text weight="semibold" size={400}>{t('app.name')} — {t('app.subtitle')}</Text>
          <Button
            appearance="subtle"
            icon={chatOpen ? <DismissRegular /> : <ChatRegular />}
            onClick={() => setChatOpen(!chatOpen)}
          />
        </header>
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <div className={styles.content}>
            <Outlet />
          </div>
          {chatOpen && (
            <div className={styles.chatPanel}>
              <ChatPanel />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
