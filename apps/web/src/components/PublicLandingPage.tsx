import React, { useState } from 'react';
import { 
  Shield, 
  ArrowRight, 
  Cpu, 
  Lock, 
  Building2, 
  Mail,
  Eye,
  EyeOff,
  Globe
} from 'lucide-react';
import { getTranslations } from '../utils/translations';
import type { Language } from '../utils/translations';

interface PublicLandingPageProps {
  onEnterSOC: () => void;
  language?: Language;
  onToggleLanguage?: () => void;
}

export const PublicLandingPage: React.FC<PublicLandingPageProps> = ({ 
  onEnterSOC,
  language = 'en',
  onToggleLanguage 
}) => {
  const [currentView, setCurrentView] = useState<'home' | 'about' | 'docs' | 'contact'>('home');
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [loginNotice, setLoginNotice] = useState('');

  const t = getTranslations(language);
  const isAm = language === 'am';

  const openLoginModal = () => {
    setLoginNotice('');
    setShowLoginPassword(false);
    setShowLoginModal(true);
  };

  const closeLoginModal = () => {
    setShowLoginModal(false);
    setLoginNotice('');
    setShowLoginPassword(false);
  };

  const handleLoginSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoginNotice(
      isAm 
        ? 'የመግቢያ ገጹ ዝግጁ ነው፤ ነገር ግን ከሰርቨር ጋር አልተገናኘም። የእርስዎ የይለፍ ቃል አልተላከም ወይም አልተቀመጠም።' 
        : 'The sign-in UI is ready, but authentication is not connected yet. Your credentials were not sent or stored.'
    );
  };

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
              {isAm ? 'ብሄራዊ የሳይበር ደህንነት' : 'National AI SOC/SIEM'}
            </span>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-6 text-xs text-[#7D8A99]">
          <button 
            onClick={() => setCurrentView('home')} 
            className={`hover:text-white transition ${currentView === 'home' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            {t.publicPage.navHome}
          </button>
          <button 
            onClick={() => setCurrentView('about')} 
            className={`hover:text-white transition ${currentView === 'about' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            {t.publicPage.navAbout}
          </button>
          <button 
            onClick={() => setCurrentView('docs')} 
            className={`hover:text-white transition ${currentView === 'docs' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            {t.publicPage.navDocs}
          </button>
          <button 
            onClick={() => setCurrentView('contact')} 
            className={`hover:text-white transition ${currentView === 'contact' ? 'text-[#00D9FF] font-bold' : ''}`}
          >
            {t.publicPage.navContact}
          </button>
        </nav>

        <div className="flex items-center space-x-3">
          {onToggleLanguage && (
            <button 
              onClick={onToggleLanguage}
              title="Toggle English / Amharic"
              className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-[#111923] hover:bg-[#1E2A38] border border-[#1E2A38] text-xs font-mono text-[#00D9FF] transition"
            >
              <Globe className="w-3.5 h-3.5" />
              <span className="font-bold">{language === 'en' ? 'EN' : 'አማ'}</span>
            </button>
          )}
          <button 
            onClick={openLoginModal}
            className="px-3.5 py-1.5 text-xs text-[#E6EDF3] hover:text-white bg-[#111923] border border-[#1E2A38] hover:border-[#00D9FF]/40 rounded-lg transition"
          >
            {t.banner.signIn}
          </button>
          <button 
            onClick={onEnterSOC}
            className="px-4 py-1.5 text-xs bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-bold rounded-lg transition flex items-center space-x-1.5 shadow-lg shadow-[#00D9FF]/20"
          >
            <span>{t.publicPage.ctaEnterSoc}</span>
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
                <span>{t.publicPage.heroBadge}</span>
              </div>

              <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                {t.publicPage.heroTitle} <br />
                <span className="text-[#00D9FF]">{t.publicPage.heroTitleHighlight}</span>
              </h1>

              <p className="text-sm sm:text-base text-[#7D8A99] leading-relaxed max-w-2xl mx-auto">
                {t.publicPage.heroSubtitle}
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
                <button 
                  onClick={onEnterSOC}
                  className="w-full sm:w-auto px-6 py-3 bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-extrabold text-sm rounded-xl transition flex items-center justify-center space-x-2 shadow-xl shadow-[#00D9FF]/25"
                >
                  <span>{t.publicPage.ctaEnterSoc}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => setCurrentView('docs')}
                  className="w-full sm:w-auto px-6 py-3 bg-[#111923] hover:bg-[#1E2A38] text-white border border-[#1E2A38] font-bold text-sm rounded-xl transition"
                >
                  {t.publicPage.ctaLearnMore}
                </button>
              </div>
            </div>

            {/* Core Feature Pillars */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#00D9FF]/40 transition">
                <div className="p-3 bg-[#00D9FF]/10 text-[#00D9FF] rounded-lg w-fit">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{t.publicPage.feature1Title}</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  {t.publicPage.feature1Desc}
                </p>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#FF1744]/40 transition">
                <div className="p-3 bg-[#FF1744]/10 text-[#FF1744] rounded-lg w-fit">
                  <Lock className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{t.publicPage.feature2Title}</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  {t.publicPage.feature2Desc}
                </p>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#22C55E]/40 transition">
                <div className="p-3 bg-[#22C55E]/10 text-[#22C55E] rounded-lg w-fit">
                  <Building2 className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{t.publicPage.feature3Title}</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  {t.publicPage.feature3Desc}
                </p>
              </div>
            </div>

            {/* Metrics Ribbon */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-[#111923] border border-[#1E2A38] rounded-2xl p-6 text-center">
              <div>
                <div className="text-3xl font-extrabold text-[#00D9FF] font-mono">{t.publicPage.statsEps}</div>
                <div className="text-xs text-[#7D8A99] mt-1">{t.publicPage.statsEpsLabel}</div>
              </div>
              <div className="border-t sm:border-t-0 sm:border-x border-[#1E2A38] pt-4 sm:pt-0">
                <div className="text-3xl font-extrabold text-white font-mono">{t.publicPage.statsAgents}</div>
                <div className="text-xs text-[#7D8A99] mt-1">{t.publicPage.statsAgentsLabel}</div>
              </div>
              <div className="border-t sm:border-t-0 border-[#1E2A38] pt-4 sm:pt-0">
                <div className="text-3xl font-extrabold text-[#22C55E] font-mono">{t.publicPage.statsPass}</div>
                <div className="text-xs text-[#7D8A99] mt-1">{t.publicPage.statsPassLabel}</div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'about' && (
          <div className="space-y-6 max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-white">
              {isAm ? 'ስለ ኢትዮ-ሳይበርጋርድ (ETHIO-CYBERGUARD)' : 'About ETHIO-CYBERGUARD'}
            </h2>
            <p className="text-xs sm:text-sm text-[#7D8A99] leading-relaxed">
              {isAm
                ? 'ዘመናዊ ኢንተርፕራይዞች፣ ባንኮች እና የመንግስት ተቋማት በየቀኑ በሚሊዮን የሚቆጠሩ የደህንነት ክስተቶችን ያመነጫሉ። እውነተኛውን የሳይበር ጥቃት ከዕለት ተዕለት እንቅስቃሴው ለይቶ ለማወቅ ከፍተኛ ብቃት ያለው የሳይበር ደህንነት ባለሙያ ያስፈልጋል። ኢትዮ-ሳይበርጋርድ ይህን ክፍተት በላቀ አርቴፊሻል ኢንተለጀንስ እና በሰለጠኑ ባለሙያዎች ቅንጅት ይሞላል።'
                : 'Modern enterprises and governmental institutions generate millions of security events daily from endpoints, routers, firewalls, and applications. Identifying true intrusions amidst normal noise requires scarce specialized expertise. ETHIO-CYBERGUARD bridges this gap.'}
            </p>
            <div className="bg-[#111923] border border-[#1E2A38] p-5 rounded-xl space-y-3">
              <h3 className="text-sm font-bold text-[#00D9FF]">
                {isAm ? 'ዋና ዋና ተጠቃሚ ተቋማት፡' : 'Target Stakeholders:'}
              </h3>
              <ul className="text-xs space-y-2 text-[#E6EDF3]">
                <li>• 🎓 {isAm ? 'ዩኒቨርሲቲዎች እና የከፍተኛ ትምህርት የምርምር ማዕከላት' : 'Universities and educational research faculties'}</li>
                <li>• 🏦 {isAm ? 'የኢትዮጵያ ንግድ ባንክ እና የግል የፋይናንስ ተቋማት' : 'Commercial Bank of Ethiopia (CBE) and financial institutions'}</li>
                <li>• 📱 {isAm ? 'ኢትዮ ቴሌኮም እና የቴሌብር ክፍያ ሥርዓት' : 'Ethio Telecom and Telebirr digital payment networks'}</li>
                <li>• ⚡ {isAm ? 'የኢትዮጵያ ኤሌክትሪክ ሃይል እና ወሳኝ መሰረተ-ልማቶች' : 'Ethiopian Electric Power and critical utility networks'}</li>
                <li>• 🏛️ {isAm ? 'የፌደራል እና የክልል የመንግስት ተቋማት' : 'Federal and regional governmental institutions'}</li>
              </ul>
            </div>
          </div>
        )}

        {currentView === 'docs' && (
          <div className="space-y-6 max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-white">
              {isAm ? 'ቴክኒካል ሰነዶች እና መግለጫዎች' : 'Technical Documentation & Schemas'}
            </h2>
            <p className="text-xs sm:text-sm text-[#7D8A99]">
              {isAm ? 'በፕሮጀክቱ ማህደር ውስጥ የተካተቱ ሙሉ የሲስተም መግለጫዎች፡' : 'Explore complete specifications in the repository:'}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">docs/architecture.md</span>
                <span className="text-[#7D8A99]">{isAm ? 'የሲስተም መዋቅር እና የECS ሎግ አሰባሰብ' : 'Overall pipeline and ECS normalization logic'}</span>
              </div>
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">docs/ai-architecture.md</span>
                <span className="text-[#7D8A99]">{isAm ? 'የ7ቱ ኤአይ ወኪሎች ስራ እና አወቃቀር' : 'The 7 specialized AI agents & prompt design'}</span>
              </div>
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">docs/api.md</span>
                <span className="text-[#7D8A99]">{isAm ? 'የFastAPI REST እና ዌብሰኬት ኤፒአይ' : 'FastAPI REST & WebSocket endpoints'}</span>
              </div>
              <div className="p-4 bg-[#111923] border border-[#1E2A38] rounded-lg">
                <span className="font-bold text-white block">database/schema.sql</span>
                <span className="text-[#7D8A99]">{isAm ? 'የPostgreSQL ዳታቤዝ ሰንጠረዦች እና RBAC' : 'PostgreSQL core DDL & RBAC definitions'}</span>
              </div>
            </div>
          </div>
        )}

        {currentView === 'contact' && (
          <div className="space-y-6 max-w-xl mx-auto bg-[#111923] border border-[#1E2A38] p-6 rounded-xl text-center">
            <Mail className="w-8 h-8 text-[#00D9FF] mx-auto" />
            <h2 className="text-xl font-bold text-white">
              {isAm ? 'የኢትዮ-ሳይበርጋርድ ግንኙነት አድራሻ' : 'Contact ETHIO-CYBERGUARD Team'}
            </h2>
            <p className="text-xs text-[#7D8A99]">
              {isAm ? 'ለትብብር፣ ለምርምር አጋርነት እና ለሳይበር ጥቃት ሪፖርት፡' : 'For collaboration, research partnerships, and incident disclosures:'}
            </p>
            <div className="p-4 bg-[#070B12] rounded-lg border border-[#1E2A38] text-xs font-mono text-[#00D9FF]">
              inquiries@ethio-cyberguard.et • Addis Ababa, Ethiopia
            </div>
          </div>
        )}
      </main>

      {/* Frontend Sign In Modal */}
      {showLoginModal && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) closeLoginModal();
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="login-modal-title"
            className="bg-[#111923] border border-[#1E2A38] rounded-xl max-w-sm w-full p-6 space-y-5 shadow-2xl"
          >
            <div className="text-center">
              <Shield className="w-8 h-8 text-[#00D9FF] mx-auto mb-2" />
              <h3 id="login-modal-title" className="text-base font-bold text-white">
                {isAm ? 'ወደ ኢትዮ-ሳይበርጋርድ ይግቡ' : 'Sign in to ETHIO-CYBERGUARD'}
              </h3>
              <p className="mt-1 text-[11px] text-[#7D8A99]">
                {isAm ? 'የመለያ መረጃዎን ያስገቡ።' : 'Enter your account details to preview the sign-in experience.'}
              </p>
            </div>

            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label htmlFor="login-email" className="block text-xs font-medium text-[#E6EDF3]">
                  {isAm ? 'የኢሜይል አድራሻ' : 'Email address'}
                </label>
                <div className="relative">
                  <Mail
                    aria-hidden="true"
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7D8A99]"
                  />
                  <input
                    id="login-email"
                    name="email"
                    type="email"
                    autoComplete="username"
                    required
                    value={loginEmail}
                    onChange={(event) => {
                      setLoginEmail(event.target.value);
                      setLoginNotice('');
                    }}
                    placeholder="you@example.com"
                    className="w-full rounded-lg border border-[#1E2A38] bg-[#070B12] py-2.5 pl-10 pr-3 text-sm text-white placeholder:text-[#526171] outline-none focus:border-[#00D9FF]"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="login-password" className="block text-xs font-medium text-[#E6EDF3]">
                  {isAm ? 'የይለፍ ቃል' : 'Password'}
                </label>
                <div className="relative">
                  <Lock
                    aria-hidden="true"
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7D8A99]"
                  />
                  <input
                    id="login-password"
                    name="password"
                    type={showLoginPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    minLength={8}
                    value={loginPassword}
                    onChange={(event) => {
                      setLoginPassword(event.target.value);
                      setLoginNotice('');
                    }}
                    placeholder={isAm ? 'የይለፍ ቃልዎን ያስገቡ' : 'Enter your password'}
                    className="w-full rounded-lg border border-[#1E2A38] bg-[#070B12] py-2.5 pl-10 pr-11 text-sm text-white placeholder:text-[#526171] outline-none focus:border-[#00D9FF]"
                  />
                  <button
                    type="button"
                    onClick={() => setShowLoginPassword((visible) => !visible)}
                    aria-label={showLoginPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1.5 text-[#7D8A99] hover:text-white"
                  >
                    {showLoginPassword ? (
                      <EyeOff aria-hidden="true" className="w-4 h-4" />
                    ) : (
                      <Eye aria-hidden="true" className="w-4 h-4" />
                    )}
                  </button>
                </div>
                <p className="text-[10px] text-[#7D8A99]">
                  {isAm ? 'ቢያንስ 8 ፊደላትን ይጠቀሙ።' : 'Use at least 8 characters for this form preview.'}
                </p>
              </div>

              {loginNotice && (
                <p role="status" className="rounded-lg border border-[#F59E0B]/30 bg-[#F59E0B]/10 p-3 text-[11px] leading-relaxed text-[#FCD34D]">
                  {loginNotice}
                </p>
              )}

              <button
                type="submit"
                className="w-full rounded-lg bg-[#00D9FF] py-2.5 text-xs font-bold text-black transition hover:bg-[#00D9FF]/80"
              >
                {isAm ? 'መግቢያውን ይሞክሩ' : 'Preview sign-in'}
              </button>
            </form>

            <button
              type="button"
              onClick={closeLoginModal}
              className="w-full py-1 text-xs text-[#7D8A99] hover:text-white"
            >
              {isAm ? 'ተመለስ' : 'Cancel'}
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-[#1E2A38] py-6 px-6 text-center text-xs text-[#7D8A99] bg-[#070B12]">
        <p>{t.publicPage.footerText}</p>
      </footer>
    </div>
  );
};
