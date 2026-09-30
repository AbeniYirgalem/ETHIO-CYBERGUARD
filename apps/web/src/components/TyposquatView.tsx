import React, { useState } from 'react';
import { 
  Search, 
  Globe, 
  AlertTriangle, 
  ShieldAlert, 
  Check, 
  Copy, 
  RefreshCw,
  ShoppingBag
} from 'lucide-react';

interface TyposquatViewProps {
  onNotify?: (msg: string) => void;
}

const PRESET_TARGETS = [
  { domain: 'telebirr.et', brand: 'Telebirr', sector: 'Mobile Money & Digital Payment' },
  { domain: 'combanketh.et', brand: 'Commercial Bank of Ethiopia', sector: 'National Banking' },
  { domain: 'ethiotelecom.et', brand: 'Ethio Telecom', sector: 'Telecommunications' },
  { domain: 'insa.gov.et', brand: 'INSA Cyber Security', sector: 'Government & Defense' },
  { domain: 'chapa.co', brand: 'Chapa Financial', sector: 'Fintech & Payment Gateway' },
  { domain: 'aau.edu.et', brand: 'Addis Ababa University', sector: 'Higher Education' }
];

export const TyposquatView: React.FC<TyposquatViewProps> = () => {
  const [targetInput, setTargetInput] = useState('telebirr.et');
  const [activeBrand, setActiveBrand] = useState('telebirr.et');
  const [filterQuery, setFilterQuery] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [copiedDomain, setCopiedDomain] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Realistic generated mutations
  const [results, setResults] = useState([
    {
      domain: 'te1ebirr.et',
      technique: 'Homoglyph (1 for l)',
      distance: 1,
      similarity: 88.9,
      risk: 'CRITICAL',
      status: 'Active Threat',
      desc: 'Active SMS phishing gateway hosting fake Telebirr OTP harvesting form.',
      recommended: 'Issue immediate Registrar Takedown and blacklist in DNS resolver.'
    },
    {
      domain: 'telebirr-login.com',
      technique: 'Combosquatting (Phishing Lure)',
      distance: 9,
      similarity: 78.4,
      risk: 'CRITICAL',
      status: 'Active Threat',
      desc: 'Credential harvester mimicking official Telebirr web portal.',
      recommended: 'Send UDRP cease-and-desist letter; block outbound traffic.'
    },
    {
      domain: 'telebir.et',
      technique: 'Omission Squatting',
      distance: 1,
      similarity: 87.5,
      risk: 'HIGH',
      status: 'Registered / Parked',
      desc: 'Registered via foreign registrar; parking page displaying ads.',
      recommended: 'Monitor daily for DNS A-record changes.'
    },
    {
      domain: 'telebirr-verify.net',
      technique: 'Combosquatting (Prefix/Suffix)',
      distance: 10,
      similarity: 72.0,
      risk: 'HIGH',
      status: 'Registered / Parked',
      desc: 'Recently registered domain in Seychelles; no MX record currently.',
      recommended: 'Submit proactive abuse report.'
    },
    {
      domain: 'telebirr.xyz',
      technique: 'TLD Swap (.xyz)',
      distance: 3,
      similarity: 75.0,
      risk: 'HIGH',
      status: 'Active Threat',
      desc: 'Hosting Telegram bot link promising 10,000 Birr lottery bonuses.',
      recommended: 'Add to national CERT threat intelligence feed.'
    },
    {
      domain: 'telebrir.et',
      technique: 'Transposition Squatting',
      distance: 2,
      similarity: 77.8,
      risk: 'MEDIUM',
      status: 'Available for Defensive Purchase',
      desc: 'Unregistered permutation prone to common typing mistakes.',
      recommended: 'Purchase domain defensively at .et registrar ($15/year).'
    },
    {
      domain: 'telebirr.org',
      technique: 'TLD Swap (.org)',
      distance: 3,
      similarity: 75.0,
      risk: 'MEDIUM',
      status: 'Available for Defensive Purchase',
      desc: 'Available for registration on public registrar.',
      recommended: 'Register defensively to protect non-profit brand perception.'
    },
    {
      domain: 'telebirr-support.com',
      technique: 'Combosquatting (Support Lure)',
      distance: 11,
      similarity: 68.2,
      risk: 'HIGH',
      status: 'Registered / Parked',
      desc: 'Registered with WHOIS privacy shield enabled.',
      recommended: 'File trademark infringement claim.'
    },
    {
      domain: 'te1eb1rr.com',
      technique: 'Double Homoglyph',
      distance: 2,
      similarity: 80.0,
      risk: 'CRITICAL',
      status: 'Active Threat',
      desc: 'Directing visitors to credential stealer APK download.',
      recommended: 'Block host IP on perimeter firewalls.'
    }
  ]);

  const handleScan = (domainToScan: string) => {
    setIsScanning(true);
    setActiveBrand(domainToScan);
    setTimeout(() => {
      setIsScanning(false);
      const clean = domainToScan.split('.')[0];
      // Generate dynamic dataset for selected brand
      setResults([
        {
          domain: `${clean}-login.com`,
          technique: 'Combosquatting (Phishing Lure)',
          distance: 9,
          similarity: 82.0,
          risk: 'CRITICAL',
          status: 'Active Threat',
          desc: `Active phishing site impersonating ${domainToScan} authentication endpoint.`,
          recommended: 'Issue immediate Registrar Takedown & blacklist on DNS sinkhole.'
        },
        {
          domain: `${clean.replace('e', '3').replace('o', '0')}.et`,
          technique: 'Homoglyph / Visual Spoof',
          distance: 1,
          similarity: 90.0,
          risk: 'CRITICAL',
          status: 'Active Threat',
          desc: 'High visual similarity spoof targeting mobile users on small screens.',
          recommended: 'Block domain and report to Ethio Telecom CERT.'
        },
        {
          domain: `${clean}.xyz`,
          technique: 'TLD Swap (.xyz)',
          distance: 3,
          similarity: 78.0,
          risk: 'HIGH',
          status: 'Registered / Parked',
          desc: 'Registered under privacy protection on overseas registrar.',
          recommended: 'Monitor for MX record activation.'
        },
        {
          domain: `${clean}verify.net`,
          technique: 'Combosquatting (Lure)',
          distance: 6,
          similarity: 73.0,
          risk: 'HIGH',
          status: 'Registered / Parked',
          desc: 'Inactive DNS records; ready for weaponization.',
          recommended: 'Proactively flag on proxy intelligence.'
        },
        {
          domain: `${clean.slice(0, -1)}.et`,
          technique: 'Omission Squatting',
          distance: 1,
          similarity: 88.5,
          risk: 'MEDIUM',
          status: 'Available for Defensive Purchase',
          desc: 'Frequent typo omission candidate.',
          recommended: 'Register defensively at Ethiopian national registrar.'
        },
        {
          domain: `secure-${clean}.com`,
          technique: 'Combosquatting (Prefix)',
          distance: 7,
          similarity: 70.0,
          risk: 'HIGH',
          status: 'Active Threat',
          desc: 'Hosting fake certificate and SSL credentials lure.',
          recommended: 'Submit domain abuse report to hosting provider.'
        }
      ]);
    }, 600);
  };

  const handleCopy = (dom: string) => {
    navigator.clipboard.writeText(dom);
    setCopiedDomain(dom);
    setTimeout(() => setCopiedDomain(null), 2000);
  };

  const handleTakeAction = (dom: string, action: string) => {
    setActionSuccess(`Action "${action}" queued for domain ${dom}`);
    setTimeout(() => setActionSuccess(null), 3500);
  };

  const filtered = results.filter(r => 
    r.domain.toLowerCase().includes(filterQuery.toLowerCase()) ||
    r.technique.toLowerCase().includes(filterQuery.toLowerCase()) ||
    r.risk.toLowerCase().includes(filterQuery.toLowerCase())
  );

  const criticalCount = results.filter(r => r.risk === 'CRITICAL').length;
  const activeThreatCount = results.filter(r => r.status === 'Active Threat').length;
  const defensiveCount = results.filter(r => r.status.includes('Defensive Purchase')).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1E2A38] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#00D9FF]/20 text-[#00D9FF] uppercase tracking-wider">
              openSquat Engine
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#F59E0B]/20 text-[#F59E0B] uppercase tracking-wider">
              Brand Defense & Anti-Typosquatting
            </span>
          </div>
          <h1 className="text-xl font-bold text-white mt-1">Typosquatting & Look-Alike Domain Monitor</h1>
          <p className="text-xs text-[#7D8A99]">
            Proactive brand protection monitoring homoglyphs, omission squatting, combosquatting, and high-risk TLD variations targeting Ethiopian institutions
          </p>
        </div>

        {/* Search Input */}
        <div className="flex items-center space-x-2">
          <div className="relative">
            <input
              type="text"
              value={targetInput}
              onChange={(e) => setTargetInput(e.target.value)}
              placeholder="e.g. telebirr.et"
              className="bg-[#111923] border border-[#1E2A38] rounded-lg px-3 py-2 text-xs text-white placeholder-[#7D8A99] focus:outline-none focus:border-[#00D9FF] w-48 font-mono"
            />
          </div>
          <button
            onClick={() => handleScan(targetInput)}
            disabled={isScanning}
            className="flex items-center space-x-1.5 px-4 py-2 bg-[#00D9FF] hover:bg-[#00B8D9] text-black font-bold text-xs rounded-lg transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
            <span>Scan Brand</span>
          </button>
        </div>
      </div>

      {actionSuccess && (
        <div className="p-3 bg-[#22C55E]/10 border border-[#22C55E]/30 rounded-lg text-xs text-[#22C55E] flex items-center justify-between">
          <span>{actionSuccess}</span>
          <button onClick={() => setActionSuccess(null)} className="text-[#22C55E] hover:underline">Dismiss</button>
        </div>
      )}

      {/* Preset Target Selector */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
        <div className="text-xs font-bold text-white mb-2 flex items-center space-x-2">
          <Globe className="w-4 h-4 text-[#00D9FF]" />
          <span>Monitored Ethiopian National Brands</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {PRESET_TARGETS.map((t) => (
            <button
              key={t.domain}
              onClick={() => {
                setTargetInput(t.domain);
                handleScan(t.domain);
              }}
              className={`p-2.5 rounded-lg text-left border transition-all text-xs cursor-pointer ${
                activeBrand === t.domain
                  ? 'border-[#00D9FF] bg-[#00D9FF]/10 text-white'
                  : 'border-[#1E2A38] bg-[#0D131C] text-[#7D8A99] hover:text-[#E6EDF3] hover:border-[#2C3E50]'
              }`}
            >
              <div className="font-bold text-white font-mono text-[12px] truncate">{t.domain}</div>
              <div className="text-[10px] text-[#7D8A99] truncate mt-0.5">{t.brand}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">TOTAL MUTATIONS ANALYZED</div>
          <div className="text-2xl font-black text-white mt-1 font-mono">{results.length * 8}</div>
          <div className="text-[10px] text-[#00D9FF] mt-1">Generated via openSquat rules</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">ACTIVE PHISHING THREATS</div>
          <div className="text-2xl font-black text-[#FF1744] mt-1 font-mono">{activeThreatCount}</div>
          <div className="text-[10px] text-[#FF1744] mt-1">Weaponized and live online</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">CRITICAL RISK SQUATTERS</div>
          <div className="text-2xl font-black text-[#F59E0B] mt-1 font-mono">{criticalCount}</div>
          <div className="text-[10px] text-[#F59E0B] mt-1">Similarity score &gt; 80%</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">DEFENSIVE PURCHASE READY</div>
          <div className="text-2xl font-black text-[#22C55E] mt-1 font-mono">{defensiveCount}</div>
          <div className="text-[10px] text-[#22C55E] mt-1">Unregistered look-alikes</div>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="text-sm font-bold text-white flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-[#FF1744]" />
            <span>Look-Alike Permutation Findings for <span className="text-[#00D9FF] font-mono">{activeBrand}</span></span>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-[#7D8A99]" />
            <input
              type="text"
              placeholder="Filter domain or technique..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-[#070B12] border border-[#1E2A38] rounded-lg text-xs text-white placeholder-[#7D8A99] focus:outline-none focus:border-[#00D9FF] w-60"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0D131C] text-[#7D8A99] uppercase text-[10px] tracking-wider border-b border-[#1E2A38]">
              <tr>
                <th className="py-2.5 px-3">Look-Alike Domain</th>
                <th className="py-2.5 px-3">Technique</th>
                <th className="py-2.5 px-3">Levenshtein</th>
                <th className="py-2.5 px-3">Similarity</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">SOC Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2A38]">
              {filtered.map((item) => (
                <tr key={item.domain} className="hover:bg-[#0D131C]/60 transition-colors">
                  <td className="py-3 px-3">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-white font-bold text-[13px]">{item.domain}</span>
                      <button
                        onClick={() => handleCopy(item.domain)}
                        className="text-[#7D8A99] hover:text-[#00D9FF] cursor-pointer"
                        title="Copy domain"
                      >
                        {copiedDomain === item.domain ? <Check className="w-3.5 h-3.5 text-[#22C55E]" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                    <div className="text-[11px] text-[#7D8A99] mt-0.5">{item.desc}</div>
                  </td>
                  <td className="py-3 px-3 text-[#E6EDF3]">
                    <span className="px-2 py-0.5 rounded bg-[#1E2A38] text-[11px]">
                      {item.technique}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-[#E6EDF3]">
                    {item.distance}
                  </td>
                  <td className="py-3 px-3 font-mono">
                    <span className={`font-bold ${item.similarity >= 85 ? 'text-[#FF1744]' : item.similarity >= 75 ? 'text-[#F59E0B]' : 'text-[#22C55E]'}`}>
                      {item.similarity}%
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.risk === 'CRITICAL' ? 'bg-[#FF1744]/20 text-[#FF1744]' :
                      item.risk === 'HIGH' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' : 'bg-[#00D9FF]/20 text-[#00D9FF]'
                    }`}>
                      {item.risk}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className={`text-[11px] font-semibold ${
                      item.status === 'Active Threat' ? 'text-[#FF1744] flex items-center' :
                      item.status.includes('Defensive') ? 'text-[#22C55E]' : 'text-[#7D8A99]'
                    }`}>
                      {item.status === 'Active Threat' && <AlertTriangle className="w-3 h-3 mr-1 text-[#FF1744]" />}
                      {item.status}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <div className="flex items-center justify-end space-x-1.5">
                      {item.status === 'Active Threat' ? (
                        <>
                          <button
                            onClick={() => handleTakeAction(item.domain, 'Takedown Request')}
                            className="px-2 py-1 bg-[#FF1744]/20 hover:bg-[#FF1744]/30 text-[#FF1744] font-bold text-[10px] rounded cursor-pointer transition-all"
                          >
                            Takedown
                          </button>
                          <button
                            onClick={() => handleTakeAction(item.domain, 'DNS Blacklist')}
                            className="px-2 py-1 bg-[#1E2A38] hover:bg-[#2C3E50] text-white text-[10px] rounded cursor-pointer transition-all"
                          >
                            Sinkhole
                          </button>
                        </>
                      ) : item.status.includes('Defensive') ? (
                        <button
                          onClick={() => handleTakeAction(item.domain, 'Defensive Purchase Order')}
                          className="px-2 py-1 bg-[#22C55E]/20 hover:bg-[#22C55E]/30 text-[#22C55E] font-bold text-[10px] rounded cursor-pointer transition-all flex items-center space-x-1"
                        >
                          <ShoppingBag className="w-3 h-3" />
                          <span>Buy Defensively</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => handleTakeAction(item.domain, 'WHOIS Monitor Alert')}
                          className="px-2 py-1 bg-[#1E2A38] hover:bg-[#2C3E50] text-[#7D8A99] hover:text-white text-[10px] rounded cursor-pointer transition-all"
                        >
                          Track WHOIS
                        </button>
                      )}
                    </div>
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
