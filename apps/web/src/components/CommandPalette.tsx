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
  Sliders, 
  ArrowRight,
  Flame,
  Binary,
  CheckSquare,
  BarChart3,
  FileText,
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
  const isAm = language === 'am';

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
      title: isAm ? 'አጠቃላይ እይታ እና ዋና መረጃዎች' : 'Command Overview & Executive KPI',
      subtitle: isAm ? 'የቀጥታ የደህንነት ሁኔታ፣ MTTD/MTTR እና ንቁ ስጋቶች' : 'Live SOC posture, MTTD/MTTR metrics, active threats',
      icon: <LayoutDashboard className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G O',
      perform: () => { onNavigate('overview'); onClose(); }
    },
    {
      id: 'nav-incidents',
      category: 'Navigation',
      title: isAm ? 'የሳይበር አደጋዎች ዝርዝር እና የጥቃት ግራፍ' : 'Incidents Queue & Attack Graph',
      subtitle: isAm ? 'የተጠለፉ ሲስተሞች እና የመከላከል ሂደት' : 'Investigate multi-stage attack chains and containment status',
      icon: <Flame className="w-4 h-4 text-[#FF1744]" />,
      shortcut: 'G I',
      perform: () => { onNavigate('incidents'); onClose(); }
    },
    {
      id: 'nav-phishing',
      category: 'Navigation',
      title: isAm ? 'የፊሺንግ ኢሜይል እና የአማርኛ ፎረንሲክስ' : 'Phishing Email & Amharic Forensics',
      subtitle: isAm ? 'የRFC-822 ሄደር፣ SPF/DKIM እና የቴሌብር ማጭበርበሪያዎች' : 'Analyze RFC-822 headers, SPF/DKIM, and Telebirr lures',
      icon: <Mail className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G P',
      perform: () => { onNavigate('phishing'); onClose(); }
    },
    {
      id: 'nav-threat-intel',
      category: 'Navigation',
      title: isAm ? 'የስጋት መረጃ እና አይኦሲ ዳታቤዝ' : 'Threat Intelligence & IOC Feeds',
      subtitle: isAm ? 'የኢትዮ-ሰርት እና የባንኮች የጋራ ጥቃት መረጃዎች' : 'MISP, OpenCTI, and Ethio-CERT malicious indicators',
      icon: <Binary className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G T',
      perform: () => { onNavigate('threat_intel'); onClose(); }
    },
    {
      id: 'nav-response',
      category: 'Navigation',
      title: isAm ? 'የፈጣን ምላሽ ማዕከል እና የሰው ማጽደቂያ' : 'Response Center & Containment Actions',
      subtitle: isAm ? 'ባለሁለት-ደረጃ የሰው ማረጋገጫ እና አውቶማቲክ መከላከያ' : 'Dual-custody authorization queue for host/IP isolation',
      icon: <CheckSquare className="w-4 h-4 text-[#22C55E]" />,
      shortcut: 'G S',
      perform: () => { onNavigate('response'); onClose(); }
    },
    {
      id: 'nav-risk',
      category: 'Navigation',
      title: isAm ? 'የስጋት ስሌት እና ተጋላጭነት ትንተና' : 'Explainable Risk & Asset Scoring',
      subtitle: isAm ? 'የባንክ እና ቴሌኮም ንብረቶች የተጋላጭነት ነጥብ' : 'Formula breakdown: Threat × Asset × Vulnerability',
      icon: <BarChart3 className="w-4 h-4 text-[#F59E0B]" />,
      shortcut: 'G K',
      perform: () => { onNavigate('risk'); onClose(); }
    },
    {
      id: 'nav-radar',
      category: 'Navigation',
      title: isAm ? 'የኢትዮጵያ ወሳኝ መሰረተ-ልማቶች ራዳር' : 'National Infrastructure Threat Radar',
      subtitle: isAm ? 'በባንክ፣ ቴሌኮም፣ ሃይል እና መንግስት ላይ ያለ የጥቃት ቅኝት' : 'Real-time telemetry across banking, telco, energy, and government',
      icon: <Radar className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G D',
      perform: () => { onNavigate('overview'); onClose(); }
    },
    {
      id: 'nav-reports',
      category: 'Navigation',
      title: isAm ? 'የሳይበር ደህንነት እና የኢንሳ ተገዢነት ሪፖርት' : 'Executive Threat & Compliance Reports',
      subtitle: isAm ? 'የቦርድ አጭር መግለጫ እና የኢንሳ መመሪያ ተገዢነት' : 'Board-level briefings and INSA compliance audit dossiers',
      icon: <FileText className="w-4 h-4 text-[#22C55E]" />,
      shortcut: 'G E',
      perform: () => { onNavigate('reports'); onClose(); }
    },
    {
      id: 'nav-typosquat',
      category: 'Navigation',
      title: isAm ? 'የስም ቅጅ እና የማጭበርበሪያ ድረ-ገጾች' : 'Brand Defense & Domain Typosquatting',
      subtitle: isAm ? 'openSquat የባንኮች የማስመሰል ድረ-ገጾች እና ማወረጃ' : 'openSquat homoglyphs, Ethiopian bank lookalikes, takedowns',
      icon: <Globe className="w-4 h-4 text-[#F59E0B]" />,
      shortcut: 'G B',
      perform: () => { onNavigate('typosquat'); onClose(); }
    },
    {
      id: 'nav-osint',
      category: 'Navigation',
      title: isAm ? 'የጥቃት ቀጠና እና የኦሲንት ቅኝት (OSINT)' : 'Attack Surface & OSINT Reconnaissance',
      subtitle: isAm ? 'SpiderFoot የኢትዮ ቴሌኮም ASN እና ክፍት ፖርቶች ፍተሻ' : 'SpiderFoot ASN routing, passive subdomains, open port audits',
      icon: <Radar className="w-4 h-4 text-[#22C55E]" />,
      shortcut: 'G R',
      perform: () => { onNavigate('osint'); onClose(); }
    },
    {
      id: 'nav-awareness',
      category: 'Navigation',
      title: isAm ? 'የሰራተኞች የሳይበር ግንዛቤ እና ስልጠና' : 'Security Awareness Simulator',
      subtitle: isAm ? 'የቴሌብር እና የባንክ ማጭበርበሪያዎች የተሞክሮ ዘመቻ' : 'Employee simulation campaigns, Telebirr/CBE fraud lures',
      icon: <GraduationCap className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'G A',
      perform: () => { onNavigate('awareness'); onClose(); }
    },
    {
      id: 'nav-assistant',
      category: 'Navigation',
      title: isAm ? '7 የተቀናጁ የኤአይ የደህንነት ወኪሎች' : '7 Multi-Agent AI Security Assistant',
      subtitle: isAm ? 'የጥቃት ትንተና፣ የMITRE ምደባ እና የአማካሪ ወኪሎች' : 'Query event, correlation, and MITRE investigation agents',
      icon: <Bot className="w-4 h-4 text-[#FF1744]" />,
      shortcut: 'G C',
      perform: () => { onNavigate('assistant'); onClose(); }
    },
    {
      id: 'nav-settings',
      category: 'Navigation',
      title: isAm ? 'የማንነት፣ ፈቃዶች እና የተቋም ማስተካከያ' : 'System Settings & Multi-Tenant Role',
      subtitle: isAm ? 'የRBAC ፈቃዶች እና የተቋም መለያ' : 'Configure RBAC permissions and organization profile',
      icon: <Sliders className="w-4 h-4 text-[#7D8A99]" />,
      shortcut: 'G ,',
      perform: () => { onNavigate('settings'); onClose(); }
    },

    // Quick Actions
    {
      id: 'act-toggle-sound',
      category: 'Tactical Actions',
      title: soundEnabled ? (isAm ? 'የታክቲካል ድምፅ ማጥፊያ' : 'Mute Tactical Audio Synthesizer') : (isAm ? 'የታክቲካል ድምፅ ማብሪያ' : 'Enable Tactical Audio Synthesizer'),
      subtitle: isAm ? 'የማጽደቂያዎች እና ማስጠንቀቂያዎች ድምፅ ማስተካከያ' : 'Audio feedback for clicks, alerts, and SOAR response approvals',
      icon: soundEnabled ? <VolumeX className="w-4 h-4 text-[#F59E0B]" /> : <Volume2 className="w-4 h-4 text-[#22C55E]" />,
      shortcut: 'M',
      perform: () => { onToggleSound(); onClose(); }
    },
    {
      id: 'act-toggle-lang',
      category: 'Tactical Actions',
      title: language === 'en' ? 'Switch Language to Amharic (አማርኛ)' : 'Switch Language to English (EN)',
      subtitle: isAm ? 'ወደ እንግሊዝኛ ቋንቋ ቀይር' : 'Localize threat descriptors, guidance, and alert reports',
      icon: <Languages className="w-4 h-4 text-[#00D9FF]" />,
      shortcut: 'L',
      perform: () => { onToggleLanguage(); onClose(); }
    },

    // Dynamic Incidents Search
    ...incidents.map(inc => ({
      id: `inc-${inc.id}`,
      category: 'Incidents' as const,
      title: `${inc.incident_number}: ${inc.title}`,
      subtitle: `${isAm ? 'የተጠቃ ሲስተም' : 'Asset'}: ${inc.affected_asset} • ${isAm ? 'ክብደት' : 'Severity'}: ${inc.severity} • ${isAm ? 'ስጋት' : 'Risk'}: ${inc.risk_score}/100`,
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
            placeholder={isAm ? "ትዕዛዝ፣ የአደጋ መለያ (ለምሳሌ INC-00042) ወይም የክፍል ስም ይተይቡ..." : "Type a command, incident ID (e.g. INC-00042), or tab name..."}
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
              <p>{isAm ? `ምንም የተገኘ ትዕዛዝ ወይም አደጋ የለም፡ "${query}"` : `No matching commands or incidents found for "${query}".`}</p>
              <p className="mt-1 text-[11px] text-[#00D9FF]">
                {isAm ? 'እንደ "አደጋዎች"፣ "ፊሺንግ"፣ "ቴሌብር" ወይም "cbe" ብለው ይፈልጉ' : 'Try searching "incidents", "phishing", "cbe", or "telebirr"'}
              </p>
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
            <span>{isAm ? "↑↓ ለመምረጥ" : "↑↓ to navigate"}</span>
            <span>{isAm ? "↵ ለማረጋገጥ" : "↵ to select"}</span>
            <span>{isAm ? "ESC ለመዝጋት" : "ESC to close"}</span>
          </div>
          <span className="text-[#00D9FF]">
            {isAm ? "የኢትዮ-ሳይበርጋርድ ፈጣን መፈለጊያ" : "ETHIO-CYBERGUARD HUD"}
          </span>
        </div>
      </div>
    </div>
  );
};
