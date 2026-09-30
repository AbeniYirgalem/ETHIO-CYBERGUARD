import React, { useState } from 'react';
import { Binary, Search } from 'lucide-react';
import type { ThreatIndicator } from '../types';

interface ThreatIntelViewProps {
  indicators: ThreatIndicator[];
}

export const ThreatIntelView: React.FC<ThreatIntelViewProps> = ({ indicators }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [lookupResult, setLookupResult] = useState<ThreatIndicator | null>(null);

  const filtered = indicators.filter(ind => 
    ind.indicator.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ind.threat_actor.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ind.malware.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleQuickLookup = (val: string) => {
    const match = indicators.find(i => i.indicator.toLowerCase() === val.toLowerCase());
    setLookupResult(match || {
      indicator: val,
      type: val.includes('.') ? (val.split('.').length === 4 ? 'IPV4' : 'DOMAIN') : 'SHA256',
      reputation: 'BENIGN',
      confidence: 75,
      first_seen: 'Not found in blacklist',
      threat_actor: 'None recorded',
      malware: 'Clean',
      country: 'Unknown',
      related_incidents: []
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-2 border-b border-[#1E2A38]">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Binary className="w-5 h-5 text-[#00D9FF]" />
            <span>Threat Intelligence Database</span>
          </h1>
          <p className="text-xs text-[#7D8A99]">Aggregated IOC feeds from Ethio-CERT, INSA, and regional financial intelligence exchanges</p>
        </div>

        {/* Live Feed Status */}
        <div className="flex items-center space-x-2 text-xs font-mono bg-[#0D131C] px-3 py-1.5 rounded-lg border border-[#1E2A38] mt-3 sm:mt-0">
          <span className="w-2 h-2 rounded-full bg-[#22C55E]"></span>
          <span className="text-white">Active Feed: Ethio-CERT Sync</span>
        </div>
      </div>

      {/* Lookup Bar */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
        <h2 className="text-sm font-bold text-white mb-2">On-Demand Indicator Lookup</h2>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#7D8A99] absolute left-3 top-2.5" />
            <input 
              type="text" 
              placeholder="Paste IP (e.g. 185.220.101.5), domain, or SHA-256 hash..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#070B12] border border-[#1E2A38] rounded-lg py-2 pl-9 pr-3 text-xs text-white placeholder-[#7D8A99] focus:outline-none focus:border-[#00D9FF]"
            />
          </div>
          <button 
            onClick={() => handleQuickLookup(searchTerm || "185.220.101.5")}
            className="px-4 py-2 bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-bold text-xs rounded-lg transition"
          >
            Investigate IOC
          </button>
        </div>

        {lookupResult && (
          <div className="mt-4 p-4 bg-[#070B12] border border-[#1E2A38] rounded-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-white font-bold text-xs">{lookupResult.indicator}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  lookupResult.reputation === 'MALICIOUS' ? 'bg-[#FF1744]/20 text-[#FF1744]' : 'bg-[#22C55E]/20 text-[#22C55E]'
                }`}>
                  {lookupResult.reputation} • {lookupResult.confidence}% CONFIDENCE
                </span>
              </div>
              <p className="text-xs text-[#7D8A99] mt-1">Actor: {lookupResult.threat_actor} | Malware: {lookupResult.malware} | Origin: {lookupResult.country}</p>
            </div>
            <button 
              onClick={() => setLookupResult(null)}
              className="text-xs text-[#7D8A99] hover:text-white"
            >
              Dismiss
            </button>
          </div>
        )}
      </div>

      {/* Indicator Table */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#1E2A38] flex justify-between items-center">
          <h2 className="text-sm font-bold text-white">Active Verified Threat Indicators</h2>
          <span className="text-[11px] font-mono text-[#7D8A99]">{filtered.length} entries</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0D131C] text-[#7D8A99] uppercase font-mono text-[10px] tracking-wider border-b border-[#1E2A38]">
              <tr>
                <th className="py-2.5 px-4">Indicator Value</th>
                <th className="py-2.5 px-4">Type</th>
                <th className="py-2.5 px-4">Reputation</th>
                <th className="py-2.5 px-4">Threat Actor / Campaign</th>
                <th className="py-2.5 px-4">Malware Family</th>
                <th className="py-2.5 px-4">Geo Origin</th>
                <th className="py-2.5 px-4">Linked Incidents</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2A38] font-mono text-[11px]">
              {filtered.map((ind, i) => (
                <tr key={i} className="hover:bg-[#0D131C]/60 transition">
                  <td className="py-3 px-4 font-bold text-white max-w-xs truncate">{ind.indicator}</td>
                  <td className="py-3 px-4 text-[#00D9FF]">{ind.type}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      ind.reputation === 'MALICIOUS' ? 'bg-[#FF1744]/15 text-[#FF1744] border border-[#FF1744]/30' :
                      ind.reputation === 'SUSPICIOUS' ? 'bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/30' :
                      'bg-[#22C55E]/15 text-[#22C55E]'
                    }`}>
                      {ind.reputation} ({ind.confidence}%)
                    </span>
                  </td>
                  <td className="py-3 px-4 text-[#E6EDF3] font-sans">{ind.threat_actor}</td>
                  <td className="py-3 px-4 text-[#7D8A99] font-sans">{ind.malware}</td>
                  <td className="py-3 px-4 text-[#7D8A99] font-sans">{ind.country}</td>
                  <td className="py-3 px-4">
                    <div className="flex space-x-1">
                      {ind.related_incidents.map((rel, rIdx) => (
                        <span key={rIdx} className="px-1.5 py-0.2 rounded bg-[#00D9FF]/10 text-[#00D9FF] text-[10px]">
                          {rel}
                        </span>
                      ))}
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
