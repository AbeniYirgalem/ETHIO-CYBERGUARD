import React, { useState } from 'react';
import { 
  User, 
  Building2, 
  Key, 
  Lock, 
  CheckCircle2, 
  Globe
} from 'lucide-react';

interface SettingsViewProps {
  currentRole: string;
  setCurrentRole: (role: string) => void;
  currentOrg: string;
  setCurrentOrg: (org: string) => void;
  language: 'en' | 'am';
  setLanguage: (lang: 'en' | 'am') => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  currentRole,
  setCurrentRole,
  currentOrg,
  setCurrentOrg,
  language,
  setLanguage
}) => {
  const [saveNotice, setSaveNotice] = useState(false);

  const handleSave = () => {
    setSaveNotice(true);
    setTimeout(() => setSaveNotice(false), 2500);
  };

  const organizations = [
    { id: "cbe", name: "Commercial Bank of Ethiopia (CBE)", sector: "Banking" },
    { id: "ethiotelecom", name: "Ethio Telecom / Telebirr", sector: "Telecom" },
    { id: "awash", name: "Awash Bank", sector: "Banking" },
    { id: "insa", name: "Information Network Security Administration (INSA)", sector: "Government" }
  ];

  const roles = [
    { id: "SUPER_ADMIN", title: "SUPER_ADMIN", desc: "National oversight across all enterprise tenants" },
    { id: "SOC_MANAGER", title: "SOC_MANAGER", desc: "Team leadership and dual-custody approval authority" },
    { id: "INCIDENT_COMMANDER", title: "INCIDENT_COMMANDER", desc: "Containment authorization authority" },
    { id: "SOC_ANALYST", title: "SOC_ANALYST", desc: "Alert triage, phishing analysis, and evidence gathering" },
    { id: "SECURITY_ENGINEER", title: "SECURITY_ENGINEER", desc: "SIGMA detection rule tuning and OSINT scanning" },
    { id: "AUDITOR", title: "AUDITOR", desc: "Read-only access to immutable audit chain and compliance reports" },
    { id: "VIEWER", title: "VIEWER", desc: "Executive view of high-level threat metrics" }
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="pb-3 border-b border-[#1E2A38]">
        <h1 className="text-xl font-bold text-white">Identity, RBAC & Multi-Tenancy Settings</h1>
        <p className="text-xs text-[#7D8A99] mt-0.5">
          Manage your active analyst profile, switch tenant organizations, and test role-based permissions.
        </p>
      </div>

      {saveNotice && (
        <div className="p-3 bg-[#22C55E]/10 border border-[#22C55E]/30 rounded-lg flex items-center space-x-2 text-xs text-[#22C55E]">
          <CheckCircle2 className="w-4 h-4" />
          <span>Security session preferences updated successfully.</span>
        </div>
      )}

      {/* 1. User Profile */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <User className="w-4 h-4 text-[#00D9FF]" />
          <span>Active Analyst Profile</span>
        </h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-[#7D8A99] block mb-1">Full Name</label>
            <input 
              type="text" 
              defaultValue="Dawit Mengistu" 
              className="w-full bg-[#0D131C] border border-[#1E2A38] rounded-md px-3 py-2 text-white focus:outline-none focus:border-[#00D9FF]"
            />
          </div>
          <div>
            <label className="text-[#7D8A99] block mb-1">Email Address</label>
            <input 
              type="email" 
              defaultValue="dawit.mengistu@cbe.com.et" 
              disabled
              className="w-full bg-[#0D131C] border border-[#1E2A38] rounded-md px-3 py-2 text-[#7D8A99] cursor-not-allowed"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-[#1E2A38] text-xs">
          <div className="flex items-center space-x-2">
            <Lock className="w-4 h-4 text-[#22C55E]" />
            <span className="text-[#E6EDF3]">Multi-Factor Authentication (MFA / FIDO2 Hardware Key):</span>
            <span className="font-bold text-[#22C55E]">ENFORCED</span>
          </div>
          <button className="text-xs text-[#00D9FF] hover:underline font-semibold">
            Re-authenticate Key
          </button>
        </div>
      </div>

      {/* 2. Tenant Organization Switcher */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Building2 className="w-4 h-4 text-[#00D9FF]" />
          <span>Tenant Organization Isolation</span>
        </h2>
        <p className="text-xs text-[#7D8A99]">
          ETHIO-CYBERGUARD isolates all events, telemetry, and playbooks by organization ID. Select your active tenant:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {organizations.map(org => (
            <button
              key={org.id}
              onClick={() => setCurrentOrg(org.name)}
              className={`p-3 rounded-lg border text-left text-xs transition ${
                currentOrg === org.name
                  ? 'bg-[#00D9FF]/10 border-[#00D9FF] text-white'
                  : 'bg-[#0D131C] border-[#1E2A38] text-[#7D8A99] hover:border-[#7D8A99] hover:text-[#E6EDF3]'
              }`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-bold text-white">{org.name}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#111923] text-[#00D9FF] font-mono">{org.sector}</span>
              </div>
              <p className="text-[11px] text-[#7D8A99]">Strict tenant sandbox boundary active</p>
            </button>
          ))}
        </div>
      </div>

      {/* 3. Role-Based Access Control (RBAC) Switcher */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Key className="w-4 h-4 text-[#00D9FF]" />
          <span>Simulated RBAC Role</span>
        </h2>
        <p className="text-xs text-[#7D8A99]">
          Switch your active role to verify permission enforcement on containment actions, user management, and rule editing:
        </p>

        <div className="space-y-2">
          {roles.map(r => (
            <button
              key={r.id}
              onClick={() => setCurrentRole(r.id)}
              className={`w-full p-2.5 rounded-lg border text-left flex justify-between items-center text-xs transition ${
                currentRole === r.id
                  ? 'bg-[#00D9FF]/10 border-[#00D9FF] text-white'
                  : 'bg-[#0D131C] border-[#1E2A38] text-[#7D8A99] hover:border-[#7D8A99] hover:text-[#E6EDF3]'
              }`}
            >
              <div>
                <span className="font-bold text-white mr-2">{r.title}</span>
                <span className="text-[11px] text-[#7D8A99]">{r.desc}</span>
              </div>
              {currentRole === r.id && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00D9FF]/20 text-[#00D9FF] font-bold">
                  ACTIVE
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 4. Localization Preferences */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Globe className="w-4 h-4 text-[#00D9FF]" />
          <span>Localization & Language Preference</span>
        </h2>

        <div className="flex space-x-3 text-xs">
          <button
            onClick={() => setLanguage('en')}
            className={`px-4 py-2 rounded-lg border font-semibold transition ${
              language === 'en'
                ? 'bg-[#00D9FF] text-black border-[#00D9FF]'
                : 'bg-[#0D131C] border-[#1E2A38] text-[#7D8A99] hover:text-white'
            }`}
          >
            English (United States / UK)
          </button>
          <button
            onClick={() => setLanguage('am')}
            className={`px-4 py-2 rounded-lg border font-semibold transition ${
              language === 'am'
                ? 'bg-[#00D9FF] text-black border-[#00D9FF]'
                : 'bg-[#0D131C] border-[#1E2A38] text-[#7D8A99] hover:text-white'
            }`}
          >
            አማርኛ (Amharic - Ethiopia)
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end space-x-3 pt-2">
        <button
          onClick={handleSave}
          className="px-5 py-2 rounded-lg bg-[#00D9FF] hover:bg-[#00B8D9] text-black font-bold text-xs transition"
        >
          Save Configuration
        </button>
      </div>
    </div>
  );
};
