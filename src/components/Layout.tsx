import { useState, useRef, useCallback } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  makeStyles, tokens, Button, Text, Tooltip,
} from '@fluentui/react-components';
import {
  BoardRegular, ChartMultipleRegular, BoxRegular,
  VehicleTruckProfileRegular, CartRegular, BuildingFactoryRegular,
  BranchCompareRegular, DocumentRegular, SettingsRegular,
  SignOutRegular, LocalLanguageRegular, ChatRegular, DismissRegular,
  PeopleRegular, NavigationRegular,
} from '@fluentui/react-icons';
import { useI18n } from '../i18n';
import { useLogout } from '../App';
import { ChatPanel } from './ChatPanel';
import { AgentResultPanel } from './AgentResultPanel';

const useStyles = makeStyles({
  root: { display: 'flex', height: '100vh', overflow: 'hidden' },
  sidebar: {
    backgroundColor: tokens.colorNeutralBackground1,
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
    display: 'flex',
    flexDirection: 'column',
    paddingTop: '12px',
    paddingBottom: '12px',
    gap: '4px',
    flexShrink: 0,
    overflowX: 'hidden',
    overflowY: 'auto',
    transition: 'width 0.2s ease',
  },
  headerLogo: {
    height: '28px',
    width: 'auto',
    objectFit: 'contain' as const,
    marginRight: '12px',
  },
  navBtn: { minWidth: '40px', width: '40px', height: '40px', borderRadius: '8px' },
  navBtnActive: {
    minWidth: '40px', width: '40px', height: '40px',
    backgroundColor: tokens.colorBrandBackground2,
    borderRadius: '8px',
    boxShadow: `inset 3px 0 0 0 ${tokens.colorBrandForeground1}`,
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
    borderLeft: `1px solid ${tokens.colorNeutralStroke2}`,
    flexShrink: 0,
    overflow: 'hidden',
    position: 'relative' as const,
  },
  resizeHandle: {
    position: 'absolute' as const,
    left: 0,
    top: 0,
    bottom: 0,
    width: '4px',
    cursor: 'col-resize',
    backgroundColor: 'transparent',
    zIndex: 10,
    ':hover': {
      backgroundColor: tokens.colorBrandBackground2,
    },
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
  { path: '/labor-utilization', icon: <PeopleRegular />, labelKey: 'nav.labor' },
  { path: '/reports', icon: <DocumentRegular />, labelKey: 'nav.reports' },
  { path: '/settings', icon: <SettingsRegular />, labelKey: 'nav.settings' },
];

export function Layout() {
  const styles = useStyles();
  const navigate = useNavigate();
  const location = useLocation();
  const { t, lang, setLang } = useI18n();
  const logout = useLogout();
  const [chatOpen, setChatOpen] = useState(true);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [chatWidth, setChatWidth] = useState(380);
  const dragging = useRef(false);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    const startX = e.clientX;
    const startWidth = chatWidth;
    const onMouseMove = (ev: MouseEvent) => {
      if (!dragging.current) return;
      const delta = startX - ev.clientX;
      const newWidth = Math.min(700, Math.max(300, startWidth + delta));
      setChatWidth(newWidth);
    };
    const onMouseUp = () => {
      dragging.current = false;
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }, [chatWidth]);

  const sidebarWidth = sidebarExpanded ? 200 : 56;

  return (
    <div className={styles.root}>
      <nav className={styles.sidebar} style={{ width: sidebarWidth, alignItems: sidebarExpanded ? 'stretch' : 'center' }}>
        {/* Logo + Toggle */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: sidebarExpanded ? '0 8px' : '0',
          justifyContent: sidebarExpanded ? 'space-between' : 'center',
          marginBottom: 8,
        }}>
          <div style={{
            width: '40px', height: '40px', borderRadius: '8px', backgroundColor: '#1a1a2e',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <img src="/hd_small_logo.png" alt="Héroux-Devtek" style={{ width: '32px', height: '32px', objectFit: 'contain' }} />
          </div>
          {sidebarExpanded && (
            <Button
              appearance="subtle"
              icon={<NavigationRegular />}
              size="small"
              onClick={() => setSidebarExpanded(false)}
              style={{ minWidth: 28, width: 28, height: 28 }}
            />
          )}
        </div>

        {/* Expand toggle (collapsed state) */}
        {!sidebarExpanded && (
          <Tooltip content="Expand menu" relationship="label" positioning="after">
            <Button
              appearance="subtle"
              icon={<NavigationRegular />}
              className={styles.navBtn}
              onClick={() => setSidebarExpanded(true)}
            />
          </Tooltip>
        )}

        {/* Nav Items */}
        {navItems.map(item => {
          const isActive = location.pathname === item.path;
          if (sidebarExpanded) {
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '8px 12px', border: 'none', cursor: 'pointer',
                  borderRadius: 8, background: isActive ? tokens.colorBrandBackground2 : 'transparent',
                  boxShadow: isActive ? `inset 3px 0 0 0 ${tokens.colorBrandForeground1}` : 'none',
                  color: isActive ? tokens.colorBrandForeground1 : tokens.colorNeutralForeground1,
                  fontSize: 13, fontWeight: isActive ? 600 : 400,
                  textAlign: 'left', width: '100%',
                  transition: 'background 0.15s',
                }}
              >
                <span style={{ fontSize: 18, display: 'flex', alignItems: 'center' }}>{item.icon}</span>
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {t(item.labelKey)}
                </span>
              </button>
            );
          }
          return (
            <Tooltip key={item.path} content={t(item.labelKey)} relationship="label" positioning="after">
              <Button
                appearance="subtle"
                icon={item.icon}
                className={isActive ? styles.navBtnActive : styles.navBtn}
                onClick={() => navigate(item.path)}
              />
            </Tooltip>
          );
        })}

        <div className={styles.spacer} />

        {/* Bottom actions */}
        {sidebarExpanded ? (
          <>
            <button
              onClick={() => setLang(lang === 'en' ? 'fr' : lang === 'fr' ? 'es' : 'en')}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '8px 12px', border: 'none', cursor: 'pointer',
                borderRadius: 8, background: 'transparent',
                color: tokens.colorNeutralForeground1, fontSize: 13, textAlign: 'left', width: '100%',
              }}
            >
              <span style={{ fontSize: 18, display: 'flex', alignItems: 'center' }}><LocalLanguageRegular /></span>
              <span>{lang === 'en' ? 'English' : lang === 'fr' ? 'Français' : 'Español'}</span>
            </button>
            <button
              onClick={logout}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '8px 12px', border: 'none', cursor: 'pointer',
                borderRadius: 8, background: 'transparent',
                color: tokens.colorNeutralForeground1, fontSize: 13, textAlign: 'left', width: '100%',
              }}
            >
              <span style={{ fontSize: 18, display: 'flex', alignItems: 'center' }}><SignOutRegular /></span>
              <span>Logout</span>
            </button>
          </>
        ) : (
          <>
            <Tooltip content={lang === 'en' ? 'English' : lang === 'fr' ? 'Français' : 'Español'} relationship="label" positioning="after">
              <Button appearance="subtle" icon={<LocalLanguageRegular />} className={styles.navBtn} onClick={() => setLang(lang === 'en' ? 'fr' : lang === 'fr' ? 'es' : 'en')} />
            </Tooltip>
            <Tooltip content="Logout" relationship="label" positioning="after">
              <Button appearance="subtle" icon={<SignOutRegular />} className={styles.navBtn} onClick={logout} />
            </Tooltip>
          </>
        )}
      </nav>

      <div className={styles.main}>
        <header className={styles.topbar}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <img src="/hd-logo.png" alt="Héroux-Devtek" className={styles.headerLogo} />
            <Text weight="semibold" size={400}>{t('app.name')} — {t('app.subtitle')}</Text>
          </div>
          <Button
            appearance="subtle"
            icon={chatOpen ? <DismissRegular /> : <ChatRegular />}
            onClick={() => setChatOpen(!chatOpen)}
          />
        </header>
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <div className={styles.content}>
            <AgentResultPanel />
            <Outlet />
          </div>
          {chatOpen && (
            <div className={styles.chatPanel} style={{ width: chatWidth }}>
              <div
                className={styles.resizeHandle}
                onMouseDown={onMouseDown}
              />
              <ChatPanel />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
