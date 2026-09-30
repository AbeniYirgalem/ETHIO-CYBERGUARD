import React from 'react';
import { 
  LayoutDashboard, 
  Activity, 
  AlertTriangle, 
  Bot, 
  BarChart3, 
  CheckSquare, 
  Settings,
  Flame,
  Binary,
  Mail,
  Globe,
  Radar,
  GraduationCap,
  GitMerge,
  FileText,
  Sliders
} from 'lucide-react';

export type TabId = 
  | 'overview' 
  | 'monitoring' 
  | 'pipeline'
  | 'incidents' 
  | 'threat_intel' 
  | 'investigation' 
  | 'phishing'
  | 'typosquat'
  | 'osint'
  | 'awareness'
  | 'assistant' 
  | 'risk' 
  | 'response' 
  | 'reports'
  | 'settings'
  | 'admin';

interface SidebarProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  pendingApprovalsCount: number;
  criticalIncidentsCount: number;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeTab, 
  setActiveTab,
  pendingApprovalsCount,
  criticalIncidentsCount,
  mobileOpen = false,
  onCloseMobile
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'pipeline', label: 'Unified Pipeline', icon: GitMerge, badge: 'Common Graph' },
    { id: 'monitoring', label: 'Monitoring', icon: Activity, badge: 'Live' },
    { 
      id: 'incidents', 
      label: 'Incidents', 
      icon: Flame, 
      count: criticalIncidentsCount, 
      countColor: 'bg-[#FF1744] text-white' 
    },
    { id: 'threat_intel', label: 'Threat Intel', icon: Binary },
    { id: 'investigation', label: 'Investigation', icon: AlertTriangle },
    { id: 'phishing', label: 'Phishing Analyzer', icon: Mail, badge: 'NLP / Forensics' },
    { id: 'typosquat', label: 'Brand & Typosquat', icon: Globe, badge: 'openSquat' },
    { id: 'osint', label: 'Attack Surface OSINT', icon: Radar, badge: 'SpiderFoot' },
    { id: 'awareness', label: 'Security Awareness', icon: GraduationCap, badge: 'Simulations' },
    { id: 'assistant', label: 'AI Security Assistant', icon: Bot, badge: '7 Agents' },
    { id: 'risk', label: 'Risk & Analytics', icon: BarChart3 },
    { 
      id: 'response', 
      label: 'Response Center', 
      icon: CheckSquare, 
      count: pendingApprovalsCount, 
      countColor: 'bg-[#F59E0B] text-black font-bold' 
    },
    { id: 'reports', label: 'Reports & Compliance', icon: FileText, badge: 'Export' },
    { id: 'settings', label: 'Identity & RBAC', icon: Sliders },
    { id: 'admin', label: 'Administration', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div 
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-30 md:hidden"
        />
      )}

      <aside className={`
        fixed md:static inset-y-0 left-0 z-40
        w-64 bg-[#070B12] border-r border-[#1E2A38] flex flex-col justify-between 
        h-[calc(100vh-4rem)] p-3 select-none transition-transform duration-200 ease-in-out
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="space-y-1 overflow-y-auto">
          <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-[#7D8A99]">
            SOC Operations
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id as TabId);
                  if (onCloseMobile) onCloseMobile();
                }}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-md text-xs font-medium transition-all ${
                  isActive 
                    ? 'bg-[#111923] text-[#00D9FF] border-l-2 border-[#00D9FF]' 
                    : 'text-[#7D8A99] hover:text-[#E6EDF3] hover:bg-[#0D131C]'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#00D9FF]' : 'text-[#7D8A99]'}`} />
                  <span>{item.label}</span>
                </div>

                <div className="flex items-center space-x-1.5">
                  {item.badge && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
                      {item.badge}
                    </span>
                  )}
                  {item.count !== undefined && item.count > 0 && (
                    <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${item.countColor}`}>
                      {item.count}
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Bottom Status Box */}
        <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg mt-2">
          <div className="flex items-center justify-between text-[11px] text-[#7D8A99] mb-1">
            <span>SOC Health</span>
            <span className="text-[#22C55E] flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E] inline-block"></span>
              <span>OPTIMAL</span>
            </span>
          </div>
          <p className="text-[10px] text-[#7D8A99] leading-tight">
            7 AI Agents Synchronized • Ethio-CERT Threat Feed Active
          </p>
        </div>
      </aside>
    </>
  );
};
