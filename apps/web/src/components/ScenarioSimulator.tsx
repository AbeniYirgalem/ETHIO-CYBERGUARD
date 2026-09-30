import React from 'react';
import { Play, Flame, ShieldAlert, Terminal, Lock, Globe, Mail } from 'lucide-react';
import type { SecurityEvent, Incident } from '../types';

interface ScenarioSimulatorProps {
  onInjectEvents: (events: SecurityEvent[]) => void;
  onAddIncident: (inc: Incident) => void;
}

export const ScenarioSimulator: React.FC<ScenarioSimulatorProps> = ({
  onInjectEvents,
  onAddIncident
}) => {
  const runScenario = (type: 'powershell' | 'brute_force' | 'malware' | 'account' | 'port_scan' | 'phishing') => {
    const timeStr = new Date().toTimeString().split(' ')[0] + ' EAT';

    if (type === 'powershell') {
      const ev: SecurityEvent = {
        event_id: `sim_ps_${Date.now()}`,
        timestamp: timeStr,
        source: { type: 'endpoint', hostname: 'SERVER-04', ip: '10.10.1.24' },
        event_type: 'process_execution',
        severity: 'CRITICAL',
        user: 'administrator',
        process: {
          name: 'powershell.exe',
          command_line: 'powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc SQBFAFgAIAAoAE4AZQB3AC0...',
          pid: 4812
        }
      };
      const ev2: SecurityEvent = {
        event_id: `sim_net_${Date.now()}`,
        timestamp: timeStr,
        source: { type: 'endpoint', hostname: 'SERVER-04', ip: '10.10.1.24' },
        event_type: 'network_connection',
        severity: 'CRITICAL',
        user: 'administrator',
        network: { destination_ip: '185.220.101.5', destination_port: 443 }
      };
      onInjectEvents([ev, ev2]);
    } else if (type === 'brute_force') {
      const evs: SecurityEvent[] = Array.from({ length: 4 }).map((_, i) => ({
        event_id: `sim_bf_${Date.now()}_${i}`,
        timestamp: timeStr,
        source: { type: 'firewall', hostname: 'FW-PERIMETER-01', ip: '197.156.70.1' },
        event_type: 'authentication_failure',
        severity: 'HIGH',
        user: `admin_user_${i}`,
        network: { source_ip: `197.156.90.${20 + i}`, destination_port: 22 }
      }));
      onInjectEvents(evs);
    } else if (type === 'malware') {
      const ev: SecurityEvent = {
        event_id: `sim_mimikatz_${Date.now()}`,
        timestamp: timeStr,
        source: { type: 'endpoint', hostname: 'LAPTOP-FINANCE-22', ip: '10.10.4.88' },
        event_type: 'process_execution',
        severity: 'CRITICAL',
        user: 'finance_clerk',
        process: { name: 'mimikatz.exe', command_line: 'mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords"' }
      };
      onInjectEvents([ev]);
      
      // Also spawn active incident
      const newInc: Incident = {
        id: `inc_${Date.now()}`,
        incident_number: `INC-000${Math.floor(Math.random() * 50) + 50}`,
        title: "LSASS Credential Extraction Attempt via Mimikatz",
        severity: "CRITICAL",
        status: "OPEN",
        risk_score: 95,
        affected_asset: "LAPTOP-FINANCE-22",
        asset_ip: "10.10.4.88",
        department: "Treasury Operations",
        first_seen: timeStr,
        last_activity: timeStr,
        assigned_analyst: "Dawit Mengistu",
        summary: "Process mimikatz.exe injected into LSASS process memory targeting plaintext domain credentials."
      };
      onAddIncident(newInc);
    } else if (type === 'port_scan') {
      const ev: SecurityEvent = {
        event_id: `sim_scan_${Date.now()}`,
        timestamp: timeStr,
        source: { type: 'firewall', hostname: 'FW-PERIMETER-01', ip: '197.156.70.1' },
        event_type: 'port_scan_sweep',
        severity: 'HIGH',
        user: 'anonymous',
        network: { source_ip: '45.154.255.89', destination_port: 445 }
      };
      onInjectEvents([ev]);
    } else if (type === 'phishing') {
      const ev: SecurityEvent = {
        event_id: `sim_phish_${Date.now()}`,
        timestamp: timeStr,
        source: { type: 'endpoint', hostname: 'WS-FINANCE-01', ip: '10.10.4.10' },
        event_type: 'dns_query',
        severity: 'HIGH',
        user: 'alem.tadesse',
        network: { destination_ip: 'update-winsec-cloud.com' }
      };
      onInjectEvents([ev]);
    } else if (type === 'account') {
      const ev: SecurityEvent = {
        event_id: `sim_offhours_${Date.now()}`,
        timestamp: timeStr,
        source: { type: 'endpoint', hostname: 'LAPTOP-FINANCE-22', ip: '10.10.4.88' },
        event_type: 'unusual_offhours_login',
        severity: 'MEDIUM',
        user: 'finance_clerk',
        network: { source_ip: '197.156.12.18' }
      };
      onInjectEvents([ev]);
    }
  };

  return (
    <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-3">
        <div>
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
            <Play className="w-3.5 h-3.5 text-[#00D9FF]" />
            <span>Interactive Attack Scenario Simulator (Synthetic Telemetry Only)</span>
          </h3>
          <p className="text-[11px] text-[#7D8A99]">Click any scenario to inject live attack telemetry and trigger detection pipelines:</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        <button
          onClick={() => runScenario('powershell')}
          className="p-2.5 bg-[#070B12] hover:bg-[#1E2A38] border border-[#FF1744]/40 hover:border-[#FF1744] rounded-lg text-left transition group"
        >
          <div className="flex items-center space-x-1 text-[#FF1744] text-[10px] font-bold">
            <Terminal className="w-3 h-3" />
            <span>PowerShell C2</span>
          </div>
          <span className="text-white text-[11px] font-medium block mt-0.5 truncate">Encoded Stager</span>
        </button>

        <button
          onClick={() => runScenario('brute_force')}
          className="p-2.5 bg-[#070B12] hover:bg-[#1E2A38] border border-[#F59E0B]/40 hover:border-[#F59E0B] rounded-lg text-left transition group"
        >
          <div className="flex items-center space-x-1 text-[#F59E0B] text-[10px] font-bold">
            <Lock className="w-3 h-3" />
            <span>Brute Force</span>
          </div>
          <span className="text-white text-[11px] font-medium block mt-0.5 truncate">SSH Ingress Flood</span>
        </button>

        <button
          onClick={() => runScenario('malware')}
          className="p-2.5 bg-[#070B12] hover:bg-[#1E2A38] border border-[#FF1744]/40 hover:border-[#FF1744] rounded-lg text-left transition group"
        >
          <div className="flex items-center space-x-1 text-[#FF1744] text-[10px] font-bold">
            <Flame className="w-3 h-3" />
            <span>Malware</span>
          </div>
          <span className="text-white text-[11px] font-medium block mt-0.5 truncate">LSASS Cred Dump</span>
        </button>

        <button
          onClick={() => runScenario('account')}
          className="p-2.5 bg-[#070B12] hover:bg-[#1E2A38] border border-[#00D9FF]/40 hover:border-[#00D9FF] rounded-lg text-left transition group"
        >
          <div className="flex items-center space-x-1 text-[#00D9FF] text-[10px] font-bold">
            <ShieldAlert className="w-3 h-3" />
            <span>Account Hijack</span>
          </div>
          <span className="text-white text-[11px] font-medium block mt-0.5 truncate">Off-Hours SWIFT</span>
        </button>

        <button
          onClick={() => runScenario('port_scan')}
          className="p-2.5 bg-[#070B12] hover:bg-[#1E2A38] border border-[#7D8A99]/40 hover:border-white rounded-lg text-left transition group"
        >
          <div className="flex items-center space-x-1 text-[#7D8A99] text-[10px] font-bold">
            <Globe className="w-3 h-3" />
            <span>Port Scan</span>
          </div>
          <span className="text-white text-[11px] font-medium block mt-0.5 truncate">Perimeter Sweep</span>
        </button>

        <button
          onClick={() => runScenario('phishing')}
          className="p-2.5 bg-[#070B12] hover:bg-[#1E2A38] border border-[#F59E0B]/40 hover:border-[#F59E0B] rounded-lg text-left transition group"
        >
          <div className="flex items-center space-x-1 text-[#F59E0B] text-[10px] font-bold">
            <Mail className="w-3 h-3" />
            <span>Phishing</span>
          </div>
          <span className="text-white text-[11px] font-medium block mt-0.5 truncate">Malicious C2 Domain</span>
        </button>
      </div>
    </div>
  );
};
