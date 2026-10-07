import React, { useState } from 'react';
import { Shield, Radio, RefreshCw } from 'lucide-react';
import { soundManager } from '../utils/sound';

export interface RegionalNode {
  id: string;
  name: string;
  region: string;
  type: 'Financial Core' | 'Telecom Gateway' | 'National Cyber Command' | 'Academic / Data Center' | 'Regional Hub';
  status: 'OPTIMAL' | 'ELEVATED_THREAT' | 'SCRUBBING_DDOS';
  ipRange: string;
  asn: string;
  throughput: string;
  latencyMs: number;
  activeAttacksCount: number;
  coords: { x: number; y: number }; // Percentage relative to SVG container
}

export const ETHIOPIAN_NODES: RegionalNode[] = [
  {
    id: 'node-cbe-hq',
    name: 'CBE Financial Core Tower',
    region: 'Addis Ababa (Financial District)',
    type: 'Financial Core',
    status: 'ELEVATED_THREAT',
    ipRange: '197.156.70.0/24',
    asn: 'AS24757',
    throughput: '14.2 Gbps',
    latencyMs: 1.2,
    activeAttacksCount: 2,
    coords: { x: 50, y: 46 }
  },
  {
    id: 'node-insa-hq',
    name: 'INSA Cyber Operations Center',
    region: 'Addis Ababa (Goro Command)',
    type: 'National Cyber Command',
    status: 'OPTIMAL',
    ipRange: '196.188.0.0/20',
    asn: 'AS37059',
    throughput: '38.4 Gbps',
    latencyMs: 0.8,
    activeAttacksCount: 0,
    coords: { x: 52, y: 44 }
  },
  {
    id: 'node-ethio-tel',
    name: 'Ethio Telecom Central Gateway',
    region: 'Addis Ababa (Churchill Rd)',
    type: 'Telecom Gateway',
    status: 'SCRUBBING_DDOS',
    ipRange: '213.55.64.0/19',
    asn: 'AS24757',
    throughput: '82.6 Gbps',
    latencyMs: 1.9,
    activeAttacksCount: 5,
    coords: { x: 48, y: 45 }
  },
  {
    id: 'node-hawassa',
    name: 'Hawassa Industrial & Financial Node',
    region: 'Sidama Regional State',
    type: 'Regional Hub',
    status: 'OPTIMAL',
    ipRange: '197.156.92.0/24',
    asn: 'AS24757',
    throughput: '6.4 Gbps',
    latencyMs: 8.4,
    activeAttacksCount: 0,
    coords: { x: 49, y: 68 }
  },
  {
    id: 'node-diredawa',
    name: 'Dire Dawa Transit Gateway',
    region: 'Eastern Commercial Corridor',
    type: 'Regional Hub',
    status: 'OPTIMAL',
    ipRange: '197.156.110.0/24',
    asn: 'AS24757',
    throughput: '8.1 Gbps',
    latencyMs: 12.1,
    activeAttacksCount: 1,
    coords: { x: 74, y: 42 }
  },
  {
    id: 'node-bahirdar',
    name: 'Bahir Dar Operations Hub',
    region: 'Amhara Regional State',
    type: 'Regional Hub',
    status: 'OPTIMAL',
    ipRange: '197.156.84.0/24',
    asn: 'AS24757',
    throughput: '5.2 Gbps',
    latencyMs: 10.6,
    activeAttacksCount: 0,
    coords: { x: 38, y: 28 }
  },
  {
    id: 'node-adama',
    name: 'Adama Payment Switch Exchange',
    region: 'Oromia Regional State',
    type: 'Financial Core',
    status: 'OPTIMAL',
    ipRange: '197.156.78.0/24',
    asn: 'AS24757',
    throughput: '9.8 Gbps',
    latencyMs: 4.1,
    activeAttacksCount: 0,
    coords: { x: 58, y: 50 }
  }
];

