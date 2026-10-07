import React, { useState, useEffect } from 'react';
import { Shield, Bell, Search, Globe, Menu, Volume2, VolumeX, Radio } from 'lucide-react';
import { soundManager } from '../utils/sound';

interface HeaderProps {
  liveCount: number;
  onOpenNotifications?: () => void;
  language?: 'en' | 'am';
  onToggleLanguage?: () => void;
  currentOrg?: string;
  currentRole?: string;
  onToggleMobileMenu?: () => void;
  onOpenCommandPalette?: () => void;
  soundEnabled?: boolean;
  onToggleSound?: () => void;
}

const INTEL_TICKER_ITEMS = [
  { tag: 'CRITICAL', text: 'CBE Financial Core: Port 445 SMB anomaly intercepted on SERVER-04', color: 'text-[#FF1744]' },
  { tag: 'INTEL', text: 'Ethio-CERT Feed: Cobalt Strike C2 IP 185.220.101.5 added to perimeter blocklist', color: 'text-[#00D9FF]' },
  { tag: 'DEFENSE', text: 'openSquat: Rogue domain registered telebirr-verify.top (94% homoglyph score)', color: 'text-[#F59E0B]' },
  { tag: 'TELCO', text: 'Ethio Telecom AS24757: Ingress scrubbed 14.8 Gbps SYN flood sweep', color: 'text-[#22C55E]' },
  { tag: 'COMPLIANCE', text: 'INSA Directive 2026-04: Mandatory dual-custody enforced for all banking endpoints', color: 'text-[#00D9FF]' }
];

