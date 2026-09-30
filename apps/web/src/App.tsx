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

  // Action Approval Handlers
  const handleApproveAction = (id: string) => {
    setActions(prev => prev.map(a => a.id === id ? { ...a, status: 'APPROVED' } : a));
  };

  const handleRejectAction = (id: string, reason?: string) => {
    setActions(prev => prev.map(a => a.id === id ? { ...a, status: 'REJECTED', rejection_reason: reason } : a));
  };

  const handleDrilldownIncident = (inc: Incident) => {
    setSelectedIncident(inc);
    setActiveTab('incidents');
  };

  // Scenario Simulator Handlers
  const handleInjectEvents = (injected: SecurityEvent[]) => {
    setEvents(prev => [...injected, ...prev.slice(0, 45)]);
  };

  const handleAddIncident = (newInc: Incident) => {
    setIncidents(prev => [newInc, ...prev]);
    setSelectedIncident(newInc);
    setActiveTab('incidents');
  };

  const pendingCount = actions.filter(a => a.status === 'PENDING_APPROVAL').length;
  const criticalCount = incidents.filter(i => i.severity === 'CRITICAL').length;

  if (inPublicPortal) {
    return <PublicLandingPage onEnterSOC={() => setInPublicPortal(false)} />;
  }

  return (
    <div className="min-h-screen bg-[#070B12] text-[#E6EDF3] flex flex-col antialiased selection:bg-[#00D9FF] selection:text-black">
      {/* Header */}
      <Header liveCount={liveCount} />

      {/* Main App Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab}
          pendingApprovalsCount={pendingCount}
          criticalIncidentsCount={criticalCount}
        />

        {/* Dynamic Main Workspace Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#070B12] space-y-6">
          {/* Top Switcher Banner: Public Portal Link */}
          <div className="flex justify-between items-center bg-[#0D131C] border border-[#1E2A38] px-4 py-2 rounded-lg text-xs">
            <span className="text-[#7D8A99]">Active Session: <strong>Dawit Mengistu (Tier-2 SOC Analyst)</strong></span>
            <button
              onClick={() => setInPublicPortal(true)}
              className="text-[#00D9FF] hover:underline flex items-center space-x-1"
            >
              <span>Switch to Public Portal View →</span>
            </button>
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
                  <p className="text-xs text-white font-bold">Commercial Bank of Ethiopia (CBE)</p>
                  <p className="text-[11px] text-[#7D8A99]">Addis Ababa HQ • Sector: Banking</p>
                  <p className="text-[11px] text-[#00D9FF] mt-2">Compliance: INSA Financial Directive 2026</p>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