export const EthiopiaCyberRadar: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<RegionalNode>(ETHIOPIAN_NODES[0]);
  const [isScanning, setIsScanning] = useState(false);

  const handleNodeClick = (node: RegionalNode) => {
    setSelectedNode(node);
    soundManager.playClick();
  };

  const triggerDiagnosticSweep = () => {
    setIsScanning(true);
    soundManager.playAlert();
    setTimeout(() => {
      setIsScanning(false);
      soundManager.playSuccess();
    }, 1200);
  };

  return (
    <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 relative overflow-hidden">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-4 mb-4 border-b border-[#1E2A38] gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <Radio className="w-4 h-4 text-[#00D9FF] animate-pulse" />
            <h2 className="text-sm font-bold text-white tracking-wide">
              Ethiopian Critical Infrastructure Defense Radar
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
              LIVE GRID
            </span>
          </div>
          <p className="text-xs text-[#7D8A99] mt-0.5">
            Real-time telemetry feeds from banking networks, telecom backbones, and government data centers
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={triggerDiagnosticSweep}
            disabled={isScanning}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/30 hover:bg-[#00D9FF]/20 text-xs font-mono transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
            <span>{isScanning ? 'SWEEPING RADAR...' : 'DIAGNOSTIC SWEEP'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
        {/* Interactive Tactical Radar Visualization (Left 7 cols) */}
        <div className="lg:col-span-7 h-72 sm:h-84 bg-[#070B12] border border-[#1E2A38] rounded-xl relative flex items-center justify-center p-2 overflow-hidden shadow-inner">
          {/* Background Polar Coordinate Rings */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
            <div className="w-64 h-64 border border-[#00D9FF] rounded-full"></div>
            <div className="w-48 h-48 border border-[#00D9FF] rounded-full absolute"></div>
            <div className="w-32 h-32 border border-[#00D9FF] rounded-full absolute"></div>
            <div className="w-16 h-16 border border-[#00D9FF] rounded-full absolute"></div>
            <div className="w-full h-px bg-[#00D9FF] absolute"></div>
            <div className="h-full w-px bg-[#00D9FF] absolute"></div>
          </div>

          {/* Sweeping Radar Scanner Line */}
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            <div className="w-64 h-64 rounded-full relative overflow-hidden">
              <div 
                className="absolute inset-0 origin-center animate-spin"
                style={{
                  animationDuration: '6s',
                  background: 'conic-gradient(from 0deg, transparent 0deg, transparent 310deg, rgba(0, 217, 255, 0.25) 360deg)'
                }}
              ></div>
            </div>
          </div>

          {/* SVG Connector Lines from Addis Ababa to Regional Nodes */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {ETHIOPIAN_NODES.filter(n => n.id !== 'node-cbe-hq').map(node => (
              <line
                key={`line-${node.id}`}
                x1="50%"
                y1="46%"
                x2={`${node.coords.x}%`}
                y2={`${node.coords.y}%`}
                stroke={node.status === 'SCRUBBING_DDOS' ? '#F59E0B' : node.status === 'ELEVATED_THREAT' ? '#FF1744' : '#00D9FF'}
                strokeWidth="1.2"
                strokeDasharray="3 3"
                opacity="0.4"
              />
            ))}
          </svg>

          {/* Infrastructure Nodes on Grid */}
          {ETHIOPIAN_NODES.map((node) => {
            const isSelected = selectedNode.id === node.id;
            return (
              <div
                key={node.id}
                onClick={() => handleNodeClick(node)}
                style={{ left: `${node.coords.x}%`, top: `${node.coords.y}%` }}
                className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
              >
                {/* Pulsing Beacon Ring */}
                <div className={`relative flex items-center justify-center`}>
                  <span className={`animate-ping absolute inline-flex h-5 w-5 rounded-full opacity-75 ${
                    node.status === 'SCRUBBING_DDOS' ? 'bg-[#F59E0B]' :
                    node.status === 'ELEVATED_THREAT' ? 'bg-[#FF1744]' : 'bg-[#00D9FF]'
                  }`}></span>
                  
                  <span className={`relative inline-flex rounded-full h-3.5 w-3.5 border-2 border-black ${
                    node.status === 'SCRUBBING_DDOS' ? 'bg-[#F59E0B]' :
                    node.status === 'ELEVATED_THREAT' ? 'bg-[#FF1744]' : 'bg-[#00D9FF]'
                  } ${isSelected ? 'ring-2 ring-white scale-125' : ''}`}></span>
                </div>

                {/* Node Label Tooltip */}
                <div className={`absolute top-5 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded text-[10px] font-mono whitespace-nowrap border pointer-events-none transition ${
                  isSelected 
                    ? 'bg-[#00D9FF] text-black font-bold border-white' 
                    : 'bg-[#0D131C]/90 text-white border-[#1E2A38] opacity-75 group-hover:opacity-100'
                }`}>
                  {node.name.split(' ')[0]}
                </div>
              </div>
            );
          })}

          {/* Compass Rose Coordinates */}
          <div className="absolute bottom-2 left-3 text-[10px] font-mono text-[#7D8A99]">
            GEO: 9.0300° N, 38.7400° E • ADDIS ABABA ROOT
          </div>
          <div className="absolute top-2 right-3 text-[10px] font-mono text-[#00D9FF]">
            DEFCON 2 • ACTIVE SURVEILLANCE
          </div>
        </div>

        {/* Selected Node Telemetry Dossier (Right 5 cols) */}
        <div className="lg:col-span-5 bg-[#0D131C] border border-[#1E2A38] rounded-xl p-4 flex flex-col justify-between h-full min-h-[280px]">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-[#7D8A99] uppercase tracking-wider">
                NODE TELEMETRY DOSSIER
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${
                selectedNode.status === 'SCRUBBING_DDOS' 
                  ? 'bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30' 
                  : selectedNode.status === 'ELEVATED_THREAT'
                  ? 'bg-[#FF1744]/15 text-[#FF1744] border-[#FF1744]/30'
                  : 'bg-[#22C55E]/15 text-[#22C55E] border-[#22C55E]/30'
              }`}>
                {selectedNode.status.replace('_', ' ')}
              </span>
            </div>

            <h3 className="text-base font-bold text-white mb-1 flex items-center space-x-2">
              <Shield className="w-4 h-4 text-[#00D9FF]" />
              <span>{selectedNode.name}</span>
            </h3>
            <p className="text-xs text-[#7D8A99] mb-4">{selectedNode.region}</p>

            <div className="grid grid-cols-2 gap-3 text-xs mb-4">
              <div className="p-2.5 bg-[#111923] rounded-lg border border-[#1E2A38]">
                <span className="text-[10px] text-[#7D8A99] block font-mono">ASN & CIDR</span>
                <span className="text-white font-mono font-semibold">{selectedNode.asn}</span>
                <span className="text-[10px] text-[#00D9FF] block font-mono mt-0.5">{selectedNode.ipRange}</span>
              </div>

              <div className="p-2.5 bg-[#111923] rounded-lg border border-[#1E2A38]">
                <span className="text-[10px] text-[#7D8A99] block font-mono">BACKBONE THROUGHPUT</span>
                <span className="text-white font-mono font-semibold">{selectedNode.throughput}</span>
                <span className="text-[10px] text-[#22C55E] block font-mono mt-0.5">{selectedNode.latencyMs} ms latency</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-[#7D8A99]">Active Threat Ingress:</span>
                <span className={`font-mono font-bold ${selectedNode.activeAttacksCount > 0 ? 'text-[#FF1744]' : 'text-[#22C55E]'}`}>
                  {selectedNode.activeAttacksCount} Active Probes
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-[#7D8A99]">BGP Peering Link:</span>
                <span className="text-white font-mono">Carrier Interconnect 100G</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-[#7D8A99]">Firewall Mitigation State:</span>
                <span className="text-[#00D9FF] font-mono">Fortinet Cluster Synced</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-[#1E2A38] mt-3 flex items-center justify-between text-xs">
            <span className="text-[#7D8A99] text-[11px]">INSA Compliance: Certified</span>
            <button 
              onClick={() => {
                soundManager.playLockAction();
                alert(`Security audit report generated for ${selectedNode.name}.`);
              }}
              className="text-[#00D9FF] hover:underline font-semibold text-[11px] flex items-center space-x-1"
            >
              <span>Download Node Audit →</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
