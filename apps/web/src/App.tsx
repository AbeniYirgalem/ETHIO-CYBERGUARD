import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import type { TabId } from './components/Sidebar';
import { OverviewView } from './components/OverviewView';
import { IncidentsView } from './components/IncidentsView';
import { ThreatIntelView } from './components/ThreatIntelView';
import { AssistantView } from './components/AssistantView';
import { RiskView } from './components/RiskView';
import { ResponseView } from './components/ResponseView';
import { ScenarioSimulator } from './components/ScenarioSimulator';
import { PublicLandingPage } from './components/PublicLandingPage';
import { PhishingAnalyzerView } from './components/PhishingAnalyzerView';
import { TyposquatView } from './components/TyposquatView';
import { OSINTReconView } from './components/OSINTReconView';
import { AwarenessSimulatorView } from './components/AwarenessSimulatorView';
import { UnifiedPipelineView } from './components/UnifiedPipelineView';
import { ReportsView } from './components/ReportsView';
import { SettingsView } from './components/SettingsView';
import { NotificationsModal } from './components/NotificationsModal';
import { CommandPalette } from './components/CommandPalette';
import { LoginModal } from './components/LoginModal';
import { ToastManager } from './components/ToastManager';
import type { ToastMessage } from './components/ToastManager';
import { soundManager } from './utils/sound';
import {
  ApiError, getSession, login, logout, fetchIncidents, fetchActions, decideAction,
} from './api/client';
import type { Session } from './api/client';
import { 
  INITIAL_INCIDENTS, 
  INITIAL_EVENTS, 
  INITIAL_INDICATORS, 
  INITIAL_ACTIONS, 
  INITIAL_TIMELINE 
} from './mockData';
import type { Incident, SecurityEvent, ResponseAction } from './types';

