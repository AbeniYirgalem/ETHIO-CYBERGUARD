import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  LayoutDashboard, 
  AlertTriangle, 
  Mail, 
  Globe, 
  Radar, 
  GraduationCap, 
  Bot, 
  ShieldCheck, 
  Sliders, 
  ArrowRight,
  Flame,
  Volume2,
  VolumeX,
  Languages,
  X
} from 'lucide-react';
import type { TabId } from './Sidebar';
import type { Incident } from '../types';
import { soundManager } from '../utils/sound';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (tab: TabId) => void;
  incidents: Incident[];
  onSelectIncident: (inc: Incident) => void;
  onToggleSound: () => void;
  soundEnabled: boolean;
  onToggleLanguage: () => void;
  language: 'en' | 'am';
}

interface PaletteAction {
  id: string;
  category: 'Navigation' | 'Incidents' | 'Tactical Actions' | 'System';
  title: string;
  subtitle?: string;
  icon: React.ReactNode;
  shortcut?: string;
  perform: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onNavigate,
  incidents,
  onSelectIncident,
  onToggleSound,
  soundEnabled,
  onToggleLanguage,
  language
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      soundManager.playClick();
      const timer = setTimeout(() => {
        setQuery('');
        setSelectedIndex(0);
        inputRef.current?.focus();
      }, 20);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // Build searchable commands list
  const allActions: PaletteAction[] = [
    // Navigation
    {
      id: 'nav-overview',
      category: 'Navigation',
      title: 'Command Overview & Executive KPI',
      subtitle: 'Live SOC posture, MTTD/MTTR metrics, active threats',
      icon: <LayoutDashboard className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G O',
      perform: () => { onNavigate('overview'); onClose(); }
    },
    {
      id: 'nav-incidents',
      category: 'Navigation',
      title: 'Incidents Queue & Attack Graph',
      subtitle: 'Investigate multi-stage attack chains and containment status',
      icon: <Flame className="w-4 h-4 text-[#FF1744]" />,
      shortcut: 'G I',
      perform: () => { onNavigate('incidents'); onClose(); }
    },
    {
      id: 'nav-phishing',
      category: 'Navigation',
      title: 'Phishing Email & Amharic Forensics',
      subtitle: 'Analyze RFC-822 headers, SPF/DKIM, and Telebirr lures',
      icon: <Mail className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G P',
      perform: () => { onNavigate('phishing'); onClose(); }
    },
    {
      id: 'nav-typosquat',
      category: 'Navigation',
      title: 'Brand Defense & Domain Typosquatting',
      subtitle: 'openSquat homoglyphs, Ethiopian bank lookalikes, takedowns',
      icon: <Globe className="w-4 h-4 text-[#F59E0B]" />,
      shortcut: 'G T',
      perform: () => { onNavigate('typosquat'); onClose(); }
    },
    {
      id: 'nav-osint',
      category: 'Navigation',
      title: 'Attack Surface & OSINT Reconnaissance',
      subtitle: 'SpiderFoot ASN routing, passive subdomains, open port audits',
      icon: <Radar className="w-4 h-4 text-[#22C55E]" />,
      shortcut: 'G R',
      perform: () => { onNavigate('osint'); onClose(); }
    },
    {
      id: 'nav-awareness',
      category: 'Navigation',
      title: 'Security Awareness Simulator',
      subtitle: 'Employee simulation campaigns, Telebirr/CBE fraud lures',
      icon: <GraduationCap className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G A',
      perform: () => { onNavigate('awareness'); onClose(); }
    },
    {
      id: 'nav-assistant',
      category: 'Navigation',
      title: '7 Multi-Agent AI Security Assistant',
      subtitle: 'Query event, correlation, and MITRE investigation agents',
      icon: <Bot className="w-4 h-4 text-[#FF1744]" />,
      shortcut: 'G C',
      perform: () => { onNavigate('assistant'); onClose(); }
    },
    {
      id: 'nav-response',
      category: 'Navigation',
      title: 'SOAR Containment Center',
      subtitle: 'Dual-custody approval, host isolation, firewall IP drops',
      icon: <ShieldCheck className="w-4 h-4 text-[#22C55E]" />,
      shortcut: 'G S',
      perform: () => { onNavigate('response'); onClose(); }
    },
    {
      id: 'nav-settings',
      category: 'Navigation',
      title: 'System Settings & Multi-Tenant Role',
      subtitle: 'Configure RBAC permissions and organization profile',
      icon: <Sliders className="w-4 h-4 text-[#7D8A99]" />,
      shortcut: 'G ,',
      perform: () => { onNavigate('settings'); onClose(); }
    },

    // Quick Actions
    {
      id: 'act-toggle-sound',
      category: 'Tactical Actions',
      title: soundEnabled ? 'Mute Tactical Audio Synthesizer' : 'Enable Tactical Audio Synthesizer',
      subtitle: 'Audio feedback for clicks, alerts, and SOAR response approvals',
      icon: soundEnabled ? <VolumeX className="w-4 h-4 text-[#F59E0B]" /> : <Volume2 className="w-4 h-4 text-[#22C55E]" />,
      shortcut: 'M',
      perform: () => { onToggleSound(); onClose(); }
    },
    {
      id: 'act-toggle-lang',
      category: 'Tactical Actions',
      title: language === 'en' ? 'Switch Language to Amharic (አማርኛ)' : 'Switch Language to English (EN)',
      subtitle: 'Localize threat descriptors, guidance, and alert reports',
      icon: <Languages className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'L',
      perform: () => { onToggleLanguage(); onClose(); }
    },

    // Dynamic Incidents Search
    ...incidents.map(inc => ({
      id: `inc-${inc.id}`,
      category: 'Incidents' as const,
      title: `${inc.incident_number}: ${inc.title}`,
      subtitle: `Asset: ${inc.affected_asset} • Severity: ${inc.severity} • Risk: ${inc.risk_score}/100`,
      icon: <AlertTriangle className={`w-4 h-4 ${inc.severity === 'CRITICAL' ? 'text-[#FF1744]' : 'text-[#F59E0B]'}`} />,
      shortcut: `Risk ${inc.risk_score}`,
      perform: () => {
        onSelectIncident(inc);
        onNavigate('incidents');
        onClose();
      }
    }))
  ];