export const Header: React.FC<HeaderProps> = ({ 
  liveCount,
  onOpenNotifications,
  language = 'en',
  onToggleLanguage,
  currentOrg = "Commercial Bank of Ethiopia (CBE)",
  currentRole = "SECURITY_ANALYST",
  onToggleMobileMenu,
  onOpenCommandPalette,
  soundEnabled = true,
  onToggleSound
}) => {
  const [tickerIndex, setTickerIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setTickerIndex(prev => (prev + 1) % INTEL_TICKER_ITEMS.length);
    }, 5500);
    return () => clearInterval(timer);
  }, []);

  const currentTicker = INTEL_TICKER_ITEMS[tickerIndex];

  return (
    <header className="border-b border-[#1E2A38] bg-[#070B12]/95 backdrop-blur-md sticky top-0 z-40">
      {/* Top Tactical Alert Ribbon */}
      <div className="bg-[#090E17] border-b border-[#1E2A38]/50 px-4 py-1 flex items-center justify-between text-[11px] overflow-hidden">
        <div className="flex items-center space-x-2 min-w-0">
          <span className="flex items-center space-x-1 text-[#00D9FF] font-mono font-bold shrink-0">
            <Radio className="w-3 h-3 animate-pulse text-[#00D9FF]" />
            <span>ETHIO-CERT LIVE WIRE:</span>
          </span>
          <div className="flex items-center space-x-2 truncate">
            <span className={`px-1.5 py-0.2 rounded font-mono font-bold text-[9px] bg-[#111923] border border-[#1E2A38] ${currentTicker.color}`}>
              [{currentTicker.tag}]
            </span>
            <span className="text-[#E6EDF3] truncate font-mono text-[11px] animate-in fade-in duration-300">
              {currentTicker.text}
            </span>
          </div>
        </div>

        <div className="hidden md:flex items-center space-x-3 shrink-0 pl-3 font-mono text-[10px] text-[#7D8A99]">
          <span className="flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E]"></span>
            <span>INSA LINK: SYNCHRONIZED</span>
          </span>
          <span>•</span>
          <span className="text-[#00D9FF]">ADDIS ABABA ROOT SOC</span>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="h-15 px-4 sm:px-6 flex items-center justify-between">
        {/* Brand Identity & Mobile Menu Toggle */}
        <div className="flex items-center space-x-3">
          {onToggleMobileMenu && (
            <button 
              onClick={onToggleMobileMenu}
              className="md:hidden p-1.5 rounded-lg border border-[#1E2A38] text-[#7D8A99] hover:text-white"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}
          <div className="p-2 bg-[#00D9FF]/10 border border-[#00D9FF]/30 rounded-lg flex items-center justify-center shadow-lg shadow-[#00D9FF]/5">
            <Shield className="w-5 h-5 text-[#00D9FF]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold tracking-wider text-sm sm:text-base text-white">ETHIO-CYBERGUARD</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#00D9FF]/15 text-[#00D9FF] border border-[#00D9FF]/30 font-bold">
                DEFCON 2
              </span>
            </div>
            <p className="text-[10px] sm:text-[11px] text-[#7D8A99] tracking-tight hidden sm:block">
              National AI SIEM & Incident Command • Critical Infrastructure
            </p>
          </div>
        </div>

        {/* Center Search / Command Palette Bar */}
        <div className="hidden lg:flex items-center w-80 xl:w-96 relative">
          <Search className="w-4 h-4 text-[#7D8A99] absolute left-3" />
          <input 
            type="text" 
            readOnly
            onClick={onOpenCommandPalette}
            placeholder="Press ⌘K or click to search indicators, assets, actions..."
            className="w-full bg-[#0D131C] border border-[#1E2A38] hover:border-[#00D9FF]/50 cursor-pointer rounded-md py-1.5 pl-9 pr-16 text-xs text-[#E6EDF3] placeholder-[#7D8A99] focus:outline-none transition-all font-mono"
          />
          <button
            onClick={onOpenCommandPalette}
            className="absolute right-2 text-[10px] font-mono text-[#00D9FF] bg-[#111923] border border-[#1E2A38] px-1.5 py-0.5 rounded hover:bg-[#00D9FF]/20 transition"
          >
            ⌘K HUD
          </button>
        </div>

        {/* Right Controls & Profile */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Live Telemetry Rate */}
          <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 bg-[#0D131C] border border-[#1E2A38] rounded-full text-xs">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00D9FF] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00D9FF]"></span>
            </span>
            <span className="text-[#7D8A99] font-mono text-[11px]">
              INGEST: <strong className="text-white">{liveCount.toLocaleString()} EPS</strong>
            </span>
          </div>

          {/* Sound Synthesizer Toggle */}
          {onToggleSound && (
            <button
              onClick={() => {
                onToggleSound();
                soundManager.playClick();
              }}
              title={soundEnabled ? "Mute Tactical Audio Synthesizer" : "Enable Tactical Audio Synthesizer"}
              className={`p-2 rounded-md border text-xs transition ${
                soundEnabled 
                  ? 'bg-[#00D9FF]/10 text-[#00D9FF] border-[#00D9FF]/30 hover:bg-[#00D9FF]/20' 
                  : 'bg-[#0D131C] text-[#7D8A99] border-[#1E2A38] hover:text-white'
              }`}
            >
              {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </button>
          )}

          {/* Language Switcher */}
          {onToggleLanguage && (
            <button 
              onClick={() => {
                onToggleLanguage();
                soundManager.playClick();
              }}
              title="Toggle English / Amharic"
              className="flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-[#0D131C] hover:bg-[#111923] border border-[#1E2A38] text-xs font-mono text-[#00D9FF] transition"
            >
              <Globe className="w-3.5 h-3.5" />
              <span className="font-bold">{language === 'en' ? 'EN' : 'አማ'}</span>
            </button>
          )}

          {/* Notifications */}
          <button 
            onClick={() => {
              if (onOpenNotifications) onOpenNotifications();
              soundManager.playClick();
            }}
            title="Open Notifications"
            className="relative p-2 rounded-md hover:bg-[#111923] border border-[#1E2A38] text-[#7D8A99] hover:text-white transition"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#FF1744]"></span>
          </button>

          {/* User Account / Organization Badge */}
          <div className="flex items-center space-x-2.5 pl-2 border-l border-[#1E2A38]">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#00D9FF]/20 to-[#1E2A38] border border-[#00D9FF]/40 flex items-center justify-center text-xs font-bold text-[#00D9FF] shadow">
              DM
            </div>
            <div className="hidden sm:block text-left leading-none" title={`Organization: ${currentOrg}`}>
              <p className="text-xs font-semibold text-white">Dawit Mengistu</p>
              <p className="text-[10px] text-[#00D9FF] font-mono mt-0.5">{currentRole}</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
