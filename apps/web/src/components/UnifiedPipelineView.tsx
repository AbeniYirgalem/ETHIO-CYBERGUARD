import React, { useState } from 'react';
import { 
  GitMerge, 
  Play, 
  CheckCircle2, 
  ShieldAlert, 
  Binary, 
  Bot, 
  Lock, 
  FileText, 
  ArrowRight, 
  CheckSquare, 
  Fingerprint,
  RefreshCw
} from 'lucide-react';

interface UnifiedPipelineViewProps {
  onNotify?: (msg: string) => void;
}

export const UnifiedPipelineView: React.FC<UnifiedPipelineViewProps> = () => {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [selectedSubTab, setSelectedSubTab] = useState<'graph' | 'ecs' | 'evidence' | 'ai' | 'soar' | 'audit'>('graph');
  const [approvedActions, setApprovedActions] = useState<Record<string, boolean>>({});

  const PIPELINE_STEPS = [
    { id: 1, title: 'Event Ingestion', desc: 'Email / Endpoint / Network source received', icon: FileText, color: 'text-[#00D9FF]' },
    { id: 2, title: 'ECS Normalization', desc: 'Mapped to canonical Elastic Common Schema', icon: Binary, color: 'text-[#22C55E]' },
    { id: 3, title: 'SIGMA Detection', desc: 'Matched Rule SIGMA-EML-001 (T1566.002)', icon: ShieldAlert, color: 'text-[#F59E0B]' },
    { id: 4, title: 'Graph Correlation', desc: 'Common Security Graph linked User + Asset + IOC', icon: GitMerge, color: 'text-[#00D9FF]' },
    { id: 5, title: '7 AI Agents Layer', desc: 'Root cause analysis with Evidence Grounding', icon: Bot, color: 'text-[#FF1744]' },
    { id: 6, title: 'Dual-Custody SOAR', desc: 'Host isolation & IP block pending analyst review', icon: CheckSquare, color: 'text-[#F59E0B]' },
    { id: 7, title: 'Immutable Audit', desc: 'Cryptographic SHA256 checksum recorded', icon: Lock, color: 'text-[#22C55E]' }
  ];

  const handleRunFullChain = () => {
    setIsRunning(true);
    setActiveStep(1);
    const interval = setInterval(() => {
      setActiveStep(prev => {
        if (prev >= 7) {
          clearInterval(interval);
          setIsRunning(false);
          return 7;
        }
        return prev + 1;
      });
    }, 700);
  };

  const handleApproveAction = (actionId: string) => {
    setApprovedActions(prev => ({ ...prev, [actionId]: true }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1E2A38] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#00D9FF]/20 text-[#00D9FF] uppercase tracking-wider">
              Common Security Graph Engine
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#22C55E]/20 text-[#22C55E] uppercase tracking-wider">
              Unified Vertical Slice
            </span>
          </div>
          <h1 className="text-xl font-bold text-white mt-1">Unified Security Pipeline & Attack Graph</h1>
          <p className="text-xs text-[#7D8A99]">
            The unified workflow where every capability feeds the same: Event → Evidence → Alert → Incident → 7 AI Agents → SOAR Response → Audit Trail
          </p>
        </div>

        <button
          onClick={handleRunFullChain}
          disabled={isRunning}
          className="flex items-center space-x-2 px-5 py-2.5 bg-[#00D9FF] hover:bg-[#00B8D9] text-black font-bold text-xs rounded-lg transition-all shadow-lg shadow-[#00D9FF]/10 cursor-pointer disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Executing Pipeline Step {activeStep}/7...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute End-to-End Vertical Slice</span>
            </>
          )}
        </button>
      </div>

      {/* Pipeline Stepper Progression Banner */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
        <div className="text-xs font-bold text-white mb-4 flex items-center justify-between">
          <span>7-Stage Pipeline Lifecycle Progression</span>
          <span className="text-[11px] text-[#00D9FF] font-mono">
            {activeStep === 0 ? 'Ready to execute' : activeStep === 7 ? 'Pipeline Completed (100%)' : `Executing Stage ${activeStep} of 7...`}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
          {PIPELINE_STEPS.map((step) => {
            const Icon = step.icon;
            const isCompleted = activeStep >= step.id;
            const isCurrent = activeStep === step.id;

            return (
              <div 
                key={step.id} 
                className={`p-3 rounded-lg border text-left transition-all ${
                  isCurrent 
                    ? 'border-[#00D9FF] bg-[#00D9FF]/10 ring-1 ring-[#00D9FF]' 
                    : isCompleted 
                    ? 'border-[#22C55E]/40 bg-[#0D131C]' 
                    : 'border-[#1E2A38] bg-[#070B12] opacity-60'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono font-bold text-[#7D8A99]">STEP 0{step.id}</span>
                  {isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#22C55E]" />
                  ) : (
                    <Icon className={`w-3.5 h-3.5 ${step.color}`} />
                  )}
                </div>
                <div className="font-bold text-white text-[12px] truncate">{step.title}</div>
                <div className="text-[10px] text-[#7D8A99] line-clamp-2 mt-0.5">{step.desc}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sub-Tabs: Graph, ECS Event, Evidence Trail, AI Investigation, SOAR, Audit */}
      <div className="flex items-center space-x-1 border-b border-[#1E2A38] pb-1 overflow-x-auto text-xs">
        <button
          onClick={() => setSelectedSubTab('graph')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'graph' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Common Security Graph
        </button>
        <button
          onClick={() => setSelectedSubTab('ecs')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'ecs' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Canonical ECS Event
        </button>
        <button
          onClick={() => setSelectedSubTab('evidence')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'evidence' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Evidence Grounding (EV-001)
        </button>
        <button
          onClick={() => setSelectedSubTab('ai')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'ai' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          7 AI Agents Synthesis
        </button>
        <button
          onClick={() => setSelectedSubTab('soar')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'soar' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Dual-Custody SOAR Response
        </button>
        <button
          onClick={() => setSelectedSubTab('audit')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'audit' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Tamper-Proof Audit Record
        </button>
      </div>

      {/* Tab 1: Common Security Graph */}
      {selectedSubTab === 'graph' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm font-bold text-white">Unified Attack Correlation Graph (INC-00042)</div>
              <div className="text-xs text-[#7D8A99]">Correlating entities across Inbound Email → Extracted URL → Endpoint → Perimeter Gateway</div>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#FF1744]/20 text-[#FF1744] font-bold">
              Multi-Stage Attack Chain
            </span>
          </div>

          {/* ASCII / Visual Graph Map */}
          <div className="p-6 bg-[#070B12] border border-[#1E2A38] rounded-xl flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs overflow-x-auto">
            <div className="p-3 bg-[#0D131C] border border-[#FF1744]/50 rounded-lg text-center w-48">
              <span className="text-[10px] text-[#FF1744] font-bold uppercase block">INBOUND EMAIL</span>
              <span className="text-white font-bold block mt-1">telebirr-bonus.xyz</span>
              <span className="text-[#7D8A99] text-[10px]">SPF: FAIL • DKIM: FAIL</span>
            </div>

            <ArrowRight className="w-5 h-5 text-[#00D9FF] shrink-0" />

            <div className="p-3 bg-[#0D131C] border border-[#F59E0B]/50 rounded-lg text-center w-48">
              <span className="text-[10px] text-[#F59E0B] font-bold uppercase block">TARGETED USER</span>
              <span className="text-white font-bold block mt-1">dawit.mengistu</span>
              <span className="text-[#7D8A99] text-[10px]">Finance Dept • High Privilege</span>
            </div>

            <ArrowRight className="w-5 h-5 text-[#00D9FF] shrink-0" />

            <div className="p-3 bg-[#0D131C] border border-[#00D9FF]/50 rounded-lg text-center w-48">
              <span className="text-[10px] text-[#00D9FF] font-bold uppercase block">PRIMARY ASSET</span>
              <span className="text-white font-bold block mt-1">SERVER-04 (10.10.1.24)</span>
              <span className="text-[#7D8A99] text-[10px]">Core Banking Infrastructure</span>
            </div>

            <ArrowRight className="w-5 h-5 text-[#00D9FF] shrink-0" />

            <div className="p-3 bg-[#0D131C] border border-[#FF1744]/50 rounded-lg text-center w-48">
              <span className="text-[10px] text-[#FF1744] font-bold uppercase block">MALICIOUS C2 HOST</span>
              <span className="text-[#FF1744] font-bold block mt-1">185.220.101.5:443</span>
              <span className="text-[#7D8A99] text-[10px]">Cobalt Strike Beacon</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Canonical ECS Event */}
      {selectedSubTab === 'ecs' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3">
          <div className="text-sm font-bold text-white">Canonical Elastic Common Schema (ECS) Representation</div>
          <pre className="p-4 bg-[#070B12] border border-[#1E2A38] rounded-lg text-xs font-mono text-[#00D9FF] overflow-x-auto">
{JSON.stringify({
  "@timestamp": "2026-09-30T10:42:00Z",
  "event": {
    "kind": "alert",
    "category": ["email", "threat_intel"],
    "type": ["phishing_email", "brand_impersonation"],
    "action": "blocked_by_gateway",
    "outcome": "failure"
  },
  "source": {
    "ip": "196.188.99.12",
    "port": 49210,
    "domain": "telebirr-bonus.xyz"
  },
  "destination": {
    "ip": "10.10.1.24",
    "port": 25,
    "user": "dawit.mengistu@cbe.com.et"
  },
  "email": {
    "from": "support@telebirr-bonus.xyz",
    "reply_to": "phisher-collector@gmail.com",
    "subject": "URGENT: ቴሌብር 10,000 ብር የሽልማት አሸናፊ - አሁኑኑ ያረጋግጡ",
    "spf": "fail",
    "dkim": "fail",
    "dmarc": "fail"
  },
  "observables": [
    { "type": "domain", "value": "telebirr-bonus.xyz", "reputation": "MALICIOUS" },
    { "type": "url", "value": "http://196.188.99.12/claim-prize/login.php", "risk_weight": 35 }
  ]
}, null, 2)}
          </pre>
        </div>
      )}

      {/* Tab 3: Evidence Grounding */}
      {selectedSubTab === 'evidence' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="text-sm font-bold text-white">Traceable Evidence Grounding (Zero Hallucination Guarantee)</div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-lg text-xs space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-mono font-bold text-[#00D9FF]">EV-001</span>
                <span className="text-[10px] text-[#22C55E] font-bold">Conf: 99.4%</span>
              </div>
              <div className="font-bold text-white">Cryptographic SPF/DKIM Mismatch</div>
              <p className="text-[#7D8A99] text-[11px]">
                RFC-822 header `Authentication-Results` returned hard failure for sender IP 196.188.99.12 against SPF record.
              </p>
            </div>

            <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-lg text-xs space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-mono font-bold text-[#00D9FF]">EV-002</span>
                <span className="text-[10px] text-[#22C55E] font-bold">Conf: 94.8%</span>
              </div>
              <div className="font-bold text-white">Regional Financial Brand Abuse</div>
              <p className="text-[#7D8A99] text-[11px]">
                NLP regex identified Telebirr brand name in Amharic (`የቴሌብር ሽልማት`) sent from unauthorized foreign domain.
              </p>
            </div>

            <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-lg text-xs space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-mono font-bold text-[#00D9FF]">EV-003</span>
                <span className="text-[10px] text-[#22C55E] font-bold">Conf: 96.2%</span>
              </div>
              <div className="font-bold text-white">Raw IPv4 Egress Beaconing</div>
              <p className="text-[#7D8A99] text-[11px]">
                Network socket telemetry confirmed outbound connection on port 443 to known Cobalt Strike C2 (185.220.101.5).
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: 7 AI Agents Synthesis */}
      {selectedSubTab === 'ai' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3">
          <div className="text-sm font-bold text-white">7 Specialized AI Agents Output Synthesis</div>
          <div className="space-y-2 text-xs">
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <strong className="text-[#00D9FF]">1. Event Analysis Agent:</strong> Deconstructed initial inbound SMTP vector into MITRE ATT&CK technique T1566.002 (Spearphishing Link).
            </div>
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <strong className="text-[#00D9FF]">2. Threat Intelligence Agent:</strong> Cross-referenced extracted C2 IP 185.220.101.5 against Ethio-CERT blacklist (Confirmed 98% malicious).
            </div>
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <strong className="text-[#00D9FF]">3. Correlation Agent:</strong> Linked recipient user dawit.mengistu with SERVER-04 PowerShell execution within a 4-minute time window.
            </div>
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <strong className="text-[#00D9FF]">4. Investigation Agent:</strong> Root cause established: Credential harvesting link clicked from email client, leading to secondary stage delivery.
            </div>
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <strong className="text-[#00D9FF]">5. Risk Assessment Agent:</strong> Asset Criticality (Core Banking +25) + Privileged User (+20) + Malicious IOC (+25) + Brand Spoof (+20) = 92/100 (CRITICAL).
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Dual-Custody SOAR Response */}
      {selectedSubTab === 'soar' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm font-bold text-white">Dual-Custody SOAR Playbook Execution</div>
              <div className="text-xs text-[#7D8A99]">High-impact containment actions require explicit Tier-2 SOC Analyst authorization</div>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#F59E0B]/20 text-[#F59E0B] font-bold">
              Human-In-The-Loop Enforced
            </span>
          </div>

          <div className="space-y-3">
            <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white text-xs">ISOLATE_HOST: SERVER-04 (10.10.1.24)</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#FF1744]/20 text-[#FF1744] font-bold">HIGH RISK</span>
                </div>
                <div className="text-[11px] text-[#7D8A99] mt-0.5">
                  Cuts lateral network propagation while keeping SOC forensic connection alive.
                </div>
              </div>

              {approvedActions['act_isolate'] ? (
                <span className="px-3 py-1.5 rounded bg-[#22C55E]/20 text-[#22C55E] font-bold text-xs flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Approved & Enforced</span>
                </span>
              ) : (
                <button
                  onClick={() => handleApproveAction('act_isolate')}
                  className="px-4 py-2 bg-[#22C55E] hover:bg-[#16A34A] text-black font-bold text-xs rounded-lg transition-all cursor-pointer"
                >
                  Approve Host Isolation
                </button>
              )}
            </div>

            <div className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white text-xs">BLOCK_IP: 185.220.101.5 on Perimeter Gateways</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#00D9FF]/20 text-[#00D9FF] font-bold">LOW RISK</span>
                </div>
                <div className="text-[11px] text-[#7D8A99] mt-0.5">
                  Drops all outbound network beaconing to Cobalt Strike C2 server.
                </div>
              </div>

              {approvedActions['act_block'] ? (
                <span className="px-3 py-1.5 rounded bg-[#22C55E]/20 text-[#22C55E] font-bold text-xs flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Approved & Enforced</span>
                </span>
              ) : (
                <button
                  onClick={() => handleApproveAction('act_block')}
                  className="px-4 py-2 bg-[#22C55E] hover:bg-[#16A34A] text-black font-bold text-xs rounded-lg transition-all cursor-pointer"
                >
                  Approve Perimeter Drop
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 6: Tamper-Proof Audit */}
      {selectedSubTab === 'audit' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3 font-mono text-xs">
          <div className="text-sm font-bold text-white font-sans flex items-center space-x-2">
            <Fingerprint className="w-4 h-4 text-[#22C55E]" />
            <span>Cryptographic Immutable Audit Log Entry</span>
          </div>
          <div className="p-4 bg-[#070B12] border border-[#1E2A38] rounded-lg space-y-2 text-[#E6EDF3]">
            <div><strong>Audit ID:</strong> aud_7f19b2e8a1</div>
            <div><strong>Timestamp:</strong> 2026-09-30T10:42:15.892Z</div>
            <div><strong>Incident Promoted:</strong> INC-00042 (CRITICAL)</div>
            <div><strong>Duty Analyst:</strong> Dawit Mengistu (ID: SEC-ETH-04)</div>
            <div><strong>Dual-Custody Peer Approver:</strong> Sara Yohannes (ID: SEC-ETH-09)</div>
            <div><strong>SHA256 Checksum:</strong> <span className="text-[#00D9FF]">b74557f489f60126dca93785996abbe178b9cfbc3bd132b0351cbb22a978d183</span></div>
          </div>
        </div>
      )}
    </div>
  );
};