  // Filter actions based on query
  const filtered = query.trim() === ''
    ? allActions
    : allActions.filter(a => 
        a.title.toLowerCase().includes(query.toLowerCase()) ||
        (a.subtitle && a.subtitle.toLowerCase().includes(query.toLowerCase())) ||
        a.category.toLowerCase().includes(query.toLowerCase())
      );

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % (filtered.length || 1));
        soundManager.playClick();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filtered.length) % (filtered.length || 1));
        soundManager.playClick();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filtered[selectedIndex]) {
          filtered[selectedIndex].perform();
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filtered, selectedIndex, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/75 backdrop-blur-md animate-in fade-in duration-150">
      <div 
        className="w-full max-w-2xl bg-[#0D131C] border border-[#00D9FF]/40 rounded-2xl shadow-2xl shadow-[#00D9FF]/10 overflow-hidden flex flex-col max-h-[75vh]"
        onClick={e => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="p-4 border-b border-[#1E2A38] flex items-center space-x-3 bg-[#111923]">
          <Search className="w-5 h-5 text-[#00D9FF]" />
          <input 
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command, incident ID (e.g. INC-00042), or tab name..."
            className="flex-1 bg-transparent text-sm text-white placeholder-[#7D8A99] focus:outline-none font-mono"
          />
          <button 
            onClick={onClose}
            className="p-1 rounded-md text-[#7D8A99] hover:text-white hover:bg-[#1E2A38] transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Action Results List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1 divide-y divide-[#1E2A38]/30">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-xs text-[#7D8A99]">
              <p>No matching commands or incidents found for "{query}".</p>
              <p className="mt-1 text-[11px] text-[#00D9FF]">Try searching "incidents", "phishing", "cbe", or "telebirr"</p>
            </div>
          ) : (
            filtered.map((action, idx) => {
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={action.id}
                  onClick={() => action.perform()}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`px-3 py-2.5 rounded-lg flex items-center justify-between cursor-pointer transition ${
                    isSelected 
                      ? 'bg-[#00D9FF]/15 border border-[#00D9FF]/30 text-white' 
                      : 'hover:bg-[#111923] text-[#E6EDF3]'
                  }`}
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <div className="p-1.5 rounded-md bg-[#070B12] border border-[#1E2A38] shrink-0">
                      {action.icon}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold truncate">{action.title}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#070B12] text-[#7D8A99] border border-[#1E2A38]">
                          {action.category}
                        </span>
                      </div>
                      {action.subtitle && (
                        <p className="text-[11px] text-[#7D8A99] truncate mt-0.5">{action.subtitle}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0 ml-4">
                    {action.shortcut && (
                      <kbd className="font-mono text-[10px] text-[#7D8A99] bg-[#070B12] border border-[#1E2A38] px-1.5 py-0.5 rounded">
                        {action.shortcut}
                      </kbd>
                    )}
                    {isSelected && <ArrowRight className="w-3.5 h-3.5 text-[#00D9FF]" />}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Shortcut Hints */}
        <div className="px-4 py-2.5 bg-[#070B12] border-t border-[#1E2A38] flex items-center justify-between text-[11px] text-[#7D8A99] font-mono">
          <div className="flex items-center space-x-3">
            <span>↑↓ to navigate</span>
            <span>↵ to select</span>
            <span>ESC to close</span>
          </div>
          <span className="text-[#00D9FF]">ETHIO-CYBERGUARD HUD</span>
        </div>
      </div>
    </div>
  );
};
