import React from 'react';
import { CheckCircle2, AlertTriangle, Info, X, ShieldAlert } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'warning' | 'critical' | 'info';
  title: string;
  message: string;
  timestamp: string;
}

interface ToastManagerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastManager: React.FC<ToastManagerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col space-y-2.5 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto p-3.5 rounded-xl border backdrop-blur-md shadow-2xl flex items-start space-x-3 transition-all duration-300 animate-in slide-in-from-bottom-5 ${
            toast.type === 'critical'
              ? 'bg-[#FF1744]/15 border-[#FF1744] text-white shadow-[#FF1744]/20'
              : toast.type === 'warning'
              ? 'bg-[#F59E0B]/15 border-[#F59E0B] text-white shadow-[#F59E0B]/20'
              : toast.type === 'success'
              ? 'bg-[#22C55E]/15 border-[#22C55E] text-white shadow-[#22C55E]/20'
              : 'bg-[#00D9FF]/15 border-[#00D9FF] text-white shadow-[#00D9FF]/20'
          }`}
        >
          <div className="mt-0.5 shrink-0">
            {toast.type === 'critical' && <ShieldAlert className="w-5 h-5 text-[#FF1744]" />}
            {toast.type === 'warning' && <AlertTriangle className="w-5 h-5 text-[#F59E0B]" />}
            {toast.type === 'success' && <CheckCircle2 className="w-5 h-5 text-[#22C55E]" />}
            {toast.type === 'info' && <Info className="w-5 h-5 text-[#00D9FF]" />}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-0.5">
              <h4 className="text-xs font-bold tracking-wide truncate">{toast.title}</h4>
              <span className="text-[10px] font-mono text-[#7D8A99]">{toast.timestamp}</span>
            </div>
            <p className="text-[11px] text-[#E6EDF3] leading-snug">{toast.message}</p>
          </div>

          <button
            onClick={() => onDismiss(toast.id)}
            className="text-[#7D8A99] hover:text-white p-1 rounded transition shrink-0"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};
