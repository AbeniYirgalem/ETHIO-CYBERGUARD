import React, { useState } from 'react';
import { Bell, X, ShieldAlert, Flame, AlertTriangle } from 'lucide-react';

interface NotificationItem {
  id: string;
  title: string;
  category: 'INCIDENT' | 'SOAR' | 'PHISHING' | 'SYSTEM';
  severity: 'CRITICAL' | 'HIGH' | 'INFO';
  time: string;
  isRead: boolean;
}

interface NotificationsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateToTab?: (tab: string) => void;
}

export const NotificationsModal: React.FC<NotificationsModalProps> = ({
  isOpen,
  onClose,
  onNavigateToTab
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: "NOTIF-01",
      title: "CRITICAL: Obfuscated PowerShell & Cobalt Strike C2 beacon on SERVER-04",
      category: "INCIDENT",
      severity: "CRITICAL",
      time: "2 minutes ago",
      isRead: false
    },
    {
      id: "NOTIF-02",
      title: "SOAR ACTION REQUIRED: Host isolation pending approval for SERVER-04",
      category: "SOAR",
      severity: "HIGH",
      time: "4 minutes ago",
      isRead: false
    },
    {
      id: "NOTIF-03",
      title: "Active Phishing Campaign: 14 spoofed Telebirr prize emails intercepted",
      category: "PHISHING",
      severity: "HIGH",
      time: "12 minutes ago",
      isRead: false
    },
    {
      id: "NOTIF-04",
      title: "Ethio-CERT Threat Feed: 142 new malicious IP indicators synchronized",
      category: "SYSTEM",
      severity: "INFO",
      time: "1 hour ago",
      isRead: true
    }
  ]);

  if (!isOpen) return null;

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end p-4 sm:p-6 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md bg-[#0D131C] border border-[#1E2A38] rounded-xl shadow-2xl overflow-hidden mt-12 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-4 border-b border-[#1E2A38] flex justify-between items-center bg-[#111923]">
          <div className="flex items-center space-x-2">
            <Bell className="w-4 h-4 text-[#00D9FF]" />
            <h2 className="text-sm font-bold text-white">SOC Notification Center</h2>
            {unreadCount > 0 && (
              <span className="px-1.5 py-0.5 rounded-full bg-[#FF1744] text-[10px] font-bold text-white">
                {unreadCount}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {unreadCount > 0 && (
              <button 
                onClick={markAllRead}
                className="text-[11px] text-[#00D9FF] hover:underline"
              >
                Mark all read
              </button>
            )}
            <button 
              onClick={onClose}
              className="p-1 rounded hover:bg-[#1E2A38] text-[#7D8A99] hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Notifications List */}
        <div className="divide-y divide-[#1E2A38] max-h-96 overflow-y-auto">
          {notifications.map(n => (
            <div 
              key={n.id} 
              onClick={() => {
                setNotifications(prev => prev.map(item => item.id === n.id ? { ...item, isRead: true } : item));
                if (onNavigateToTab) {
                  if (n.category === 'INCIDENT') onNavigateToTab('incidents');
                  else if (n.category === 'SOAR') onNavigateToTab('response');
                  else if (n.category === 'PHISHING') onNavigateToTab('phishing');
                  onClose();
                }
              }}
              className={`p-3.5 transition text-xs flex space-x-3 cursor-pointer hover:bg-[#1E2A38]/50 ${
                n.isRead ? 'bg-[#0D131C] text-[#7D8A99]' : 'bg-[#111923]/60 text-white font-medium'
              }`}
            >
              <div className="mt-0.5">
                {n.severity === 'CRITICAL' ? (
                  <Flame className="w-4 h-4 text-[#FF1744]" />
                ) : n.severity === 'HIGH' ? (
                  <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
                ) : (
                  <ShieldAlert className="w-4 h-4 text-[#00D9FF]" />
                )}
              </div>
              <div className="flex-1 space-y-1">
                <p className="leading-snug">{n.title}</p>
                <div className="flex justify-between items-center text-[10px] text-[#7D8A99]">
                  <span className="font-mono text-[#00D9FF]">{n.category}</span>
                  <span>{n.time}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-[#1E2A38] bg-[#070B12] text-center text-[11px] text-[#7D8A99]">
          Directly linked to WebSocket Live Event Stream
        </div>
      </div>
    </div>
  );
};
