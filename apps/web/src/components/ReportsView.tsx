import React, { useState } from 'react';
import { 
  Download, 
  CheckCircle2, 
  Printer 
} from 'lucide-react';

export const ReportsView: React.FC = () => {
  const [selectedReport, setSelectedReport] = useState<'incident' | 'executive' | 'compliance'>('incident');
  const [isExporting, setIsExporting] = useState(false);

  const handleExportCSV = () => {
    setIsExporting(true);
    setTimeout(() => {
      const csvContent = "data:text/csv;charset=utf-8,Report_ID,Title,Severity,Status,RiskScore,Organization,GeneratedAt\nREP-INC-00042,PowerShell C2 Beaconing,CRITICAL,CONTAINED,92,Commercial Bank of Ethiopia,2026-09-30T11:45:00Z\n";
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `ETHIO-CYBERGUARD_${selectedReport.toUpperCase()}_REPORT.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setIsExporting(false);
    }, 600);
  };

  const handleExportJSON = () => {
    setIsExporting(true);
    setTimeout(() => {
      const data = {
        report_id: "REP-ETHIO-2026-09",
        report_type: selectedReport,
        organization: "Commercial Bank of Ethiopia",
        classification: "CONFIDENTIAL // TLP:AMBER",
        overall_security_posture_score: 91.5,
        compliance: {
          insa_directive_2026: "COMPLIANT",
          pci_dss_v4: "AUDITED",
          iso_27001: "CERTIFIED"
        },
        active_threats_blocked_today: 312,
        generated_at: new Date().toISOString()
      };
      const jsonUri = "data:application/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
      const link = document.createElement("a");
      link.setAttribute("href", jsonUri);
      link.setAttribute("download", `ETHIO-CYBERGUARD_${selectedReport.toUpperCase()}_REPORT.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setIsExporting(false);
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#1E2A38]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white">Executive & Compliance Reporting Center</h1>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
              AI Agent 6: Executive Report
            </span>
          </div>
          <p className="text-xs text-[#7D8A99] mt-1">
            Automated generation of technical incident dossiers, executive boardroom briefs, and INSA regulatory filings.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleExportCSV}
            disabled={isExporting}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#111923] hover:bg-[#1E2A38] border border-[#1E2A38] text-xs font-semibold text-[#E6EDF3] transition"
          >
            <Download className="w-3.5 h-3.5 text-[#00D9FF]" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={handleExportJSON}
            disabled={isExporting}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#111923] hover:bg-[#1E2A38] border border-[#1E2A38] text-xs font-semibold text-[#E6EDF3] transition"
          >
            <Download className="w-3.5 h-3.5 text-[#22C55E]" />
            <span>Export JSON</span>
          </button>
          <button
            onClick={() => window.print()}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#00D9FF] hover:bg-[#00B8D9] text-black text-xs font-bold transition"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Report Selection Tabs */}
      <div className="flex space-x-2 border-b border-[#1E2A38]">
        <button
          onClick={() => setSelectedReport('incident')}
          className={`px-4 py-2 text-xs font-semibold border-b-2 transition ${
            selectedReport === 'incident'
              ? 'border-[#00D9FF] text-[#00D9FF]'
              : 'border-transparent text-[#7D8A99] hover:text-white'
          }`}
        >
          Technical Incident Report (INC-00042)
        </button>
        <button
          onClick={() => setSelectedReport('executive')}
          className={`px-4 py-2 text-xs font-semibold border-b-2 transition ${
            selectedReport === 'executive'
              ? 'border-[#00D9FF] text-[#00D9FF]'
              : 'border-transparent text-[#7D8A99] hover:text-white'
          }`}
        >
          Quarterly Executive Brief (Q3 2026)
        </button>
        <button
          onClick={() => setSelectedReport('compliance')}
          className={`px-4 py-2 text-xs font-semibold border-b-2 transition ${
            selectedReport === 'compliance'
              ? 'border-[#00D9FF] text-[#00D9FF]'
              : 'border-transparent text-[#7D8A99] hover:text-white'
          }`}
        >
          INSA / National Bank Compliance Audit
        </button>
      </div>

      {/* Render Selected Report Content */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-6">
        {selectedReport === 'incident' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-4 border-b border-[#1E2A38]">
              <div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#FF1744]/15 text-[#FF1744] border border-[#FF1744]/30 font-bold">
                  CRITICAL SEVERITY // TLP:AMBER
                </span>
                <h2 className="text-base font-bold text-white mt-2">
                  INC-00042: Suspicious Obfuscated PowerShell Activity & Cobalt Strike C2 Beaconing
                </h2>
                <p className="text-xs text-[#7D8A99]">Target: Commercial Bank of Ethiopia (Core Banking Infrastructure • SERVER-04)</p>
              </div>
              <div className="text-right text-xs text-[#7D8A99] mt-2 sm:mt-0 font-mono">
                <p>Status: <span className="text-[#22C55E] font-bold">CONTAINED</span></p>
                <p>Risk Score: <span className="text-[#FF1744] font-bold">92 / 100</span></p>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#00D9FF]">1. Executive Incident Summary</h3>
              <p className="text-xs text-[#E6EDF3] leading-relaxed">
                On 2026-09-30 at 10:42:00 EAT, a critical security incident was detected on production banking host <strong>SERVER-04 (10.10.1.24)</strong>. 
                An interactive session under the <code>administrator</code> service account spawned an obfuscated PowerShell process invoking a remote stager. 
                Subsequent network telemetry revealed active egress beaconing to external IPv4 <code>185.220.101.5:443</code>, identified as a known Cobalt Strike C2 server. 
                Under dual-custody authorization, the host was quarantined via SOAR host isolation, preventing unauthorized database ledger tampering.
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#00D9FF]">2. MITRE ATT&CK Killchain Evidence</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
                  <p className="text-[#7D8A99] font-mono text-[10px]">T1059.001 - EXECUTION</p>
                  <p className="font-bold text-white mt-1">Obfuscated PowerShell</p>
                  <p className="text-[#7D8A99] text-[11px] mt-1 font-mono">powershell.exe -NoP -W Hidden -Enc SQBFAFgA...</p>
                </div>
                <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
                  <p className="text-[#7D8A99] font-mono text-[10px]">T1071.001 - C2 BEACONING</p>
                  <p className="font-bold text-white mt-1">Egress to Malicious IP</p>
                  <p className="text-[#7D8A99] text-[11px] mt-1 font-mono">Dest: 185.220.101.5:443 (Ethio-CERT Blacklist)</p>
                </div>
                <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
                  <p className="text-[#7D8A99] font-mono text-[10px]">T1003.001 - CREDENTIAL ACCESS</p>
                  <p className="font-bold text-white mt-1">LSASS Memory Scan Attempt</p>
                  <p className="text-[#7D8A99] text-[11px] mt-1 font-mono">Blocked by Endpoint Memory Guard</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#00D9FF]">3. SOAR Containment & Remediation Actions Taken</h3>
              <ul className="text-xs space-y-1.5 text-[#E6EDF3]">
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
                  <span><strong>Host Isolation:</strong> Host SERVER-04 severed from LAN, maintaining only encrypted SOC EDR command channel.</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
                  <span><strong>Perimeter Firewall Drop:</strong> IP 185.220.101.5 blocked on all edge routers (Rule FW-BLOCK-185-220-101-5).</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
                  <span><strong>Credential Invalidation:</strong> Service account Kerberos tickets revoked and password rotated in Active Directory.</span>
                </li>
              </ul>
            </div>
          </div>
        )}

        {selectedReport === 'executive' && (
          <div className="space-y-6">
            <div className="pb-4 border-b border-[#1E2A38]">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/30 font-bold">
                BOARD OF DIRECTORS // EXECUTIVE SUMMARY
              </span>
              <h2 className="text-base font-bold text-white mt-2">
                National Cyber Defense & Threat Resilience Briefing (Q3 2026)
              </h2>
              <p className="text-xs text-[#7D8A99]">Target: Ethiopian Financial & Telecommunications Critical Infrastructure</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-xl text-center">
                <p className="text-2xl font-bold text-[#00D9FF]">14,209</p>
                <p className="text-[11px] text-[#7D8A99] mt-1">Attacks Neutralized</p>
              </div>
              <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-xl text-center">
                <p className="text-2xl font-bold text-[#22C55E]">3.8%</p>
                <p className="text-[11px] text-[#7D8A99] mt-1">Phishing Click Rate (Down from 14.2%)</p>
              </div>
              <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-xl text-center">
                <p className="text-2xl font-bold text-white">4.2 min</p>
                <p className="text-[11px] text-[#7D8A99] mt-1">Mean Time to Detect (MTTD)</p>
              </div>
              <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-xl text-center">
                <p className="text-2xl font-bold text-[#F59E0B]">11.5 min</p>
                <p className="text-[11px] text-[#7D8A99] mt-1">Mean Time to Contain (MTTC)</p>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#00D9FF]">Strategic Threat Outlook</h3>
              <p className="text-xs text-[#E6EDF3] leading-relaxed">
                Adversaries have increasingly focused on localized social engineering schemes targeting <strong>Telebirr mobile wallets</strong> and <strong>CBE Birr banking credentials</strong>, 
                leveraging Ge'ez script SMS lures. Implementation of automated header authentication (SPF/DKIM/DMARC) and AI-driven domain typosquatting monitoring has reduced brand confusion by 73% across Q3.
              </p>
            </div>
          </div>
        )}

        {selectedReport === 'compliance' && (
          <div className="space-y-6">
            <div className="pb-4 border-b border-[#1E2A38]">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/30 font-bold">
                REGULATORY STATUS: FULLY COMPLIANT
              </span>
              <h2 className="text-base font-bold text-white mt-2">
                National Cyber Security Standards & INSA Regulatory Compliance Audit
              </h2>
              <p className="text-xs text-[#7D8A99]">Verified against Information Network Security Administration (INSA) Financial Directives</p>
            </div>

            <div className="divide-y divide-[#1E2A38] text-xs">
              <div className="py-3 flex justify-between items-center">
                <div>
                  <p className="font-bold text-white">INSA Directive No. 04/2026: Mandatory 24-Hour Critical Incident Reporting</p>
                  <p className="text-[#7D8A99] text-[11px]">Requires electronic notification to Ethio-CERT within 24 hours of compromise confirmation.</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-[#22C55E]/15 text-[#22C55E] font-bold">COMPLIANT (Automated)</span>
              </div>

              <div className="py-3 flex justify-between items-center">
                <div>
                  <p className="font-bold text-white">National Bank of Ethiopia (NBE): Financial Cyber Resilience Framework</p>
                  <p className="text-[#7D8A99] text-[11px]">Enforces dual-custody authorization for interbank SWIFT and transaction ledger containment.</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-[#22C55E]/15 text-[#22C55E] font-bold">VERIFIED</span>
              </div>

              <div className="py-3 flex justify-between items-center">
                <div>
                  <p className="font-bold text-white">PCI-DSS v4.0 Requirement 10: Immutable Audit Logging & Tamper Resistance</p>
                  <p className="text-[#7D8A99] text-[11px]">All administrative approvals and incident containment actions recorded with cryptographic SHA-256 chain.</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-[#22C55E]/15 text-[#22C55E] font-bold">CERTIFIED</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
