import React, { useState } from 'react';
import { LogIn, X, Loader2 } from 'lucide-react';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (email: string, password: string) => Promise<void>;
}

const DEMO_ACCOUNTS = [
  { email: 'analyst@cbe.com.et', label: 'Analyst (cannot approve)' },
  { email: 'commander@cbe.com.et', label: 'Commander (can approve)' },
  { email: 'admin@cbe.com.et', label: 'Super Admin' },
];

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      await onSubmit(email.trim(), password);
      setPassword('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign-in failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl max-w-sm w-full p-6 space-y-4 shadow-2xl">
        <div className="flex justify-between items-center border-b border-[#1E2A38] pb-3">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <LogIn className="w-5 h-5 text-[#00D9FF]" />
            <span>Sign in to SOC API</span>
          </h3>
          <button onClick={onClose} className="text-[#7D8A99] hover:text-white" aria-label="Close">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="text-[11px] text-[#7D8A99] block mb-1" htmlFor="ecg-email">Email</label>
            <input
              id="ecg-email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#070B12] border border-[#1E2A38] rounded-lg p-2 text-white focus:outline-none focus:border-[#00D9FF]"
            />
          </div>
          <div>
            <label className="text-[11px] text-[#7D8A99] block mb-1" htmlFor="ecg-password">Password</label>
            <input
              id="ecg-password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#070B12] border border-[#1E2A38] rounded-lg p-2 text-white focus:outline-none focus:border-[#00D9FF]"
            />
          </div>

          {error && (
            <p className="text-[#FF1744] bg-[#FF1744]/10 border border-[#FF1744]/30 rounded-lg p-2">{error}</p>
          )}

          <button
            type="submit"
            disabled={busy}
            className="w-full py-2 rounded-lg bg-[#00D9FF] hover:bg-[#00D9FF]/80 disabled:opacity-50 text-black font-bold flex items-center justify-center space-x-2 transition"
          >
            {busy && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{busy ? 'Signing in…' : 'Sign in'}</span>
          </button>
        </form>

        <div className="pt-3 border-t border-[#1E2A38] space-y-1.5">
          <p className="text-[10px] text-[#7D8A99] uppercase font-mono">Demo accounts (click to fill email)</p>
          {DEMO_ACCOUNTS.map((a) => (
            <button
              key={a.email}
              type="button"
              onClick={() => setEmail(a.email)}
              className="w-full text-left text-[11px] text-[#E6EDF3] hover:text-[#00D9FF] font-mono"
            >
              {a.email} <span className="text-[#7D8A99] font-sans">· {a.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