export const App: React.FC = () => {
  const [inPublicPortal, setInPublicPortal] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [incidents, setIncidents] = useState<Incident[]>(INITIAL_INCIDENTS);
  const [selectedIncident, setSelectedIncident] = useState<Incident>(INITIAL_INCIDENTS[0]);
  const [events, setEvents] = useState<SecurityEvent[]>(INITIAL_EVENTS);
  const [indicators] = useState(INITIAL_INDICATORS);
  const [actions, setActions] = useState<ResponseAction[]>(INITIAL_ACTIONS);
  const [isStreaming, setIsStreaming] = useState(true);
  const [liveCount, setLiveCount] = useState(4210);

  // Identity, Tenant & Notification State
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [language, setLanguage] = useState<'en' | 'am'>('en');
  const [currentOrg, setCurrentOrg] = useState("Commercial Bank of Ethiopia (CBE)");
  const [currentRole, setCurrentRole] = useState("SECURITY_ANALYST");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Real backend session. No session (or backend offline) = simulated demo data.
  const [session, setSession] = useState<Session | null>(() => getSession());
  const [liveMode, setLiveMode] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);

  // Toast dispatch and cleanup helper
  const addToast = (toast: Omit<ToastMessage, 'id' | 'timestamp'>) => {
    const now = new Date();
    const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' EAT';
    const newToast: ToastMessage = {
      id: `toast_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      timestamp,
      ...toast
    };
    setToasts(prev => [newToast, ...prev].slice(0, 5));
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== newToast.id));
    }, 5000);
  };

  const dismissToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const fallBackToDemo = (message: string) => {
    logout();
    setSession(null);
    setLiveMode(false);
    setIncidents(INITIAL_INCIDENTS);
    setSelectedIncident(INITIAL_INCIDENTS[0]);
    setActions(INITIAL_ACTIONS);
    setCurrentRole('SECURITY_ANALYST');
    addToast({ type: 'warning', title: 'Using demo data', message });
  };

  const handleLogin = async (email: string, password: string) => {
    const next = await login(email, password);
    setSession(next);
    setCurrentRole(next.user.role);
    soundManager.playSuccess();
    addToast({ type: 'success', title: 'Signed in', message: `${next.user.name} (${next.user.role})` });
  };

  const handleLogout = () => {
    logout();
    setSession(null);
    setLiveMode(false);
    setIncidents(INITIAL_INCIDENTS);
    setSelectedIncident(INITIAL_INCIDENTS[0]);
    setActions(INITIAL_ACTIONS);
    setCurrentRole('SECURITY_ANALYST');
    addToast({ type: 'info', title: 'Signed out', message: 'Showing simulated demo data.' });
  };

  const reportApiError = (err: unknown, title: string) => {
    if (err instanceof ApiError && err.status === 401) {
      fallBackToDemo('Session expired. Please sign in again.');
      return;
    }
    soundManager.playAlert();
    addToast({
      type: 'critical',
      title,
      message: err instanceof Error ? err.message : 'Unexpected error',
    });
  };

  // Load live incidents and SOAR actions whenever a real session exists
  useEffect(() => {
    if (!session) return;
    let cancelled = false;
    (async () => {
      const [inc, act] = await Promise.allSettled([fetchIncidents(), fetchActions()]);
      if (cancelled) return;
      if (inc.status === 'rejected' && act.status === 'rejected') {
        const reason = inc.reason;
        if (reason instanceof ApiError && reason.status === 401) {
          fallBackToDemo('Session expired. Please sign in again.');
        } else {
          setLiveMode(false);
          addToast({ type: 'warning', title: 'Backend unreachable', message: 'Showing simulated demo data.' });
        }
        return;
      }
      if (inc.status === 'fulfilled' && inc.value.length > 0) {
        setIncidents(inc.value);
        setSelectedIncident(inc.value[0]);
      }
      if (act.status === 'fulfilled') setActions(act.value);
      setLiveMode(true);
    })();
    return () => { cancelled = true; };
  }, [session]);

  const toggleSound = () => {
    const next = !soundEnabled;
    setSoundEnabled(next);
    soundManager.setEnabled(next);
    if (next) soundManager.playSuccess();
  };

  // Keyboard HUD shortcut (⌘K / Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
        soundManager.playClick();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Simulated live telemetry stream
  useEffect(() => {
    if (!isStreaming) return;
    const interval = setInterval(() => {
      setLiveCount(prev => prev + Math.floor(Math.random() * 80) - 35);
      
      const sampleEvents = [
        { host: 'SERVER-04', type: 'registry_read', user: 'SYSTEM', sev: 'INFO' as const, detail: 'HKLM\\SAM query' },
        { host: 'FW-PERIMETER-01', type: 'firewall_drop', user: 'ingress', sev: 'LOW' as const, detail: 'Blocked port 23 scan' },
        { host: 'LAPTOP-22', type: 'dns_lookup', user: 'finance_clerk', sev: 'INFO' as const, detail: 'Query: office.com' },
        { host: 'SERVER-04', type: 'network_socket', user: 'administrator', sev: 'HIGH' as const, detail: 'Egress beacon 185.220.101.5:443' }
      ];

      const chosen = sampleEvents[Math.floor(Math.random() * sampleEvents.length)];
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0] + ' EAT';

      const newEv: SecurityEvent = {
        event_id: `evt_${Date.now()}`,
        timestamp: timeStr,
        source: { type: 'endpoint', hostname: chosen.host, ip: '10.10.1.24' },
        event_type: chosen.type,
        severity: chosen.sev,
        user: chosen.user,
        process: { name: 'system', command_line: chosen.detail }
      };

      setEvents(prev => [newEv, ...prev.slice(0, 49)]);
    }, 4000);

    return () => clearInterval(interval);
  }, [isStreaming]);

  // Deep-link URL hash synchronization
  useEffect(() => {
    const handleHash = () => {
      let hash = window.location.hash.replace('#', '') as TabId | 'recon' | 'threat-intel';
      if (hash === 'recon') hash = 'osint';
      if (hash === 'threat-intel') hash = 'threat_intel';

      const validTabs: TabId[] = [
        'overview', 'monitoring', 'pipeline', 'incidents', 'threat_intel',
        'investigation', 'phishing', 'typosquat', 'osint', 'awareness',
        'assistant', 'risk', 'response', 'reports', 'settings', 'admin'
      ];
      if (validTabs.includes(hash as TabId)) {
        setActiveTab(hash as TabId);
      }
    };
    handleHash();
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, []);

  const switchTab = (tab: TabId) => {
    setActiveTab(tab);
    window.location.hash = tab;
    soundManager.playClick();
  };

  const [showDemoBanner, setShowDemoBanner] = useState(true);

  // Action Approval Handlers (live API when signed in, local simulation otherwise)
  const handleApproveAction = async (id: string, reason?: string) => {
    if (!liveMode) {
      setActions(prev => prev.map(a => a.id === id ? { ...a, status: 'APPROVED' } : a));
      soundManager.playLockAction();
      addToast({
        type: 'success',
        title: 'SOAR Action Executed (demo)',
        message: `Action ${id} approved in simulated mode.`
      });
      return;
    }
    try {
      const updated = await decideAction(id, 'approve', reason || 'Approved via SOC console');
      setActions(prev => prev.map(a => a.id === id ? { ...a, ...updated } : a));
      soundManager.playLockAction();
      addToast({
        type: 'success',
        title: 'SOAR Action Approved',
        message: `Action ${id} approved and recorded in the audit log.`
      });
    } catch (err) {
      reportApiError(err, 'Approval refused');
    }
  };

  const handleRejectAction = async (id: string, reason?: string) => {
    if (!liveMode) {
      setActions(prev => prev.map(a => a.id === id ? { ...a, status: 'REJECTED', rejection_reason: reason } : a));
      soundManager.playAlert();
      addToast({
        type: 'warning',
        title: 'Action Dismissed by Analyst (demo)',
        message: `Action ${id} rejected${reason ? `: ${reason}` : '.'}`
      });
      return;
    }
    try {
      const updated = await decideAction(id, 'reject', reason || 'Rejected via SOC console');
      setActions(prev => prev.map(a => a.id === id ? { ...a, ...updated } : a));
      soundManager.playAlert();
      addToast({
        type: 'warning',
        title: 'Action Rejected',
        message: `Action ${id} rejected${reason ? `: ${reason}` : '.'}`
      });
    } catch (err) {
      reportApiError(err, 'Rejection refused');
    }
  };

  const handleDrilldownIncident = (inc: Incident) => {
    setSelectedIncident(inc);
    setActiveTab('incidents');
    soundManager.playClick();
  };

  // Scenario Simulator Handlers
  const handleInjectEvents = (injected: SecurityEvent[]) => {
    setEvents(prev => [...injected, ...prev.slice(0, 45)]);
    soundManager.playAlert();
    addToast({
      type: 'warning',
      title: 'Telemetry Surge Injected',
      message: `${injected.length} synthetic attack events ingested into pipeline.`
    });
  };

  const handleAddIncident = (newInc: Incident) => {
    setIncidents(prev => [newInc, ...prev]);
    setSelectedIncident(newInc);
    setActiveTab('incidents');
    soundManager.playAlert();
    addToast({
      type: 'critical',
      title: `New Incident Raised: ${newInc.id}`,
      message: `${newInc.title} (${newInc.severity}) assigned to active queue.`
    });
  };

  const pendingCount = actions.filter(a => a.status === 'PENDING_APPROVAL').length;
  const criticalCount = incidents.filter(i => i.severity === 'CRITICAL').length;

  if (inPublicPortal) {
    return <PublicLandingPage onEnterSOC={() => setInPublicPortal(false)} />;
  }

  return (
    <div className="min-h-screen bg-[#070B12] text-[#E6EDF3] flex flex-col antialiased selection:bg-[#00D9FF] selection:text-black">
      {/* Header */}
      <Header 
        liveCount={liveCount} 
        onOpenNotifications={() => setNotificationsOpen(true)}
        language={language}
        onToggleLanguage={() => setLanguage(l => l === 'en' ? 'am' : 'en')}
        currentOrg={currentOrg}
        currentRole={currentRole}
        onToggleMobileMenu={() => setMobileMenuOpen(m => !m)}
        onOpenCommandPalette={() => setCommandPaletteOpen(true)}
        soundEnabled={soundEnabled}
        onToggleSound={toggleSound}
      />

      {/* Main App Body */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar */}
        <Sidebar 
          activeTab={activeTab} 
          setActiveTab={switchTab}
          pendingApprovalsCount={pendingCount}
          criticalIncidentsCount={criticalCount}
          mobileOpen={mobileMenuOpen}
          onCloseMobile={() => setMobileMenuOpen(false)}
        />

        {/* Dynamic Main Workspace Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 bg-[#070B12] space-y-6">
          {/* Demo Mode Alert Banner */}
          {showDemoBanner && !liveMode && (
            <div className="bg-[#FF9100]/10 border border-[#FF9100]/30 rounded-lg p-3 px-4 flex items-center justify-between text-xs text-[#FF9100]">
              <div className="flex items-center space-x-2">
                <span className="font-bold flex items-center">
                  <span className="w-2 h-2 rounded-full bg-[#FF9100] animate-pulse mr-2"></span>
                  Demo Mode:
                </span>
                <span>All incidents, assets, and telemetry metrics are currently simulated.</span>
              </div>
              <button 
                onClick={() => setShowDemoBanner(false)}
                className="text-[#FF9100]/70 hover:text-[#FF9100] font-mono text-sm px-1.5"
                title="Dismiss banner"
              >
                ✕
              </button>
            </div>
          )}

          {/* Top Switcher Banner: Public Portal Link & Active Session */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-[#0D131C] border border-[#1E2A38] px-4 py-2 rounded-lg text-xs gap-2">
            <span className="text-[#7D8A99]">
              Active Tenant: <strong className="text-white">{currentOrg}</strong> • Role: <span className="font-mono text-[#00D9FF]">{currentRole}</span>
              {' '}• Data:{' '}
              <span className={liveMode ? 'text-[#22C55E] font-bold' : 'text-[#FF9100] font-bold'}>
                {liveMode ? 'LIVE API' : 'SIMULATED'}
              </span>
              {session && <span className="text-[#7D8A99]"> • {session.user.name}</span>}
            </span>
            <div className="flex items-center space-x-4">
              {session ? (
                <button onClick={handleLogout} className="text-[#FF9100] hover:underline">Sign out</button>
              ) : (
                <button onClick={() => setLoginOpen(true)} className="text-[#22C55E] hover:underline font-bold">Sign in</button>
              )}
              <button
                onClick={() => setInPublicPortal(true)}
                className="text-[#00D9FF] hover:underline flex items-center space-x-1"
              >
                <span>Switch to Public Portal View →</span>
              </button>
            </div>
          </div>

          {/* Interactive Scenario Simulator */}
          {(activeTab === 'overview' || activeTab === 'monitoring') && (
            <ScenarioSimulator 
              onInjectEvents={handleInjectEvents}
              onAddIncident={handleAddIncident}
            />
          )}

          {activeTab === 'overview' && (
            <OverviewView 
              incidents={incidents}
              events={events}
              isStreaming={isStreaming}
              setIsStreaming={setIsStreaming}
              onSelectIncident={handleDrilldownIncident}
            />
          )}

          {activeTab === 'monitoring' && (
            <div className="space-y-6">
              <div className="pb-2 border-b border-[#1E2A38]">
                <h1 className="text-xl font-bold text-white">Security Event Monitoring & Pipeline Normalization</h1>
                <p className="text-xs text-[#7D8A99]">Real-time ECS-normalized log feed from Windows endpoints, Linux servers, and network perimeter</p>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-2">Live Normalized Stream ({events.length} Telemetry Records)</h2>
                <div className="divide-y divide-[#1E2A38] font-mono text-xs">
                  {events.map(ev => (
                    <div key={ev.event_id} className="py-2.5 flex flex-col sm:flex-row justify-between items-start sm:items-center text-xs">
                      <div>
                        <span className="text-[#00D9FF] font-bold mr-2">{ev.timestamp}</span>
                        <span className="text-white font-semibold mr-2">{ev.source.hostname}</span>
                        <span className="text-[#7D8A99] mr-2">[{ev.user}]:</span>
                        <span className="text-[#E6EDF3]">{ev.process?.command_line || ev.event_type}</span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold mt-1 sm:mt-0 ${
                        ev.severity === 'CRITICAL' ? 'bg-[#FF1744]/20 text-[#FF1744]' :
                        ev.severity === 'HIGH' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' : 'bg-[#00D9FF]/20 text-[#00D9FF]'
                      }`}>
                        {ev.severity}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'pipeline' && (
            <UnifiedPipelineView />
          )}

          {activeTab === 'incidents' && (
            <IncidentsView 
              selectedIncident={selectedIncident}
              allIncidents={incidents}
              onSelectIncident={setSelectedIncident}
              timeline={INITIAL_TIMELINE}
              actions={actions}
              onApproveAction={handleApproveAction}
              onRejectAction={handleRejectAction}
            />
          )}

          {activeTab === 'threat_intel' && (
            <ThreatIntelView indicators={indicators} />
          )}

          {activeTab === 'investigation' && (
            <IncidentsView 
              selectedIncident={selectedIncident}
              allIncidents={incidents}
              onSelectIncident={setSelectedIncident}
              timeline={INITIAL_TIMELINE}
              actions={actions}
              onApproveAction={handleApproveAction}
              onRejectAction={handleRejectAction}
            />
          )}

          {activeTab === 'phishing' && (
            <PhishingAnalyzerView />
          )}

          {activeTab === 'typosquat' && (
            <TyposquatView />
          )}

          {activeTab === 'osint' && (
            <OSINTReconView />
          )}

          {activeTab === 'awareness' && (
            <AwarenessSimulatorView />
          )}

          {activeTab === 'assistant' && (
            <AssistantView currentIncident={selectedIncident} />
          )}

          {activeTab === 'risk' && (
            <RiskView currentIncident={selectedIncident} />
          )}

          {activeTab === 'response' && (
            <ResponseView 
              actions={actions}
              onApproveAction={handleApproveAction}
              onRejectAction={handleRejectAction}
            />
          )}

          {activeTab === 'reports' && (
            <ReportsView />
          )}

          {activeTab === 'settings' && (
            <SettingsView 
              currentRole={currentRole}
              setCurrentRole={setCurrentRole}
              currentOrg={currentOrg}
              setCurrentOrg={setCurrentOrg}
              language={language}
              setLanguage={setLanguage}
            />
          )}

          {activeTab === 'admin' && (
            <div className="space-y-6">
              <div className="pb-2 border-b border-[#1E2A38]">
                <h1 className="text-xl font-bold text-white">System Administration & Detection Rules</h1>
                <p className="text-xs text-[#7D8A99]">Configure data sources, SIGMA rules, and enterprise multi-tenancy settings</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
                  <h2 className="text-sm font-bold text-white mb-2">Registered Data Sources</h2>
                  <ul className="text-xs space-y-2 text-[#E6EDF3]">
                    <li className="flex justify-between"><span>Windows Event Collector</span><span className="text-[#22C55E]">ONLINE</span></li>
                    <li className="flex justify-between"><span>Linux Auditd Daemon</span><span className="text-[#22C55E]">ONLINE</span></li>
                    <li className="flex justify-between"><span>Central Syslog (UDP 5140)</span><span className="text-[#22C55E]">ONLINE</span></li>
                    <li className="flex justify-between"><span>Ethio-CERT Threat Feed</span><span className="text-[#22C55E]">SYNCED</span></li>
                  </ul>
                </div>

                <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
                  <h2 className="text-sm font-bold text-white mb-2">Detection Rule Engine</h2>
                  <ul className="text-xs space-y-2 text-[#E6EDF3]">
                    <li className="flex justify-between"><span>Active SIGMA Rules</span><span className="font-mono text-white">148</span></li>
                    <li className="flex justify-between"><span>Behavioral Baselines</span><span className="font-mono text-white">32</span></li>
                    <li className="flex justify-between"><span>Anomaly Detection Thresholds</span><span className="font-mono text-white">19</span></li>
                  </ul>
                </div>

                <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
                  <h2 className="text-sm font-bold text-white mb-2">Tenant Organization</h2>
                  <p className="text-xs text-white font-bold">{currentOrg}</p>
                  <p className="text-[11px] text-[#7D8A99]">Addis Ababa HQ • Sector: Banking</p>
                  <p className="text-[11px] text-[#00D9FF] mt-2">Compliance: INSA Financial Directive 2026</p>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      <LoginModal
        isOpen={loginOpen}
        onClose={() => setLoginOpen(false)}
        onSubmit={handleLogin}
      />

      {/* Notifications Drawer Modal */}
      <NotificationsModal 
        isOpen={notificationsOpen}
        onClose={() => setNotificationsOpen(false)}
      />

      {/* Tactical HUD Command Palette (⌘K) */}
      <CommandPalette 
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onNavigate={switchTab}
        incidents={incidents}
        onSelectIncident={handleDrilldownIncident}
        onToggleSound={toggleSound}
        soundEnabled={soundEnabled}
        onToggleLanguage={() => setLanguage(l => l === 'en' ? 'am' : 'en')}
        language={language}
      />

      {/* Floating Tactical Toast Manager */}
      <ToastManager 
        toasts={toasts}
        onDismiss={dismissToast}
      />
    </div>
  );
};

export default App;
