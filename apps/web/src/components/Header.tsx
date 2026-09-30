import React from 'react';
import { Shield, Bell, Search, Building2 } from 'lucide-react';

interface HeaderProps {
  liveCount: number;
}

export const Header: React.FC<HeaderProps> = ({ liveCount }) => {
  return (
    <header className="h-16 border-b border-[#1E2A38] bg-[#070B12] px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-[#00D9FF]/10 border border-[#00D9FF]/30 rounded-lg flex items-center justify-center">
          <Shield className="w-6 h-6 text-[#00D9FF]" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold tracking-wider text-base text-white">ETHIO-CYBERGUARD</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#00D9FF]/15 text-[#00D9FF] border border-[#00D9FF]/30">v1.0 SOC</span>
          </div>
          <p className="text-[11px] text-[#7D8A99] tracking-tight">AI-Assisted Cybersecurity Platform • Addis Ababa</p>
        </div>
      </div>

      {/* Center Search */}
      <div className="hidden md:flex items-center w-96 relative">
        <Search className="w-4 h-4 text-[#7D8A99] absolute left-3" />
        <input 
          type="text" 
          placeholder="Search indicators, assets (e.g. SERVER-04), or incidents..."
          className="w-full bg-[#0D131C] border border-[#1E2A38] rounded-md py-1.5 pl-9 pr-8 text-xs text-[#E6EDF3] placeholder-[#7D8A99] focus:outline-none focus:border-[#00D9FF] transition-all"
        />
        <kbd className="absolute right-2.5 text-[10px] font-mono text-[#7D8A99] bg-[#111923] border border-[#1E2A38] px-1 rounded">⌘K</kbd>
      </div>

      {/* Right Controls & Profile */}
      <div className="flex items-center space-x-4">
        {/* Demo Mode Notice */}
        <div className="hidden xl:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-[#F59E0B] text-[10px] font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-[#F59E0B] animate-pulse"></span>
          <span>DEMO SANDBOX • SIMULATED TELEMETRY</span>
        </div>

        {/* Live Stream Telemetry Indicator */}
        <div className="flex items-center space-x-2 px-3 py-1 bg-[#0D131C] border border-[#1E2A38] rounded-full text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00D9FF] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00D9FF]"></span>
          </span>
          <span className="text-[#7D8A99] font-mono text-[11px]">TELEMETRY STREAM: <strong className="text-white">{liveCount.toLocaleString()} EPS</strong></span>
        </div>

        {/* Tenant Indicator */}
        <div className="hidden lg:flex items-center space-x-1.5 text-xs text-[#7D8A99] bg-[#0D131C] border border-[#1E2A38] px-3 py-1 rounded-md">
          <Building2 className="w-3.5 h-3.5 text-[#00D9FF]" />
          <span>Commercial Bank of Ethiopia</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-md hover:bg-[#111923] border border-[#1E2A38] text-[#7D8A99] hover:text-white transition">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#FF1744]"></span>
        </button>

        {/* User Account */}
        <div className="flex items-center space-x-2.5 pl-2 border-l border-[#1E2A38]">
          <div className="w-8 h-8 rounded bg-gradient-to-tr from-[#00D9FF]/20 to-[#1E2A38] border border-[#00D9FF]/40 flex items-center justify-center text-xs font-bold text-[#00D9FF]">
            DM
          </div>
          <div className="hidden sm:block text-left leading-none">
            <p className="text-xs font-semibold text-white">Dawit Mengistu</p>
            <p className="text-[10px] text-[#00D9FF]">Security Analyst • Tier 2</p>
          </div>
        </div>
      </div>
    </header>
  );
};
