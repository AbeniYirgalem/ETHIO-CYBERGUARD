import React, { useState } from 'react';
import { 
  Shield, 
  ArrowRight, 
  Cpu, 
  Lock, 
  Building2, 
  Mail
} from 'lucide-react';

interface PublicLandingPageProps {
  onEnterSOC: () => void;
}

export const PublicLandingPage: React.FC<PublicLandingPageProps> = ({ onEnterSOC }) => {
  const [currentView, setCurrentView] = useState<'home' | 'about' | 'docs' | 'contact'>('home');
  const [showLoginModal, setShowLoginModal] = useState(false);

  return (
    <div className="min-h-screen bg-[#070B12] text-[#E6EDF3] flex flex-col font-sans selection:bg-[#00D9FF] selection:text-black">
      {/* Top Navbar */}
      <header className="border-b border-[#1E2A38] bg-[#070B12]/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentView('home')}>
          <div className="p-2 bg-[#00D9FF]/10 border border-[#00D9FF]/30 rounded-lg">
            <Shield className="w-5 h-5 text-[#00D9FF]" />
          </div>
          <div>
            <span className="font-bold tracking-wider text-base text-white">ETHIO-CYBERGUARD</span>
            <span className="hidden sm:inline-block ml-2 text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
              National AI SOC/SIEM
            </span>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-6 text-xs text-[#7D8A99]">
          <button 
            onClick={() => setCurrentView('home')} 
            className={`hover:text-white transition ${currentView === 'home' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            Overview
          </button>
          <button 
            onClick={() => setCurrentView('about')} 
            className={`hover:text-white transition ${currentView === 'about' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            About & Mission
          </button>
          <button 
            onClick={() => setCurrentView('docs')} 
            className={`hover:text-white transition ${currentView === 'docs' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            Documentation
          </button>
          <button 
            onClick={() => setCurrentView('contact')} 
            className={`hover:text-white transition ${currentView === 'contact' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            Contact & INSA
          </button>
        </nav>

        <div className="flex items-center space-x-3">
          <button 
            onClick={() => setShowLoginModal(true)}
            className="px-3.5 py-1.5 text-xs text-[#E6EDF3] hover:text-white bg-[#111923] border border-[#1E2A38] hover:border-[#00D9FF]/40 rounded-lg transition"
          >
            Sign In
          </button>
          <button 
            onClick={onEnterSOC}
            className="px-4 py-1.5 text-xs bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-bold rounded-lg transition flex items-center space-x-1.5 shadow-lg shadow-[#00D9FF]/20"
          >
            <span>Launch SOC Console</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Main Public Content */}
      <main className="flex-1 max-w-6xl mx-auto px-6 py-12 w-full">
        {currentView === 'home' && (
          <div className="space-y-16">
            {/* Hero Section */}
            <div className="text-center max-w-3xl mx-auto space-y-6 pt-6">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#00D9FF]/10 border border-[#00D9FF]/30 text-[#00D9FF] text-xs font-mono">
                <span className="w-2 h-2 rounded-full bg-[#00D9FF] animate-pulse"></span>
                <span>AI-Assisted Cybersecurity Platform • Addis Ababa</span>
              </div>

              <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                Centralized Threat Detection & <br />
                <span className="text-[#00D9FF]">Multi-Agent AI Investigation</span>
              </h1>

              <p className="text-sm sm:text-base text-[#7D8A99] leading-relaxed max-w-2xl mx-auto">
                ETHIO-CYBERGUARD protects Ethiopian universities, financial institutions, enterprise infrastructures, and public agencies with automated event normalization, MITRE ATT&CK correlation, and human-approved incident containment.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
                <button 
                  onClick={onEnterSOC}
                  className="w-full sm:w-auto px-6 py-3 bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-extrabold text-sm rounded-xl transition flex items-center justify-center space-x-2 shadow-xl shadow-[#00D9FF]/25"
                >
                  <span>Explore Interactive Live SOC Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => setCurrentView('docs')}
                  className="w-full sm:w-auto px-6 py-3 bg-[#111923] hover:bg-[#1E2A38] text-white border border-[#1E2A38] font-bold text-sm rounded-xl transition"
                >
                  View Architectural Specs
                </button>
              </div>
            </div>

            {/* Core Feature Pillars */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#00D9FF]/40 transition">
                <div className="p-3 bg-[#00D9FF]/10 text-[#00D9FF] rounded-lg w-fit">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">Multi-Agent AI Core</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  Seven dedicated AI agents collaborate to analyze discrete events, correlate threat intelligence, reconstruct attack chains, compute explainable risk scores, and brief leadership.
                </p>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#FF1744]/40 transition">
                <div className="p-3 bg-[#FF1744]/10 text-[#FF1744] rounded-lg w-fit">
                  <Lock className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">Human-in-the-Loop Safe Response</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  Zero autonomous destructive execution guarantee. AI evaluates blast radius and recommends containment; certified analysts inspect evidence and confirm host or IP isolation.
                </p>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#22C55E]/40 transition">
                <div className="p-3 bg-[#22C55E]/10 text-[#22C55E] rounded-lg w-fit">
                  <Building2 className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">Tailored for Regional Resilience</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  Engineered specifically for African critical sectors: Commercial Bank of Ethiopia (CBE), Addis Ababa University (AAU), Ethio Telecom IP ranges, and INSA regulatory frameworks.
                </p>
              </div>
            </div>
          </div>
        )}

        {currentView === 'about' && (
          <div className="space-y-6 max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-white">About ETHIO-CYBERGUARD</h2>
            <p className="text-xs sm:text-sm text-[#7D8A99] leading-relaxed">
              Modern enterprises and governmental institutions generate millions of security events daily from endpoints, routers, firewalls, and applications. Identifying true intrusions amidst normal noise requires scarce specialized expertise.
            </p>
            <div className="bg-[#111923] border border-[#1E2A38] p-5 rounded-xl space-y-3">
              <h3 className="text-sm font-bold text-[#00D9FF]">Target Stakeholders:</h3>
              <ul className="text-xs space-y-2 text-[#E6EDF3]">
                <li>• 🎓 Universities and educational research faculties</li>
                <li>• 🏦 Commercial banks, microfinance and payment switches</li>
                <li>• 🏥 Regional hospitals and healthcare systems</li>
                <li>• 🏛️ Federal and municipal public institutions</li>
              </ul>
            </div>
          </div>
        )}

        {currentView === 'docs' && (
          <div className="space-y-6 max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-white">Technical Documentation & Schemas</h2>
            <p className="text-xs sm:text-sm text-[#7D8A99]">Explore complete specifications in the repository:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">docs/architecture.md</span>
                <span className="text-[#7D8A99]">Overall pipeline and ECS normalization logic</span>
              </div>
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">docs/ai-architecture.md</span>
                <span className="text-[#7D8A99]">The 7 specialized AI agents & prompt design</span>
              </div>
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">docs/api.md</span>
                <span className="text-[#7D8A99]">FastAPI REST & WebSocket endpoints</span>
              </div>
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">database/schema.sql</span>
                <span className="text-[#7D8A99]">PostgreSQL core DDL & RBAC definitions</span>
              </div>
            </div>
          </div>
        )}

        {currentView === 'contact' && (
          <div className="space-y-6 max-w-xl mx-auto bg-[#111923] border border-[#1E2A38] p-6 rounded-xl text-center">
            <Mail className="w-8 h-8 text-[#00D9FF] mx-auto" />
            <h2 className="text-xl font-bold text-white">Contact ETHIO-CYBERGUARD Team</h2>
            <p className="text-xs text-[#7D8A99]">
              For collaboration, research partnerships, and incident disclosures:
            </p>
            <div className="p-4 bg-[#070B12] rounded-lg border border-[#1E2A38] text-xs font-mono text-[#00D9FF]">
              inquiries@ethio-cyberguard.et • Addis Ababa, Ethiopia
            </div>
          </div>
        )}
      </main>

      {/* Role-based Sign In Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-[#111923] border border-[#1E2A38] rounded-xl max-w-sm w-full p-6 space-y-4 shadow-2xl">
            <div className="text-center">
              <Shield className="w-8 h-8 text-[#00D9FF] mx-auto mb-2" />
              <h3 className="text-base font-bold text-white">Authenticate to SOC Console</h3>
              <p className="text-[11px] text-[#7D8A99]">Select demo credential role to enter dashboard:</p>
            </div>

            <div className="space-y-2">
              <button
                onClick={() => { setShowLoginModal(false); onEnterSOC(); }}
                className="w-full p-3 rounded-lg bg-[#070B12] hover:bg-[#1E2A38] border border-[#00D9FF]/40 text-left transition flex items-center justify-between"
              >
                <div>
                  <p className="text-xs font-bold text-white">Dawit Mengistu</p>
                  <p className="text-[10px] text-[#00D9FF]">Security Analyst • Tier 2</p>
                </div>
                <ArrowRight className="w-4 h-4 text-[#00D9FF]" />
              </button>

              <button
                onClick={() => { setShowLoginModal(false); onEnterSOC(); }}
                className="w-full p-3 rounded-lg bg-[#070B12] hover:bg-[#1E2A38] border border-[#1E2A38] text-left transition flex items-center justify-between"
              >
                <div>
                  <p className="text-xs font-bold text-white">Sara Yohannes</p>
                  <p className="text-[10px] text-[#F59E0B]">SOC Manager • Approval Authority</p>
                </div>
                <ArrowRight className="w-4 h-4 text-[#7D8A99]" />
              </button>
            </div>

            <button
              onClick={() => setShowLoginModal(false)}
              className="w-full py-2 text-xs text-[#7D8A99] hover:text-white"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-[#1E2A38] py-6 px-6 text-center text-xs text-[#7D8A99] bg-[#070B12]">
        <p>© 2026 ETHIO-CYBERGUARD Contributors. Licensed under Apache-2.0. Built for National Cyber Defense.</p>
      </footer>
    </div>
  );
};
