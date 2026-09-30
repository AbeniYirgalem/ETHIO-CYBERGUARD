import React from 'react';
import { BarChart3, Info } from 'lucide-react';
import type { Incident } from '../types';

interface RiskViewProps {
  currentIncident: Incident;
}

export const RiskView: React.FC<RiskViewProps> = ({ currentIncident }) => {
  const metrics = [
    { label: 'Impact', value: 90, bar: 'w-[90%]', color: 'bg-[#FF1744]' },
    { label: 'Likelihood', value: 87, bar: 'w-[87%]', color: 'bg-[#FF1744]' },
    { label: 'Confidence', value: 94, bar: 'w-[94%]', color: 'bg-[#00D9FF]' },
    { label: 'Exposure', value: 82, bar: 'w-[82%]', color: 'bg-[#F59E0B]' },
  ];

  const breakdown = [
    { factor: 'Privileged user account (administrator) executed script', points: 28, category: 'Identity Risk' },
    { factor: 'Confirmed connection to active Cobalt Strike TeamServer (185.220.101.5)', points: 25, category: 'Threat Intel Match' },
    { factor: 'Asset criticality: Tier-1 Core Banking Server (SERVER-04)', points: 22, category: 'Asset Criticality' },
    { factor: 'Potential lateral movement route into SWIFT financial processing node', points: 17, category: 'Blast Radius' },
  ];

  const totalCalculated = breakdown.reduce((acc, curr) => acc + curr.points, 0);

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b border-[#1E2A38]">
        <h1 className="text-xl font-bold text-white flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-[#00D9FF]" />
          <span>Explainable Risk Assessment Engine</span>
        </h1>
        <p className="text-xs text-[#7D8A99]">Transparent multi-factor risk quantification based on organizational asset impact and threat telemetry</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Risk Score Card */}
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 flex flex-col justify-between text-center">
          <div>
            <span className="text-xs uppercase font-mono text-[#7D8A99] tracking-widest">Aggregate Incident Risk</span>
            <div className="my-4">
              <span className="text-6xl font-black font-mono text-[#FF1744] tracking-tight">{currentIncident.risk_score}</span>
              <span className="text-xs font-mono text-[#7D8A99] block mt-1">/ 100 MAXIMUM</span>
            </div>
            <div className="inline-block px-3 py-1 rounded bg-[#FF1744]/15 text-[#FF1744] font-bold text-xs border border-[#FF1744]/30 uppercase tracking-wider">
              CRITICAL SEVERITY
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#1E2A38] text-xs text-[#7D8A99] text-left space-y-1">
            <p>Target: <strong className="text-white">{currentIncident.affected_asset}</strong></p>
            <p>Department: <strong className="text-white">{currentIncident.department}</strong></p>
            <p>Incident: <strong className="text-[#00D9FF]">{currentIncident.incident_number}</strong></p>
          </div>
        </div>

        {/* 4 Dimension Bars */}
        <div className="lg:col-span-2 bg-[#111923] border border-[#1E2A38] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white mb-1">Four-Dimensional Risk Decomposition</h2>
            <p className="text-xs text-[#7D8A99] mb-5">Quantitative metrics calculated by AI Risk Assessment Agent</p>

            <div className="space-y-4">
              {metrics.map((m, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-xs mb-1.5 font-mono">
                    <span className="text-white font-medium">{m.label}</span>
                    <span className="text-[#00D9FF] font-bold">{m.value} / 100</span>
                  </div>
                  <div className="w-full bg-[#070B12] h-2.5 rounded-full overflow-hidden p-0.5 border border-[#1E2A38]">
                    <div className={`h-full rounded-full ${m.color} ${m.bar}`}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#1E2A38] flex items-center space-x-2 text-xs text-[#7D8A99]">
            <Info className="w-4 h-4 text-[#00D9FF]" />
            <span>Confidence score of 94% indicates verified threat actor signatures matching Ethio-CERT intelligence.</span>
          </div>
        </div>
      </div>

      {/* Explainability Breakdown Table */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6">
        <h2 className="text-sm font-bold text-white mb-1">Algorithmic Scoring Derivation</h2>
        <p className="text-xs text-[#7D8A99] mb-4">Every point contributed to the final score is mathematically accounted for and explainable</p>

        <div className="border border-[#1E2A38] rounded-lg overflow-hidden font-mono text-xs">
          <table className="w-full text-left">
            <thead className="bg-[#0D131C] text-[#7D8A99] border-b border-[#1E2A38] uppercase text-[10px]">
              <tr>
                <th className="py-2.5 px-4">Contributing Evidence & Anomaly Factor</th>
                <th className="py-2.5 px-4">Category</th>
                <th className="py-2.5 px-4 text-right">Points Added</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2A38] text-white">
              {breakdown.map((row, i) => (
                <tr key={i} className="hover:bg-[#0D131C]/60 transition">
                  <td className="py-3 px-4 font-sans">{row.factor}</td>
                  <td className="py-3 px-4 text-[#00D9FF] text-[11px]">{row.category}</td>
                  <td className="py-3 px-4 text-right font-bold text-[#FF1744]">+{row.points}</td>
                </tr>
              ))}
              <tr className="bg-[#0D131C] font-bold">
                <td className="py-3 px-4 text-[#7D8A99]">Composite Risk Score (Sum of Weighted Factors)</td>
                <td className="py-3 px-4 text-[#7D8A99]">Normalized 0-100</td>
                <td className="py-3 px-4 text-right text-base text-[#FF1744] font-black">{totalCalculated} / 100</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
