import React, { useState } from 'react';
import { 
  AlertOctagon, 
  ShieldAlert, 
  Activity, 
  Flame, 
  ArrowUpRight, 
  Clock, 
  Server, 
  Play, 
  Pause,
  Download,
  Search
} from 'lucide-react';
import type { Incident, SecurityEvent } from '../types';
import { EthiopiaCyberRadar } from './EthiopiaCyberRadar';
import { soundManager } from '../utils/sound';

interface OverviewViewProps {
  incidents: Incident[];
  events: SecurityEvent[];
  isStreaming: boolean;
  setIsStreaming: (val: boolean) => void;
  onSelectIncident: (inc: Incident) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  incidents,
  events,
  isStreaming,
  setIsStreaming,
  onSelectIncident
}) => {
  const [selectedSeverity, setSelectedSeverity] = useState<'ALL' | 'CRITICAL' | 'HIGH' | 'MEDIUM'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Filtered incidents based on active filter and query
  const filteredIncidents = incidents.filter(inc => {
    const matchesSev = selectedSeverity === 'ALL' || inc.severity === selectedSeverity;
    const matchesQuery = searchQuery.trim() === '' || 
      inc.incident_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.affected_asset.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.department.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSev && matchesQuery;
  });

  // Export incident queue report as downloadable JSON/briefing
  const exportIncidentBriefing = () => {
    soundManager.playSuccess();
    const briefing = {
      report: "ETHIO-CYBERGUARD Executive Threat Briefing",
      timestamp: new Date().toISOString(),
      location: "Addis Ababa Cyber Command HQ",
      total_incidents: incidents.length,
      critical_count: incidents.filter(i => i.severity === 'CRITICAL').length,
      incidents: incidents.map(i => ({
        id: i.incident_number,
        title: i.title,
        severity: i.severity,
        status: i.status,
        asset: i.affected_asset,
        risk_score: i.risk_score,
        summary: i.summary
      }))
    };

    const blob = new Blob([JSON.stringify(briefing, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ETHIO-CYBERGUARD-Briefing-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Top Bar: Live Status & Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-2 border-b border-[#1E2A38] gap-3">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <span>Enterprise Security Posture & Command</span>
            <span className="text-xs px-2 py-0.5 rounded bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20 flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E] animate-pulse"></span>
              <span>Active Defense Grid</span>
            </span>
          </h1>
          <p className="text-xs text-[#7D8A99]">Real-time situational awareness across Ethiopian banking networks, telecom infrastructure, and cloud perimeters</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Export Briefing Button */}
          <button 
            onClick={exportIncidentBriefing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-[#111923] text-[#00D9FF] border border-[#1E2A38] hover:border-[#00D9FF]/40 hover:bg-[#00D9FF]/10 transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Incident Dossier</span>
          </button>

          {/* Stream Pause / Resume */}
          <button 
            onClick={() => {
              setIsStreaming(!isStreaming);
              soundManager.playClick();
            }}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium border transition ${
              isStreaming 
                ? 'bg-[#00D9FF]/10 text-[#00D9FF] border-[#00D9FF]/30 hover:bg-[#00D9FF]/20' 
                : 'bg-[#111923] text-[#7D8A99] border-[#1E2A38] hover:text-white'
            }`}
          >
            {isStreaming ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isStreaming ? 'Pause Feed' : 'Resume Feed'}</span>
          </button>
        </div>
      </div>

      {/* 4 Top-level KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Critical Card */}
        <div className="bg-[#111923] border border-[#FF1744]/40 rounded-xl p-4 relative overflow-hidden group hover:border-[#FF1744] transition-all shadow-lg shadow-[#FF1744]/5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#FF1744] uppercase tracking-wider">Critical Threats</span>
            <div className="p-2 rounded-lg bg-[#FF1744]/10 text-[#FF1744]">
              <AlertOctagon className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-extrabold text-white">
              {incidents.filter(i => i.severity === 'CRITICAL').length}
            </span>
            <span className="text-[11px] text-[#FF1744] ml-2 font-medium">Require immediate containment</span>
          </div>
          <div className="mt-2 text-[10px] text-[#7D8A99] flex items-center justify-between">
            <span>+2 in last hour</span>
            <span className="text-[#FF1744] font-semibold">Highest Priority</span>
          </div>
        </div>

        {/* High Risk Card */}
        <div className="bg-[#111923] border border-[#F59E0B]/40 rounded-xl p-4 relative overflow-hidden group hover:border-[#F59E0B] transition-all shadow-lg shadow-[#F59E0B]/5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#F59E0B] uppercase tracking-wider">High Risk Alerts</span>
            <div className="p-2 rounded-lg bg-[#F59E0B]/10 text-[#F59E0B]">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-extrabold text-white">23</span>
            <span className="text-[11px] text-[#7D8A99] ml-2">Active triage</span>
          </div>
          <div className="mt-2 text-[10px] text-[#7D8A99] flex items-center justify-between">
            <span>Baseline variance: +14%</span>
            <span className="text-[#F59E0B] font-semibold">Under Investigation</span>
          </div>
        </div>

        {/* Active Incidents Card */}
        <div className="bg-[#111923] border border-[#00D9FF]/40 rounded-xl p-4 relative overflow-hidden group hover:border-[#00D9FF] transition-all shadow-lg shadow-[#00D9FF]/5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#00D9FF] uppercase tracking-wider">Active Incidents</span>
            <div className="p-2 rounded-lg bg-[#00D9FF]/10 text-[#00D9FF]">
              <Flame className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-extrabold text-white">{incidents.length}</span>
            <span className="text-[11px] text-[#00D9FF] ml-2 font-medium">3 In Forensics</span>
          </div>
          <div className="mt-2 text-[10px] text-[#7D8A99] flex items-center justify-between">
            <span>Avg MTTR: 28 min</span>
            <span className="text-[#00D9FF] font-semibold">AI Correlated</span>
          </div>
        </div>

        {/* Events Card */}
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4 relative overflow-hidden group hover:border-[#7D8A99] transition-all shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#7D8A99] uppercase tracking-wider">Events Ingested</span>
            <div className="p-2 rounded-lg bg-[#1E2A38] text-white">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-extrabold text-white">51,240</span>
            <span className="text-[11px] text-[#22C55E] ml-2 font-mono">EPS Peak</span>
          </div>
          <div className="mt-2 text-[10px] text-[#7D8A99] flex items-center justify-between">
            <span>Sliding window: 60s</span>
            <span className="text-[#22C55E] font-semibold">100% Normalized</span>
          </div>
        </div>
      </div>

      {/* NEW: Ethiopian Critical Infrastructure Defense Radar Component */}
      <EthiopiaCyberRadar />

      {/* Threat Activity & Top Threats Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Activity Interactive Chart */}
        <div className="lg:col-span-2 bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                <span>Threat Activity Timeline</span>
                <span className="text-[10px] font-normal text-[#7D8A99]">(24h rolling window)</span>
              </h2>
              <p className="text-xs text-[#7D8A99]">Normalized event velocity, correlated alert spikes & threat detections</p>
            </div>
            <div className="flex items-center space-x-4 text-xs font-mono">
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-[#00D9FF]"></span>
                <span className="text-[#7D8A99]">Events (x10k)</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-[#FF1744]"></span>
                <span className="text-[#7D8A99]">Critical Alerts</span>
              </div>
            </div>
          </div>

          {/* SVG Activity Visualization */}
          <div className="h-44 w-full flex items-end justify-between pt-4 pb-2 px-2 border-b border-[#1E2A38]">
            {[
              { time: '00:00', events: 35, alerts: 1 },
              { time: '02:00', events: 20, alerts: 0 },
              { time: '03:14', events: 65, alerts: 6 },
              { time: '06:00', events: 45, alerts: 2 },
              { time: '08:00', events: 80, alerts: 3 },
              { time: '10:00', events: 95, alerts: 8 },
              { time: '11:30', events: 70, alerts: 4 }
            ].map((bar, i) => (
              <div key={i} className="flex flex-col items-center flex-1 group">
                <div className="w-full max-w-[28px] flex flex-col items-center justify-end h-32 relative">
                  {bar.alerts > 0 && (
                    <div 
                      className="w-full bg-[#FF1744] rounded-t-sm mb-0.5 transition-all group-hover:brightness-125"
                      style={{ height: `${bar.alerts * 8}px` }}
                      title={`${bar.alerts} critical alerts`}
                    ></div>
                  )}
                  <div 
                    className="w-full bg-[#00D9FF]/40 rounded-sm group-hover:bg-[#00D9FF] transition-all"
                    style={{ height: `${bar.events * 0.9}px` }}
                    title={`${bar.events}k events`}
                  ></div>
                </div>
                <span className="text-[10px] font-mono text-[#7D8A99] mt-2">{bar.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Threats Breakdown */}
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white mb-1">Top Threat Vectors</h2>
            <p className="text-xs text-[#7D8A99] mb-4">Classified attack patterns targeting our infrastructure</p>

            <div className="space-y-3.5">
              {[
                { name: 'Distributed SSH / RDP Brute Force', count: 1420, percent: 74, color: 'bg-[#FF1744]' },
                { name: 'Obfuscated PowerShell Execution', count: 18, percent: 55, color: 'bg-[#FF1744]' },
                { name: 'Off-Hours SWIFT Directory Access', count: 3, percent: 38, color: 'bg-[#F59E0B]' },
                { name: 'Known Malicious C2 Beaconing', count: 12, percent: 45, color: 'bg-[#FF1744]' },
                { name: 'Privilege Escalation via Sudo', count: 9, percent: 22, color: 'bg-[#00D9FF]' },
              ].map((item, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-white font-medium">{item.name}</span>
                    <span className="text-[#7D8A99] font-mono">{item.count}</span>
                  </div>
                  <div className="w-full bg-[#0D131C] h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full ${item.color}`} style={{ width: `${item.percent}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#1E2A38] flex justify-between items-center text-xs text-[#7D8A99]">
            <span>Feed Source: Ethio-CERT / INSA</span>
            <span className="text-[#00D9FF] cursor-pointer hover:underline font-mono">MITRE ATT&CK Matrix →</span>
          </div>
        </div>
      </div>

      {/* Priority Incident Queue with Interactive Filters & Search */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-[#1E2A38] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <Flame className="w-4 h-4 text-[#FF1744]" />
              <span>Priority Incident Queue</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#FF1744]/10 text-[#FF1744] border border-[#FF1744]/30">
                {filteredIncidents.length} Visible
              </span>
            </h2>
            <p className="text-xs text-[#7D8A99]">Correlated security incidents requiring analyst triage and containment</p>
          </div>

          {/* Interactive Severity Filter Buttons & Search Input */}
          <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            {/* Search Input */}
            <div className="relative flex-1 sm:w-56">
              <Search className="w-3.5 h-3.5 text-[#7D8A99] absolute left-2.5 top-2.5" />
              <input 
                type="text" 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search incident, host, dept..."
                className="w-full bg-[#0D131C] border border-[#1E2A38] rounded-md py-1.5 pl-8 pr-2 text-xs text-[#E6EDF3] placeholder-[#7D8A99] focus:outline-none focus:border-[#00D9FF]"
              />
            </div>

            {/* Severity Pill Switcher */}
            <div className="flex items-center space-x-1 bg-[#0D131C] p-1 rounded-lg border border-[#1E2A38]">
              {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'] as const).map(sev => (
                <button
                  key={sev}
                  onClick={() => {
                    setSelectedSeverity(sev);
                    soundManager.playClick();
                  }}
                  className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold transition ${
                    selectedSeverity === sev 
                      ? 'bg-[#00D9FF] text-black' 
                      : 'text-[#7D8A99] hover:text-white'
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0D131C] text-[#7D8A99] uppercase font-mono text-[10px] tracking-wider border-b border-[#1E2A38]">
              <tr>
                <th className="py-2.5 px-4">Incident ID</th>
                <th className="py-2.5 px-4">Title & Details</th>
                <th className="py-2.5 px-4">Severity</th>
                <th className="py-2.5 px-4">Risk Score</th>
                <th className="py-2.5 px-4">Affected Asset</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2A38] text-[#E6EDF3]">
              {filteredIncidents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-xs text-[#7D8A99]">
                    No incidents match the active filter criteria.
                  </td>
                </tr>
              ) : (
                filteredIncidents.map((inc) => (
                  <tr 
                    key={inc.id} 
                    onClick={() => {
                      soundManager.playClick();
                      onSelectIncident(inc);
                    }}
                    className="hover:bg-[#0D131C]/60 cursor-pointer transition group"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-[#00D9FF] flex items-center space-x-1.5">
                      <span>{inc.incident_number}</span>
                      <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition text-[#00D9FF]" />
                    </td>
                    <td className="py-3 px-4 max-w-md">
                      <p className="font-semibold text-white truncate">{inc.title}</p>
                      <p className="text-[11px] text-[#7D8A99] truncate">{inc.summary}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        inc.severity === 'CRITICAL' ? 'bg-[#FF1744]/15 text-[#FF1744] border border-[#FF1744]/30' :
                        inc.severity === 'HIGH' ? 'bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/30' :
                        'bg-[#00D9FF]/15 text-[#00D9FF] border border-[#00D9FF]/30'
                      }`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold">
                      <span className={`text-sm ${
                        inc.risk_score >= 85 ? 'text-[#FF1744]' :
                        inc.risk_score >= 70 ? 'text-[#F59E0B]' : 'text-[#00D9FF]'
                      }`}>
                        {inc.risk_score}
                      </span>
                      <span className="text-[#7D8A99] text-[10px]">/100</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-1.5">
                        <Server className="w-3.5 h-3.5 text-[#7D8A99]" />
                        <span className="font-mono text-white">{inc.affected_asset}</span>
                      </div>
                      <span className="text-[10px] text-[#7D8A99]">{inc.department}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#111923] border border-[#1E2A38] text-[#E6EDF3]">
                        {inc.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <button 
                        onClick={(e) => { 
                          e.stopPropagation();
                          soundManager.playClick();
                          onSelectIncident(inc); 
                        }}
                        className="px-2.5 py-1 rounded bg-[#00D9FF]/10 text-[#00D9FF] hover:bg-[#00D9FF] hover:text-black font-semibold text-[11px] transition flex items-center space-x-1 border border-[#00D9FF]/30"
                      >
                        <span>Investigate</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Live Security Events Feed Table */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-[#1E2A38] flex justify-between items-center">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <Activity className="w-4 h-4 text-[#00D9FF]" />
              <span>Live Security Event Ingestion Feed</span>
            </h2>
            <p className="text-xs text-[#7D8A99]">Normalized raw events arriving from endpoint agents and perimeter syslog</p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#0D131C] text-[#7D8A99] border border-[#1E2A38]">
            {events.length} Telemetry Records Streamed
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0D131C] text-[#7D8A99] uppercase font-mono text-[10px] tracking-wider border-b border-[#1E2A38]">
              <tr>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Source Host</th>
                <th className="py-2.5 px-4">Event Type</th>
                <th className="py-2.5 px-4">User</th>
                <th className="py-2.5 px-4">Payload / Arguments</th>
                <th className="py-2.5 px-4">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2A38] font-mono text-[11px]">
              {events.map((ev) => (
                <tr key={ev.event_id} className="hover:bg-[#0D131C]/60 transition">
                  <td className="py-2.5 px-4 text-[#7D8A99] flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-[#00D9FF]" />
                    <span>{ev.timestamp}</span>
                  </td>
                  <td className="py-2.5 px-4 font-semibold text-white">{ev.source.hostname}</td>
                  <td className="py-2.5 px-4 text-[#00D9FF]">{ev.event_type}</td>
                  <td className="py-2.5 px-4 text-[#E6EDF3]">{ev.user}</td>
                  <td className="py-2.5 px-4 text-[#7D8A99] max-w-xs truncate">
                    {ev.process?.command_line || (ev.network ? `${ev.network.source_ip || ''} → ${ev.network.destination_ip}:${ev.network.destination_port}` : 'Standard telemetry')}
                  </td>
                  <td className="py-2.5 px-4">
                    <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                      ev.severity === 'CRITICAL' ? 'text-[#FF1744] bg-[#FF1744]/10' :
                      ev.severity === 'HIGH' ? 'text-[#F59E0B] bg-[#F59E0B]/10' :
                      ev.severity === 'MEDIUM' ? 'text-[#00D9FF] bg-[#00D9FF]/10' : 'text-[#7D8A99]'
                    }`}>
                      {ev.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
