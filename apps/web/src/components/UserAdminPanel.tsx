import React, { useEffect, useState } from 'react';
import { UserPlus, CheckCircle2, AlertTriangle } from 'lucide-react';
import { ApiError, FALLBACK_ROLES, createUser, fetchRoles } from '../api/client';

/**
 * Administrator-only user creation. The server enforces the same rules (admin permission,
 * valid role, password policy), so this form only makes them convenient to use.
 */
export const UserAdminPanel: React.FC = () => {
  const [roles, setRoles] = useState<string[]>(FALLBACK_ROLES);
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('SECURITY_ANALYST');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null);

  useEffect(() => {
    let active = true;
    fetchRoles().then((list) => {
      if (active) setRoles(list);
    });
    return () => {
      active = false;
    };
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      const created = await createUser({
        email: email.trim(),
        password,
        full_name: fullName.trim(),
        role,
      });
      setNotice({ kind: 'ok', text: `Created ${created.email} as ${created.role}.` });
      setEmail('');
      setFullName('');
      setPassword('');
    } catch (err) {
      const text =
        err instanceof ApiError && err.status === 403
          ? 'Only administrators can create users.'
          : err instanceof Error
            ? err.message
            : 'Could not create the user.';
      setNotice({ kind: 'error', text });
    } finally {
      setBusy(false);
    }
  };

  const inputClass =
    'w-full bg-[#0D131C] border border-[#1E2A38] rounded-md px-3 py-2 text-white focus:outline-none focus:border-[#00D9FF]';

  return (
    <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
      <h2 className="text-sm font-bold text-white flex items-center space-x-2">
        <UserPlus className="w-4 h-4 text-[#00D9FF]" />
        <span>User Management (Administrators)</span>
      </h2>
      <p className="text-xs text-[#7D8A99]">
        Create an account for a colleague. Passwords need 12+ characters mixing at least three of:
        lowercase, uppercase, digits, symbols.
      </p>

      {notice && (
        <div
          role="status"
          className={`p-3 rounded-lg flex items-center space-x-2 text-xs border ${
            notice.kind === 'ok'
              ? 'bg-[#22C55E]/10 border-[#22C55E]/30 text-[#22C55E]'
              : 'bg-[#FF1744]/10 border-[#FF1744]/30 text-[#FF1744]'
          }`}
        >
          {notice.kind === 'ok' ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
          <span>{notice.text}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div>
          <label htmlFor="new-user-name" className="text-[#7D8A99] block mb-1">Full Name</label>
          <input id="new-user-name" type="text" required maxLength={100} value={fullName}
            onChange={(e) => setFullName(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label htmlFor="new-user-email" className="text-[#7D8A99] block mb-1">Email Address</label>
          <input id="new-user-email" type="email" required value={email}
            onChange={(e) => setEmail(e.target.value)} className={inputClass} autoComplete="off" />
        </div>
        <div>
          <label htmlFor="new-user-role" className="text-[#7D8A99] block mb-1">Role</label>
          <select id="new-user-role" value={role} onChange={(e) => setRole(e.target.value)} className={inputClass}>
            {roles.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="new-user-password" className="text-[#7D8A99] block mb-1">Initial Password</label>
          <input id="new-user-password" type="password" required minLength={12} maxLength={128} value={password}
            onChange={(e) => setPassword(e.target.value)} className={inputClass} autoComplete="new-password" />
        </div>
        <div className="sm:col-span-2 flex justify-end">
          <button type="submit" disabled={busy}
            className="px-5 py-2 rounded-lg bg-[#00D9FF] hover:bg-[#00B8D9] disabled:opacity-60 text-black font-bold text-xs transition">
            {busy ? 'Creating…' : 'Create User'}
          </button>
        </div>
      </form>
    </div>
  );
};
