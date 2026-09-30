import React, { useState } from 'react';
import { 
  Radar, 
  Globe, 
  Server, 
  AlertTriangle, 
  ShieldCheck, 
  Network, 
  CheckCircle2, 
  RefreshCw,
  HardDrive
} from 'lucide-react';

interface OSINTReconViewProps {
  onNotify?: (msg: string) => void;
}

const PRESET_DOMAINS = [
  { domain: 'ethiotelecom.et', org: 'Ethio Telecom HQ', asn: 'AS24757' },
  { domain: 'combanketh.et', org: 'Commercial Bank of Ethiopia', asn: 'AS24757' },
  { domain: 'insa.gov.et', org: 'Information Network Security Administration', asn: 'AS37059' },
  { domain: 'aau.edu.et', org: 'Addis Ababa University', asn: 'AS24757' },
  { domain: 'safaricom.et', org: 'Safaricom Telecommunications ET', asn: 'AS329340' }
];

export const OSINTReconView: React.FC<OSINTReconViewProps> = () => {
  const [target, setTarget] = useState('ethiotelecom.et');
  const [activeTarget, setActiveTarget] = useState('ethiotelecom.et');
  const [isScanning, setIsScanning] = useState(false);

  const [scanData, setScanData] = useState({
    target: 'ethiotelecom.et',
    primaryIp: '196.188.120.45',
    asn: 'AS24757',
    asnOrg: 'Ethio Telecom',
    city: 'Addis Ababa',
    country: 'Ethiopia (ET)',
    riskScore: 68,
    riskLevel: 'HIGH',
    dns: {
      a: ['196.188.120.45', '196.188.120.46'],
      mx: ['mail.ethiotelecom.et (Priority 10)', 'backup-mx.ethiotelecom.et (Priority 20)'],
      ns: ['ns1.telecom.net.et', 'ns2.telecom.net.et'],
      txt: 'v=spf1 include:_spf.ethiotelecom.et ~all',
      dmarc: 'v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc-reports@ethiotelecom.et'
    },
    subdomains: [
      { name: 'www.ethiotelecom.et', port: 443, service: 'Public Web Portal', status: 'ACTIVE' },
      { name: 'mail.ethiotelecom.et', port: 443, service: 'Zimbra Webmail', status: 'ACTIVE' },
      { name: 'vpn.ethiotelecom.et', port: 443, service: 'Cisco AnyConnect Gateway', status: 'ACTIVE' },
      { name: 'api.ethiotelecom.et', port: 443, service: 'Partner API Gateway', status: 'ACTIVE' },
      { name: 'telebirr.ethiotelecom.et', port: 443, service: 'Telebirr Core Hub', status: 'ACTIVE' },
      { name: 'staging.ethiotelecom.et', port: 8080, service: 'Development Staging Console', status: 'SUSPICIOUS' }
    ],
    ports: [
      { port: 80, proto: 'TCP', service: 'HTTP', risk: 'LOW', desc: 'Standard HTTP web server (Redirects to HTTPS).' },
      { port: 443, proto: 'TCP', service: 'HTTPS', risk: 'LOW', desc: 'SSL/TLS secure portal.' },
      { port: 22, proto: 'TCP', service: 'SSH', risk: 'LOW', desc: 'OpenSSH daemon (Strict pubkey enforced).' },
      { port: 8080, proto: 'TCP', service: 'HTTP-Alt', risk: 'MEDIUM', desc: 'Staging web console exposed to WAN.' },
      { port: 3389, proto: 'TCP', service: 'RDP', risk: 'CRITICAL', desc: 'Remote Desktop Protocol open to public internet on staging host.' }
    ],
    ssl: {
      issuer: "Let's Encrypt Authority X3",
      protocol: 'TLSv1.3',
      cipher: 'TLS_AES_256_GCM_SHA384',
      validUntil: '2026-10-15',
      daysLeft: 197,
      hsts: true,
      grade: 'A+'
    },
    hardening: [
      'Immediately restrict WAN access to RDP Port 3389; enforce access strictly over corporate VPN.',
      'Hide or whitelist IP access to port 8080 development staging console.',
      'Implement strict Content-Security-Policy (CSP) headers across all customer login portals.',
      'Monitor Certificate Transparency logs for unauthorized wild-card subdomains.'
    ]
  });

  const handleExecuteScan = (domainToScan: string) => {
    setIsScanning(true);
    setActiveTarget(domainToScan);
    setTimeout(() => {
      setIsScanning(false);
      const isGov = domainToScan.includes('gov') || domainToScan.includes('insa');
      const isBank = domainToScan.includes('bank');

      setScanData({
        target: domainToScan,
        primaryIp: isGov ? '196.188.10.2' : isBank ? '197.156.70.1' : '196.188.120.45',
        asn: isGov ? 'AS37059' : 'AS24757',
        asnOrg: isGov ? 'INSA National Cyber Infrastructure' : isBank ? 'Commercial Bank of Ethiopia Datacenter' : 'Ethio Telecom',
        city: 'Addis Ababa',
        country: 'Ethiopia (ET)',
        riskScore: isGov ? 32 : isBank ? 55 : 68,
        riskLevel: isGov ? 'LOW' : isBank ? 'MODERATE' : 'HIGH',
        dns: {
          a: [isGov ? '196.188.10.2' : '197.156.70.1'],
          mx: [`mail.${domainToScan} (Priority 10)`],
          ns: [`ns1.${domainToScan}`, `ns2.${domainToScan}`],
          txt: `v=spf1 include:_spf.${domainToScan} ~all`,
          dmarc: `v=DMARC1; p=reject; pct=100; rua=mailto:secops@${domainToScan}`
        },
        subdomains: [
          { name: `www.${domainToScan}`, port: 443, service: 'Primary Web Service', status: 'ACTIVE' },
          { name: `mail.${domainToScan}`, port: 443, service: 'Enterprise Mail', status: 'ACTIVE' },
          { name: `portal.${domainToScan}`, port: 443, service: 'Staff Single Sign-On', status: 'ACTIVE' },
          { name: `vpn.${domainToScan}`, port: 443, service: 'Corporate VPN Gateway', status: 'ACTIVE' }
        ],
        ports: [
          { port: 80, proto: 'TCP', service: 'HTTP', risk: 'LOW', desc: 'Port 80 redirect to 443.' },
          { port: 443, proto: 'TCP', service: 'HTTPS', risk: 'LOW', desc: 'TLSv1.3 hardened endpoint.' },
          { port: 22, proto: 'TCP', service: 'SSH', risk: 'LOW', desc: 'Secure shell port.' }
        ],
        ssl: {
          issuer: 'DigiCert Global Root G2',
          protocol: 'TLSv1.3',
          cipher: 'TLS_AES_256_GCM_SHA384',
          validUntil: '2026-11-20',
          daysLeft: 233,
          hsts: true,
          grade: 'A+'
        },
        hardening: [
          'Enforce Multi-Factor Authentication (MFA) on the external VPN portal.',
          'Verify SPF/DMARC strict reject enforcement across all subsidiary domains.',
          'Schedule periodic external automated vulnerability scanning with ETHIO-CYBERGUARD.'
        ]
      });
    }, 700);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1E2A38] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#00D9FF]/20 text-[#00D9FF] uppercase tracking-wider">
              SpiderFoot + Sherlock Engine
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#22C55E]/20 text-[#22C55E] uppercase tracking-wider">
              National Infrastructure OSINT
            </span>
          </div>
          <h1 className="text-xl font-bold text-white mt-1">Attack Surface & OSINT Reconnaissance</h1>
          <p className="text-xs text-[#7D8A99]">
            Automated perimeter mapping: DNS topology, SSL/TLS certificate health, open ports, and ASN routing for Ethiopian digital assets
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="Target domain or IP..."
            className="bg-[#111923] border border-[#1E2A38] rounded-lg px-3 py-2 text-xs text-white placeholder-[#7D8A99] focus:outline-none focus:border-[#00D9FF] w-52 font-mono"
          />
          <button
            onClick={() => handleExecuteScan(target)}
            disabled={isScanning}
            className="flex items-center space-x-1.5 px-4 py-2 bg-[#00D9FF] hover:bg-[#00B8D9] text-black font-bold text-xs rounded-lg transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
            <span>Scan Surface</span>
          </button>
        </div>
      </div>

      {/* Preset Target Selector */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
        <div className="text-xs font-bold text-white mb-2 flex items-center space-x-2">
          <Radar className="w-4 h-4 text-[#00D9FF]" />
          <span>Quick Recon Targets</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
          {PRESET_DOMAINS.map((p) => (
            <button
              key={p.domain}
              onClick={() => {
                setTarget(p.domain);
                handleExecuteScan(p.domain);
              }}
              className={`p-2.5 rounded-lg text-left border transition-all text-xs cursor-pointer ${
                activeTarget === p.domain
                  ? 'border-[#00D9FF] bg-[#00D9FF]/10 text-white'
                  : 'border-[#1E2A38] bg-[#0D131C] text-[#7D8A99] hover:text-[#E6EDF3] hover:border-[#2C3E50]'
              }`}
            >
              <div className="font-bold text-white font-mono text-[12px] truncate">{p.domain}</div>
              <div className="text-[10px] text-[#7D8A99] truncate mt-0.5">{p.org}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Top Banner: ASN & Risk Index */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">ATTACK SURFACE RISK</div>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className={`text-3xl font-black font-mono ${
              scanData.riskScore >= 70 ? 'text-[#FF1744]' : scanData.riskScore >= 40 ? 'text-[#F59E0B]' : 'text-[#22C55E]'
            }`}>
              {scanData.riskScore}
            </span>
            <span className="text-xs text-[#7D8A99]">/ 100</span>
          </div>
          <div className="text-[10px] text-[#FF1744] mt-1 font-bold">{scanData.riskLevel} EXPOSURE</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">PRIMARY HOST IP</div>
          <div className="text-xl font-bold text-white mt-1 font-mono">{scanData.primaryIp}</div>
          <div className="text-[10px] text-[#00D9FF] mt-1 flex items-center">
            <Globe className="w-3 h-3 mr-1" />
            <span>{scanData.city}, {scanData.country}</span>
          </div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">AUTONOMOUS SYSTEM (ASN)</div>
          <div className="text-xl font-bold text-white mt-1 font-mono">{scanData.asn}</div>
          <div className="text-[10px] text-[#7D8A99] truncate mt-1">{scanData.asnOrg}</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">SSL/TLS HEALTH</div>
          <div className="text-xl font-bold text-[#22C55E] mt-1 flex items-center">
            <CheckCircle2 className="w-4 h-4 mr-1.5" />
            <span>Grade {scanData.ssl.grade}</span>
          </div>
          <div className="text-[10px] text-[#7D8A99] mt-1">{scanData.ssl.daysLeft} days until renewal</div>
        </div>
      </div>

      {/* Main Grid: Subdomains & Exposed Ports */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Discovered Subdomains */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-bold text-white flex items-center space-x-2">
              <Network className="w-4 h-4 text-[#00D9FF]" />
              <span>Discovered Subdomain Infrastructure ({scanData.subdomains.length})</span>
            </span>
            <span className="text-[10px] text-[#00D9FF] font-bold">Passive DNS Recon</span>
          </div>

          <div className="divide-y divide-[#1E2A38] font-mono text-xs">
            {scanData.subdomains.map((sub, i) => (
              <div key={i} className="py-2.5 flex justify-between items-center">
                <div>
                  <div className="text-white font-bold">{sub.name}</div>
                  <div className="text-[11px] text-[#7D8A99] font-sans">{sub.service} (Port {sub.port})</div>
                </div>
                <span className={`text-[10px] px-2 py-0.5 rounded font-sans font-bold ${
                  sub.status === 'ACTIVE' ? 'bg-[#22C55E]/20 text-[#22C55E]' : 'bg-[#FF1744]/20 text-[#FF1744]'
                }`}>
                  {sub.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Exposed Ports & Services */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-bold text-white flex items-center space-x-2">
              <Server className="w-4 h-4 text-[#F59E0B]" />
              <span>Port Exposure & Service Profiling</span>
            </span>
            <span className="text-[10px] text-[#7D8A99]">SYN Scanner</span>
          </div>

          <div className="space-y-2">
            {scanData.ports.map((p, i) => (
              <div key={i} className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg text-xs flex justify-between items-center">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-white">Port {p.port}/{p.proto}</span>
                    <span className="text-[#00D9FF] font-bold">({p.service})</span>
                  </div>
                  <div className="text-[#7D8A99] text-[11px] mt-0.5">{p.desc}</div>
                </div>
                <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                  p.risk === 'CRITICAL' ? 'bg-[#FF1744]/20 text-[#FF1744]' :
                  p.risk === 'MEDIUM' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' : 'bg-[#22C55E]/20 text-[#22C55E]'
                }`}>
                  {p.risk}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* DNS Topology & Hardening Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* DNS Topology */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3">
          <div className="text-sm font-bold text-white flex items-center space-x-2">
            <HardDrive className="w-4 h-4 text-[#00D9FF]" />
            <span>DNS Topology & Security Records</span>
          </div>
          <div className="space-y-2 text-xs font-mono">
            <div className="p-2.5 bg-[#0D131C] rounded border border-[#1E2A38]">
              <span className="text-[#7D8A99] block text-[10px] uppercase font-bold font-sans">A Records</span>
              <span className="text-white">{scanData.dns.a.join(', ')}</span>
            </div>
            <div className="p-2.5 bg-[#0D131C] rounded border border-[#1E2A38]">
              <span className="text-[#7D8A99] block text-[10px] uppercase font-bold font-sans">MX Mail Exchangers</span>
              <span className="text-white">{scanData.dns.mx.join(' • ')}</span>
            </div>
            <div className="p-2.5 bg-[#0D131C] rounded border border-[#1E2A38]">
              <span className="text-[#7D8A99] block text-[10px] uppercase font-bold font-sans">SPF Authentication</span>
              <span className="text-[#22C55E]">{scanData.dns.txt}</span>
            </div>
            <div className="p-2.5 bg-[#0D131C] rounded border border-[#1E2A38]">
              <span className="text-[#7D8A99] block text-[10px] uppercase font-bold font-sans">DMARC Policy</span>
              <span className="text-[#00D9FF]">{scanData.dns.dmarc}</span>
            </div>
          </div>
        </div>

        {/* Hardening Recommendations */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3">
          <div className="text-sm font-bold text-white flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-[#22C55E]" />
            <span>Hardening & Remediation Playbook</span>
          </div>
          <div className="space-y-2">
            {scanData.hardening.map((item, idx) => (
              <div key={idx} className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg text-xs flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 text-[#F59E0B] shrink-0 mt-0.5" />
                <span className="text-[#E6EDF3]">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
