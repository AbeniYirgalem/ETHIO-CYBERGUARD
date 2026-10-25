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
  Globe,
  Users,
  CheckCircle2,
  AlertTriangle,
  Terminal,
  ExternalLink,
  Server,
  Activity,
  Layers,
  Zap,
  BookOpen,
  PhoneCall,
  X
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
  const [selectedImageModal, setSelectedImageModal] = useState<{ src: string; alt: string; title: string } | null>(null);

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

  // 7 AI Agents Data
  const aiAgents = [
    {
      num: 1,
      name: isAm ? 'የክስተቶች ትንተና ወኪል' : 'Event Analysis Agent',
      code: 'event_analysis',
      role: isAm ? 'የክስተቶች ምደባ እና ያልተለመዱ ባህሪያትን መለየት' : 'MITRE ATT&CK taxonomy classification & anomaly detection',
      desc: isAm 
        ? 'ከዊንዶውስ፣ ሊኑክስ እና የፋየርዎል ሎጎች የሚመጡ ክስተቶችን በሰከንድ ውስጥ በመመርመር የጥቃት ምልክቶችን ከዕለት ተዕለት እንቅስቃሴ ይለያል።' 
        : 'Performs streaming anomaly scoring and maps security events into MITRE ATT&CK tactics (T1059, T1078, T1021).'
    },
    {
      num: 2,
      name: isAm ? 'የስጋት መረጃ ወኪል' : 'Threat Intelligence Agent',
      code: 'threat_intel',
      role: isAm ? 'አይኦሲ (IOC) እና ብሄራዊ የስጋት መረጃዎችን ማገናኘት' : 'Real-time IOC matching against STIX 2.1 & Ethio-CERT feeds',
      desc: isAm 
        ? 'አይፒ አድራሻዎችን፣ የዶሜይን ስሞችን እና የፋይል ሀሾችን ከኢትዮ-ሰርት እና ከዓለም አቀፍ የስጋት ዳታቤዞች ጋር በማመሳከር ያጣራል።' 
        : 'Cross-references network IPs, domains, and hashes against STIX 2.1 bundles and regional C2 telemetry.'
    },
    {
      num: 3,
      name: isAm ? 'የቅንጅት ትንተና ወኪል' : 'Correlation Agent',
      code: 'correlation',
      role: isAm ? 'የተበታተኑ ጥቃቶችን በግራፍ አገናኝቶ ሙሉውን የጥቃት ሰንሰለት መገንባት' : 'Graph-based correlation of multi-source telemetry into attack chains',
      desc: isAm 
        ? 'ከተለያዩ ሰርቨሮች የሚመጡ ጥቃቅን ጥቃቶችን በጋራ በማስተሳሰር የተቀናጀ የጥቃት ሰንሰለት (Kill Chain) መኖሩን ያረጋግጣል።' 
        : 'Constructs attack graph relationships connecting endpoint processes, lateral SMB movement, and outbound beaconing.'
    },
    {
      num: 4,
      name: isAm ? 'የምርመራ እና ፎረንሲክስ ወኪል' : 'Investigation Agent',
      code: 'investigation',
      role: isAm ? 'አውቶማቲክ ማስረጃ ማሰባሰብ እና የጉዳት ስፋት ትንተና' : 'Automated host triage, blast-radius scoping & forensic evidence capture',
      desc: isAm 
        ? 'ጥቃት የተፈጸመባቸውን ኮምፒውተሮች በመፈተሽ የተሰረቁ መረጃዎችን፣ የተጎዱ አካውንቶችን እና የጥቃቱን ስፋት ያሰላል።' 
        : 'Gathers forensic memory artifacts, open sockets, user logon audits, and generates tamper-evident evidence logs.'
    },
    {
      num: 5,
      name: isAm ? 'የስጋት ስሌት ወኪል' : 'Risk Assessment Agent',
      code: 'risk_assessment',
      role: isAm ? 'የተቋም ሀብት ክብደት እና ተጋላጭነት ሂሳባዊ ስሌት (0-100)' : 'Mathematical asset criticality and vulnerability weighting (0–100 score)',
      desc: isAm 
        ? 'የተጠቃው ሲስተም ለሀገር ኢኮኖሚ ወይም ለባንኩ ያለውን ወሳኝነት መሰረት በማድረግ ግልጽ የሆነ የስጋት ነጥብ ያሰላል።' 
        : 'Applies explainable multi-variable risk scoring combining asset tier, exposure, exploit availability, and impact.'
    },
    {
      num: 6,
      name: isAm ? 'የአመራር ሪፖርት ወኪል' : 'Executive Report Agent',
      code: 'executive_report',
      role: isAm ? 'ለቦርድ እና ለከፍተኛ አመራሮች የሚቀርብ ማጠቃለያ ማዘጋጀት' : 'Board-level executive briefings and post-mortem incident dossiers',
      desc: isAm 
        ? 'ውስብስብ የቴክኒክ ቋንቋዎችን ወደ ግልጽ የንግድ እና የስራ አመራር ሪፖርት በመቀየር ለውሳኔ ሰጪዎች በቅጽበት ያቀርባል።' 
        : 'Translates technical forensic telemetry into strategic risk summaries, business impact metrics, and compliance status.'
    },
    {
      num: 7,
      name: isAm ? 'የደህንነት ረዳት ወኪል' : 'Security Assistant Agent',
      code: 'assistant',
      role: isAm ? 'ከባለሙያዎች ጋር በንግግር የሚረዳ የሶክ ረዳት (SOC Copilot)' : 'Interactive Tier-1/Tier-2 analyst assistant with injection defense',
      desc: isAm 
        ? 'የደህንነት ተንታኞች ጥያቄዎችን እንዲጠይቁ፣ ሎጎችን እንዲፈትሹ እና ፈጣን የመከላከያ ሀሳቦችን እንዲያገኙ ያግዛል።' 
        : 'Provides conversational triage queries, containment recommendations, and withstands adversarial prompt injection.'
    }
  ];

  // Team Roster Data
  const teamMembers = [
    {
      num: 1,
      nameAm: 'ቤአምላክ ስንታየሁ',
      nameEn: 'Beamlak Sintayehu',
      studentId: 'CTC-912-24',
      roleAm: 'ዋና አባል እና አስተዋፅዖ አድራጊ',
      roleEn: 'Core Member / Contributor',
      badge: 'CTC-912-24',
      badgeColor: 'border-[#00D9FF] text-[#00D9FF] bg-[#00D9FF]/10',
      desc: isAm 
        ? 'የሲስተሙን ሙሉ ሙከራዎች፣ የUI/UX ውህደት እና የኢትዮ-ሳይበርጋርድን መዋቅር በመገንባት ከፍተኛ አስተዋፅዖ ያበረከተ።' 
        : 'Instrumental in architecture implementation, test engineering, and frontend integration.'
    },
    {
      num: 2,
      nameAm: 'ዮናስ አባዲ',
      nameEn: 'Yonas Abadi',
      studentId: '[የተማሪ መለያ: ____________]',
      roleAm: 'አስተዋፅዖ አድራጊ',
      roleEn: 'Contributor',
      badge: isAm ? 'አስተዋፅዖ አድራጊ' : 'Contributor',
      badgeColor: 'border-[#A855F7] text-[#A855F7] bg-[#A855F7]/10',
      desc: isAm 
        ? 'በስጋት መረጃ እና በምርመራ ወኪሎች ትንተና ላይ ተሳትፎ ያደረገ የቡድኑ አስተዋፅዖ አድራጊ።' 
        : 'Contributed to threat intelligence modeling and investigative workflow testing.'
    },
    {
      num: 3,
      nameAm: 'አቤኔዘር ይርጋለም',
      nameEn: 'Abenezer Yirgalem',
      studentId: 'CTC-041-26',
      roleAm: 'የፕሮጀክት አስተዳዳሪ እና መሪ',
      roleEn: 'Project Lead / Maintainer',
      badge: 'CTC-041-26',
      badgeColor: 'border-[#22C55E] text-[#22C55E] bg-[#22C55E]/10',
      desc: isAm 
        ? 'የኢትዮ-ሳይበርጋርድ ዋና መስራች፣ የFastAPI የጀርባ አሰራር እና የGitHub ሪፖዚተሪ አስተዳዳሪ።' 
        : 'System design architect, FastAPI backend orchestration, and repository management.'
    },
    {
      num: 4,
      nameAm: 'ፍቅረማርያም',
      nameEn: 'FikreMariam',
      studentId: '[የተማሪ መለያ: ____________]',
      roleAm: 'የቡድን አባል',
      roleEn: 'Team Member',
      badge: isAm ? 'የቡድን አባል' : 'Team Member',
      badgeColor: 'border-[#F59E0B] text-[#F59E0B] bg-[#F59E0B]/10',
      desc: isAm 
        ? 'የደህንነት ግንዛቤ ማስጨበጫ እና የፊሺንግ ሙከራ ሞዴሎችን በማዘጋጀት የተሳተፈ የቡድን አባል።' 
        : 'Security awareness campaign logic and educational simulation design.'
    },
    {
      num: 5,
      nameAm: 'ረመዳን',
      nameEn: 'Remedan',
      studentId: '[የተማሪ መለያ: ____________]',
      roleAm: 'የቡድን አባል',
      roleEn: 'Team Member',
      badge: isAm ? 'የቡድን አባል' : 'Team Member',
      badgeColor: 'border-[#F59E0B] text-[#F59E0B] bg-[#F59E0B]/10',
      desc: isAm 
        ? 'የኔትወርክ ጥቃቶች ቅኝት (OSINT) እና የብራንድ ጥበቃ ሞጁሎችን በማጠናቀር የተሳተፈ የቡድን አባል።' 
        : 'Network OSINT reconnaissance and typosquatting detection validation.'
    }
  ];

  return (
    <div className="min-h-screen bg-[#070B12] text-[#E6EDF3] flex flex-col font-sans selection:bg-[#00D9FF] selection:text-black">
      {/* Top Navbar */}
      <header className="border-b border-[#1E2A38] bg-[#070B12]/85 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentView('home')}>
          <div className="p-2 bg-[#00D9FF]/10 border border-[#00D9FF]/30 rounded-lg shadow-sm shadow-[#00D9FF]/20">
            <Shield className="w-5 h-5 text-[#00D9FF]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold tracking-wider text-base text-white">ETHIO-CYBERGUARD</span>
              <span className="hidden sm:inline-block text-[10px] font-mono px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
                v1.1.0 // {isAm ? 'ብሄራዊ የሳይበር ደህንነት' : 'National AI SOC'}
              </span>
            </div>
            <div className="text-[10px] text-[#7D8A99] font-mono">
              {isAm ? 'የኢትዮጵያ ወሳኝ መሰረተ-ልማቶች የሳይበር ጋሻ' : 'Critical Infrastructure Threat Intelligence'}
            </div>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-6 text-xs text-[#7D8A99]">
          <button 
            onClick={() => setCurrentView('home')} 
            className={`flex items-center space-x-1.5 transition pb-1 ${currentView === 'home' ? 'text-[#00D9FF] font-bold border-b-2 border-[#00D9FF]' : 'hover:text-white'}`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{t.publicPage.navHome}</span>
          </button>
          <button 
            onClick={() => setCurrentView('about')} 
            className={`flex items-center space-x-1.5 transition pb-1 ${currentView === 'about' ? 'text-[#00D9FF] font-bold border-b-2 border-[#00D9FF]' : 'hover:text-white'}`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>{t.publicPage.navAbout}</span>
          </button>
          <button 
            onClick={() => setCurrentView('docs')} 
            className={`flex items-center space-x-1.5 transition pb-1 ${currentView === 'docs' ? 'text-[#00D9FF] font-bold border-b-2 border-[#00D9FF]' : 'hover:text-white'}`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>{t.publicPage.navDocs}</span>
          </button>
          <button 
            onClick={() => setCurrentView('contact')} 
            className={`flex items-center space-x-1.5 transition pb-1 ${currentView === 'contact' ? 'text-[#00D9FF] font-bold border-b-2 border-[#00D9FF]' : 'hover:text-white'}`}
          >
            <PhoneCall className="w-3.5 h-3.5" />
            <span>{t.publicPage.navContact}</span>
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
            className="px-3.5 py-1.5 text-xs text-[#E6EDF3] hover:text-white bg-[#111923] border border-[#1E2A38] hover:border-[#00D9FF]/40 rounded-lg transition hidden sm:inline-flex"
          >
            {t.banner.signIn}
          </button>
          <button 
            onClick={onEnterSOC}
            className="px-4 py-1.5 text-xs bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-extrabold rounded-lg transition flex items-center space-x-1.5 shadow-lg shadow-[#00D9FF]/20"
          >
            <span>{t.publicPage.ctaEnterSoc}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Main Public Content */}
      <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 py-8 w-full">
        {/* ========================================================================= */}
        {/* VIEW 1: HOME / OVERVIEW */}
        {/* ========================================================================= */}
        {currentView === 'home' && (
          <div className="space-y-14">
            {/* Hero Section */}
            <div className="text-center max-w-3xl mx-auto space-y-6 pt-4">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#00D9FF]/10 border border-[#00D9FF]/30 text-[#00D9FF] text-xs font-mono">
                <span className="w-2 h-2 rounded-full bg-[#00D9FF] animate-pulse"></span>
                <span>{isAm ? 'የቀጥታ ብሄራዊ የደህንነት ዝግጁነት' : 'NATIONAL SOC DEFCON-2 // ELEVATED'}</span>
                <span className="text-[#7D8A99]">|</span>
                <span>279/279 {isAm ? 'ፈተናዎች ያለፉ' : 'Tests Passing'}</span>
              </div>

              <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
                {t.publicPage.heroTitle} <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00D9FF] via-[#38BDF8] to-[#22C55E]">
                  {t.publicPage.heroTitleHighlight}
                </span>
              </h1>

              <p className="text-xs sm:text-sm text-[#7D8A99] leading-relaxed max-w-2xl mx-auto">
                {t.publicPage.heroSubtitle}
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
                <button 
                  onClick={onEnterSOC}
                  className="w-full sm:w-auto px-6 py-3 bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-extrabold text-xs sm:text-sm rounded-xl transition flex items-center justify-center space-x-2 shadow-xl shadow-[#00D9FF]/25"
                >
                  <Activity className="w-4 h-4" />
                  <span>{t.publicPage.ctaEnterSoc}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => setCurrentView('docs')}
                  className="w-full sm:w-auto px-6 py-3 bg-[#111923] hover:bg-[#1E2A38] text-white border border-[#1E2A38] font-bold text-xs sm:text-sm rounded-xl transition flex items-center justify-center space-x-2"
                >
                  <BookOpen className="w-4 h-4 text-[#00D9FF]" />
                  <span>{t.publicPage.ctaLearnMore}</span>
                </button>
              </div>
            </div>

            {/* Metrics Ribbon */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-[#111923]/70 border border-[#1E2A38] rounded-2xl p-6 text-center shadow-lg">
              <div className="p-2">
                <div className="text-2xl sm:text-3xl font-black text-[#00D9FF] font-mono">51,240+</div>
                <div className="text-[11px] text-[#7D8A99] mt-1 font-medium">
                  {isAm ? 'በሰከንድ የሚጣሩ ክስተቶች (EPS)' : 'Events Per Second (EPS)'}
                </div>
              </div>
              <div className="p-2 border-l border-[#1E2A38]">
                <div className="text-2xl sm:text-3xl font-black text-[#A855F7] font-mono">7 AI AGENTS</div>
                <div className="text-[11px] text-[#7D8A99] mt-1 font-medium">
                  {isAm ? 'ልዩ የደህንነት ኤጀንቶች' : 'Specialized AI Orchestration'}
                </div>
              </div>
              <div className="p-2 border-t md:border-t-0 md:border-l border-[#1E2A38]">
                <div className="text-2xl sm:text-3xl font-black text-[#22C55E] font-mono">279 / 279</div>
                <div className="text-[11px] text-[#7D8A99] mt-1 font-medium">
                  {isAm ? 'ያለፉ አውቶማቲክ ፈተናዎች' : 'Automated Tests Passing'}
                </div>
              </div>
              <div className="p-2 border-t md:border-t-0 md:border-l border-[#1E2A38]">
                <div className="text-2xl sm:text-3xl font-black text-[#F59E0B] font-mono">10-STATE</div>
                <div className="text-[11px] text-[#7D8A99] mt-1 font-medium">
                  {isAm ? 'የአደጋ ቁጥጥር ሂደት' : 'Incident Lifecycle Engine'}
                </div>
              </div>
            </div>

            {/* Platform Showcase Screenshot */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                    <Activity className="w-5 h-5 text-[#00D9FF]" />
                    <span>{isAm ? 'የቀጥታ የሳይበር ቁጥጥር ማዕከል (SOC Dashboard)' : 'Live Interactive SOC Command Platform'}</span>
                  </h3>
                  <p className="text-xs text-[#7D8A99]">
                    {isAm 
                      ? 'የኢትዮጵያ ወሳኝ ተቋማት የደህንነት ክትትል፣ የቴሌብር እና የባንክ ጥበቃ በቅጽበት' 
                      : 'Real-time telemetry stream, MITRE ATT&CK correlation, and Amharic fraud heuristics'}
                  </p>
                </div>
                <button
                  onClick={onEnterSOC}
                  className="px-3 py-1.5 rounded-lg bg-[#00D9FF]/10 text-[#00D9FF] hover:bg-[#00D9FF]/20 border border-[#00D9FF]/30 text-xs font-mono transition flex items-center space-x-1.5"
                >
                  <span>{isAm ? 'ዳሽቦርዱን በቀጥታ ይክፈቱ' : 'Launch Full Screen'}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>

              <div 
                className="relative rounded-2xl border border-[#1E2A38] bg-[#111923] overflow-hidden group cursor-pointer shadow-2xl hover:border-[#00D9FF]/50 transition"
                onClick={() => setSelectedImageModal({
                  src: './images/soc-platform-hero.png',
                  alt: 'ETHIO-CYBERGUARD SOC Platform',
                  title: isAm ? 'የኢትዮ-ሳይበርጋርድ የሶክ ዳሽቦርድ አጠቃላይ እይታ' : 'ETHIO-CYBERGUARD Unified SOC Dashboard'
                })}
              >
                <img 
                  src="./images/soc-platform-hero.png" 
                  alt="ETHIO-CYBERGUARD SOC Platform" 
                  className="w-full h-auto object-cover rounded-2xl group-hover:scale-[1.01] transition duration-300"
                  onError={(e) => {
                    // Fallback to secondary preview if hero fails to load
                    (e.target as HTMLImageElement).src = './images/soc-dashboard-preview.png';
                  }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#070B12] via-transparent to-transparent opacity-60"></div>
                <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center text-xs text-white/90 bg-[#070B12]/80 backdrop-blur px-4 py-2.5 rounded-xl border border-[#1E2A38]">
                  <div className="flex items-center space-x-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#22C55E] animate-pulse"></span>
                    <span className="font-mono">{isAm ? 'የቀጥታ ስራ ላይ ያለ ዳሽቦርድ' : 'Operational Status: Production & Demo Active'}</span>
                  </div>
                  <span className="text-[11px] text-[#00D9FF] font-mono flex items-center space-x-1">
                    <Eye className="w-3.5 h-3.5" />
                    <span>{isAm ? 'በትልቁ ለመመልከት ይጫኑ' : 'Click to enlarge screenshot'}</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Core Feature Pillars */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#00D9FF]/40 transition shadow-lg">
                <div className="p-3 bg-[#00D9FF]/10 text-[#00D9FF] rounded-lg w-fit">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{t.publicPage.feature1Title}</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  {t.publicPage.feature1Desc}
                </p>
                <div className="pt-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
                    7 Multi-Agent Workers
                  </span>
                </div>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#FF1744]/40 transition shadow-lg">
                <div className="p-3 bg-[#FF1744]/10 text-[#FF1744] rounded-lg w-fit">
                  <Lock className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{t.publicPage.feature2Title}</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  {t.publicPage.feature2Desc}
                </p>
                <div className="pt-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#FF1744]/10 text-[#FF1744] border border-[#FF1744]/20">
                    INSA Directive 2026-04 Compliant
                  </span>
                </div>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-3 hover:border-[#22C55E]/40 transition shadow-lg">
                <div className="p-3 bg-[#22C55E]/10 text-[#22C55E] rounded-lg w-fit">
                  <Building2 className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{t.publicPage.feature3Title}</h3>
                <p className="text-xs text-[#7D8A99] leading-relaxed">
                  {t.publicPage.feature3Desc}
                </p>
                <div className="pt-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20">
                    Telebirr & CBE Fraud Shield
                  </span>
                </div>
              </div>
            </div>

            {/* Competitive Benchmark & Comparative Matrix */}
            <div className="space-y-6 pt-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                    <Zap className="w-5 h-5 text-[#00D9FF]" />
                    <span>{isAm ? 'የቴክኒክ ንጽጽር እና የብቃት ደረጃ' : 'Feature Benchmark & Comparative Matrix'}</span>
                  </h3>
                  <p className="text-xs text-[#7D8A99]">
                    {isAm 
                      ? 'ኢትዮ-ሳይበርጋርድ ከነባር ዓለም አቀፍ እና ክፍት የሶፍትዌር መድረኮች ጋር ያለው ንጽጽር' 
                      : 'Evaluation of ETHIO-CYBERGUARD against conventional and open-source cybersecurity frameworks'}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedImageModal({
                    src: './images/comparative-matrix.png',
                    alt: 'Comparative Matrix Diagram',
                    title: isAm ? 'የቴክኒክ ንጽጽር ቻርት' : 'Comparative Matrix Infographic'
                  })}
                  className="px-3 py-1.5 rounded-lg bg-[#111923] text-[#7D8A99] hover:text-white border border-[#1E2A38] text-xs font-mono transition flex items-center space-x-1.5"
                >
                  <Eye className="w-3.5 h-3.5 text-[#00D9FF]" />
                  <span>{isAm ? 'የንጽጽር ፎቶውን ተመልከት' : 'View Image Infographic'}</span>
                </button>
              </div>

              {/* Responsive Matrix Table */}
              <div className="border border-[#1E2A38] rounded-2xl overflow-hidden bg-[#111923] shadow-xl">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-[#1E2A38] bg-[#070B12]/80 text-[#7D8A99]">
                        <th className="py-3 px-4 font-mono font-bold text-white">
                          {isAm ? 'የአቅም / የደህንነት ባህሪ' : 'Capability / Feature'}
                        </th>
                        <th className="py-3 px-3 font-mono">ThePhish</th>
                        <th className="py-3 px-3 font-mono">openSquat</th>
                        <th className="py-3 px-3 font-mono">CyberSatark</th>
                        <th className="py-3 px-3 font-mono">SpiderFoot</th>
                        <th className="py-3 px-4 font-mono text-[#00D9FF] bg-[#00D9FF]/10 font-bold border-l border-[#00D9FF]/30">
                          ETHIO-CYBERGUARD
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1E2A38] text-[#E6EDF3]">
                      <tr className="hover:bg-[#1E2A38]/30 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          {isAm ? 'የሎግ አሰባሰብ ፍጥነት (EPS Throughput)' : 'Telemetry Ingestion Rate'}
                        </td>
                        <td className="py-3 px-3 text-[#7D8A99]">N/A (Email only)</td>
                        <td className="py-3 px-3 text-[#7D8A99]">N/A (Batch CLI)</td>
                        <td className="py-3 px-3 text-[#7D8A99]">~500 EPS</td>
                        <td className="py-3 px-3 text-[#7D8A99]">Low (Recon only)</td>
                        <td className="py-3 px-4 text-[#00D9FF] bg-[#00D9FF]/5 font-bold border-l border-[#00D9FF]/20">
                          51,240+ EPS (Sustained)
                        </td>
                      </tr>
                      <tr className="hover:bg-[#1E2A38]/30 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          {isAm ? 'አርቴፊሻል ኢንተለጀንስ ወኪሎች' : 'AI Security Orchestration'}
                        </td>
                        <td className="py-3 px-3 text-[#FF1744]">None</td>
                        <td className="py-3 px-3 text-[#FF1744]">None (Regex only)</td>
                        <td className="py-3 px-3 text-[#F59E0B]">Basic Rules</td>
                        <td className="py-3 px-3 text-[#FF1744]">None (Scraper)</td>
                        <td className="py-3 px-4 text-[#22C55E] bg-[#00D9FF]/5 font-bold border-l border-[#00D9FF]/20">
                          7 Specialized LLM Agents
                        </td>
                      </tr>
                      <tr className="hover:bg-[#1E2A38]/30 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          {isAm ? 'ባለሁለት-ደረጃ ማጽደቂያ (SOAR Gate)' : 'Dual-Custody Human Approval'}
                        </td>
                        <td className="py-3 px-3 text-[#FF1744]">No SOAR</td>
                        <td className="py-3 px-3 text-[#FF1744]">No SOAR</td>
                        <td className="py-3 px-3 text-[#FF1744]">Single Admin</td>
                        <td className="py-3 px-3 text-[#FF1744]">No Containment</td>
                        <td className="py-3 px-4 text-[#22C55E] bg-[#00D9FF]/5 font-bold border-l border-[#00D9FF]/20">
                          Enforced (INSA Compliant)
                        </td>
                      </tr>
                      <tr className="hover:bg-[#1E2A38]/30 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          {isAm ? 'የኢትዮጵያ ስጋቶች ትንተና (Ethio-CERT/INSA)' : 'Ethiopian Regional Threat Intel'}
                        </td>
                        <td className="py-3 px-3 text-[#FF1744]">No</td>
                        <td className="py-3 px-3 text-[#FF1744]">No</td>
                        <td className="py-3 px-3 text-[#FF1744]">India-specific only</td>
                        <td className="py-3 px-3 text-[#7D8A99]">Generic OSINT</td>
                        <td className="py-3 px-4 text-[#00D9FF] bg-[#00D9FF]/5 font-bold border-l border-[#00D9FF]/20">
                          Native (Telebirr/CBE/AS24757)
                        </td>
                      </tr>
                      <tr className="hover:bg-[#1E2A38]/30 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          {isAm ? 'የአማርኛ የፊሺንግ እና የማጭበርበሪያ ቃላት' : 'Amharic / Ge\'ez NLP Phishing'}
                        </td>
                        <td className="py-3 px-3 text-[#FF1744]">No</td>
                        <td className="py-3 px-3 text-[#FF1744]">No</td>
                        <td className="py-3 px-3 text-[#FF1744]">Hindi only</td>
                        <td className="py-3 px-3 text-[#FF1744]">No</td>
                        <td className="py-3 px-4 text-[#22C55E] bg-[#00D9FF]/5 font-bold border-l border-[#00D9FF]/20">
                          Full Ge'ez NLP & Homoglyph
                        </td>
                      </tr>
                      <tr className="hover:bg-[#1E2A38]/30 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          {isAm ? 'አውቶማቲክ የሶፍትዌር ፈተናዎች' : 'Automated Verification Tests'}
                        </td>
                        <td className="py-3 px-3 text-[#7D8A99]">Unspecified</td>
                        <td className="py-3 px-3 text-[#7D8A99]">Minimal</td>
                        <td className="py-3 px-3 text-[#7D8A99]">12 tests</td>
                        <td className="py-3 px-3 text-[#7D8A99]">Partial unit</td>
                        <td className="py-3 px-4 text-[#22C55E] bg-[#00D9FF]/5 font-bold border-l border-[#00D9FF]/20">
                          279 / 279 Tests (100% Pass)
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 2: ABOUT & MISSION */}
        {/* ========================================================================= */}
        {currentView === 'about' && (
          <div className="space-y-12 max-w-4xl mx-auto">
            {/* Mission Statement */}
            <div className="space-y-4">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#00D9FF]/10 border border-[#00D9FF]/30 text-[#00D9FF] text-xs font-mono">
                <Shield className="w-3.5 h-3.5" />
                <span>{isAm ? 'ብሄራዊ ተልዕኮ እና ራዕይ' : 'National Defense Mission & Vision'}</span>
              </div>
              <h2 className="text-3xl font-extrabold text-white">
                {isAm ? 'የኢትዮ-ሳይበርጋርድ ብሄራዊ ተልዕኮ' : 'Defending Ethiopian Critical Digital Sovereignty'}
              </h2>
              <p className="text-xs sm:text-sm text-[#7D8A99] leading-relaxed">
                {isAm
                  ? 'ኢትዮ-ሳይበርጋርድ (ETHIO-CYBERGUARD) የተመሰረተው የኢትዮጵያን ዲጂታል ምህዳር፣ የፋይናንስ ተቋማትን፣ ቴሌኮሙኒኬሽንን፣ የኤሌክትሪክ ሃይልን እና ወሳኝ የመንግስት መረቦችን ከተራቀቁ የሳይበር ጥቃቶች ለመከላከል ነው። የሀገር ውስጥ የስጋት አውዶችን (የቴሌብር ማጭበርበር፣ የአማርኛ ፊሺንግ፣ የኢትዮ-ቴሌኮም ኤኤስኤን መረቦች) ከዓለም አቀፍ የላቁ አርቴፊሻል ኢንተለጀንስ ሞዴሎች ጋር በማቀናጀት ተወዳዳሪ የሌለው ብሄራዊ ጋሻ ያቀርባል።'
                  : 'ETHIO-CYBERGUARD is an autonomous enterprise cybersecurity platform designed to defend corporate, financial, governmental, and critical infrastructure networks across Ethiopia. It unifies high-throughput SIEM log telemetry ingestion, real-time SIGMA detection, automated MITRE ATT&CK correlation, multi-agent AI incident investigation, and human-in-the-loop SOAR response workflows.'}
              </p>
            </div>

            {/* Target Stakeholders */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-[#111923] border border-[#1E2A38] p-5 rounded-xl space-y-2">
                <div className="text-sm font-bold text-[#00D9FF] flex items-center space-x-2">
                  <Building2 className="w-4 h-4" />
                  <span>{isAm ? 'የፋይናንስ እና የባንክ ተቋማት' : 'Banking & Financial Sector'}</span>
                </div>
                <p className="text-xs text-[#7D8A99]">
                  {isAm 
                    ? 'የኢትዮጵያ ንግድ ባንክ (CBE)፣ አዋሽ ባንክ፣ ዳሽን ባንክ እና ቴሌብር ዲጂታል ክፍያዎችን ከተራቀቁ የገንዘብ ማጭበርበሮች እና የሰርቨር ጥቃቶች መጠበቅ።' 
                    : 'Targeted defenses for Commercial Bank of Ethiopia (CBE), Awash Bank, Dashen Bank, Chapa, and Telebirr mobile wallet transactions.'}
                </p>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] p-5 rounded-xl space-y-2">
                <div className="text-sm font-bold text-[#22C55E] flex items-center space-x-2">
                  <Server className="w-4 h-4" />
                  <span>{isAm ? 'ቴሌኮም እና ወሳኝ መሰረተ-ልማቶች' : 'Telecommunications & Critical Utilities'}</span>
                </div>
                <p className="text-xs text-[#7D8A99]">
                  {isAm 
                    ? 'ኢትዮ ቴሌኮም (AS24757)፣ ሳፋሪኮም ኢትዮጵያ እና የኢትዮጵያ ኤሌክትሪክ ሃይል ዋና ማስተላለፊያዎችን ከተቀናጁ የዲዶስ (DDoS) ጥቃቶች መከላከል' 
                    : 'Real-time telemetry scrubbing for Ethio Telecom (AS24757), Safaricom Ethiopia (AS329340), and Ethiopian Electric Power grid SCADA systems.'}
                </p>
              </div>
            </div>

            {/* 7 AI Agents Breakdown */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Cpu className="w-5 h-5 text-[#00D9FF]" />
                <h3 className="text-lg font-bold text-white">
                  {isAm ? 'የ7ቱ ልዩ የኤአይ ወኪሎች የስራ ድርሻ' : 'The 7 Specialized AI Security Agents'}
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {aiAgents.map((agent) => (
                  <div key={agent.code} className="bg-[#111923] border border-[#1E2A38] p-4 rounded-xl space-y-1.5 hover:border-[#00D9FF]/40 transition">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-white">
                        {agent.num}. {agent.name}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
                        {agent.code}
                      </span>
                    </div>
                    <div className="text-[11px] text-[#00D9FF] font-medium">{agent.role}</div>
                    <p className="text-[11px] text-[#7D8A99] leading-relaxed">{agent.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Team Roster & Photo Section */}
            <div className="space-y-6 pt-4 border-t border-[#1E2A38]">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                    <Users className="w-5 h-5 text-[#00D9FF]" />
                    <span>{isAm ? 'የፕሮጀክቱ ቡድን አባላት እና አስተዋፅዖ አድራጊዎች' : 'Project Team & Contributors'}</span>
                  </h3>
                  <p className="text-xs text-[#7D8A99]">
                    {isAm 
                      ? 'የኢትዮ-ሳይበርጋርድ የምርምር እና የሶፍትዌር ልማት ቡድን አባላት' 
                      : 'Software engineering, cybersecurity research, and deployment core team'}
                  </p>
                </div>
                <div className="text-[11px] font-mono text-[#00D9FF] px-2.5 py-1 rounded bg-[#00D9FF]/10 border border-[#00D9FF]/20">
                  {isAm ? 'የተማሪ ቡድን' : 'Student Research Team'}
                </div>
              </div>

              {/* Team Photo Card */}
              <div className="bg-[#111923] border border-[#1E2A38] rounded-2xl p-6 flex flex-col md:flex-row items-center gap-6 shadow-xl">
                <div 
                  className="w-full md:w-56 flex-shrink-0 cursor-pointer overflow-hidden rounded-xl border border-[#1E2A38] group relative"
                  onClick={() => setSelectedImageModal({
                    src: './images/team-photo.png',
                    alt: 'ETHIO-CYBERGUARD Team Photo',
                    title: isAm ? 'የኢትዮ-ሳይበርጋርድ የፕሮጀክት ቡድን ፎቶ' : 'ETHIO-CYBERGUARD Project Team'
                  })}
                >
                  <img 
                    src="./images/team-photo.png" 
                    alt="ETHIO-CYBERGUARD Team" 
                    className="w-full h-auto object-cover group-hover:scale-105 transition duration-300"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                    <span className="text-xs text-white bg-black/70 px-2 py-1 rounded font-mono flex items-center space-x-1">
                      <Eye className="w-3 h-3 text-[#00D9FF]" />
                      <span>{isAm ? 'ፎቶውን ይመልከቱ' : 'Enlarge'}</span>
                    </span>
                  </div>
                </div>

                <div className="space-y-3 flex-1 text-xs">
                  <div className="font-bold text-white text-sm">
                    {isAm ? 'የኢትዮ-ሳይበርጋርድ የምርምር ቡድን' : 'ETHIO-CYBERGUARD Student Research Collective'}
                  </div>
                  <p className="text-[#7D8A99] leading-relaxed">
                    {isAm
                      ? 'ይህ ፕሮጀክት የተገነባው በሳይበር ደህንነት እና በሶፍትዌር ኢንጂነሪንግ ተማሪዎች ቅንጅት ሲሆን፣ የሀገራችንን ወሳኝ ተቋማት ከተራቀቁ ጥቃቶች የሚከላከል ዘመናዊ ሲስተም ለመገንባት ያለመ ነው።'
                      : 'Dedicated student engineering cohort researching next-generation autonomous AI SIEM, localized Amharic threat intelligence, and human-in-the-loop critical infrastructure defense.'}
                  </p>
                  <div className="p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] text-[11px] text-[#A855F7] font-mono">
                    🎓 {isAm ? 'የቡድን አባላት መለያዎች (IDs) ከዚህ በታች ባለው ሰንጠረዥ በይፋ ተመዝግበዋል።' : 'Official student member IDs and designated roles recorded below.'}
                  </div>
                </div>
              </div>

              {/* Team Members List */}
              <div className="border border-[#1E2A38] rounded-xl overflow-hidden bg-[#111923]">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-[#1E2A38] bg-[#070B12] text-[#7D8A99] font-mono">
                      <th className="py-3 px-4">#</th>
                      <th className="py-3 px-4">{isAm ? 'ሙሉ ስም (Full Name)' : 'Full Name'}</th>
                      <th className="py-3 px-4">{isAm ? 'የተማሪ መለያ (Student ID)' : 'Student / Member ID'}</th>
                      <th className="py-3 px-4">{isAm ? 'የስራ ድርሻ (Role)' : 'Role'}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1E2A38] text-[#E6EDF3]">
                    {teamMembers.map((member) => (
                      <tr key={member.num} className="hover:bg-[#1E2A38]/30 transition">
                        <td className="py-3 px-4 font-mono text-[#7D8A99]">{member.num}</td>
                        <td className="py-3 px-4 font-bold text-white">
                          <div>{isAm ? member.nameAm : member.nameEn}</div>
                          <div className="text-[10px] text-[#7D8A99] font-normal">{member.nameEn}</div>
                        </td>
                        <td className="py-3 px-4 font-mono font-bold">
                          {member.studentId.startsWith('CTC-') ? (
                            <span className="px-2 py-0.5 rounded bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/30">
                              {member.studentId}
                            </span>
                          ) : (
                            <span className="text-[#526171] italic">{member.studentId}</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${member.badgeColor}`}>
                            {isAm ? member.roleAm : member.roleEn}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 3: DOCUMENTATION */}
        {/* ========================================================================= */}
        {currentView === 'docs' && (
          <div className="space-y-12 max-w-4xl mx-auto">
            {/* Docs Header */}
            <div className="space-y-3">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#00D9FF]/10 border border-[#00D9FF]/30 text-[#00D9FF] text-xs font-mono">
                <BookOpen className="w-3.5 h-3.5" />
                <span>{isAm ? 'ቴክኒካል ዝርዝር እና መመሪያዎች' : 'Architecture & Technical Specifications'}</span>
              </div>
              <h2 className="text-3xl font-extrabold text-white">
                {isAm ? 'የሲስተሙ አጠቃላይ መዋቅር እና ኤፒአይ' : 'System Architecture & API Catalog'}
              </h2>
              <p className="text-xs sm:text-sm text-[#7D8A99] leading-relaxed">
                {isAm 
                  ? 'የኢትዮ-ሳይበርጋርድ የመረጃ አሰባሰብ መስመር፣ ባለሁለት-ደረጃ የSOAR ማጽደቂያ፣ የ10-ደረጃ አደጋ ቁጥጥር እና የFastAPI ኤንድፖይንቶች ዝርዝር።' 
                  : 'Deep dive into ECS telemetry normalization, 148 SIGMA rules, 10-state incident state machine, dual-custody containment, and core REST APIs.'}
              </p>
            </div>

            {/* Architecture Pipeline Flow */}
            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-4 shadow-lg">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Layers className="w-5 h-5 text-[#00D9FF]" />
                <span>{isAm ? 'የመረጃ ፍተሻ እና ትንተና መስመር (Pipeline Flow)' : 'End-to-End Processing Pipeline'}</span>
              </h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] space-y-1">
                  <div className="text-[#00D9FF] font-bold font-mono">1. Telemetry Ingestion</div>
                  <p className="text-[11px] text-[#7D8A99]">Windows Sysmon, Linux Auditd, Syslog UDP 5140, Inbound MTA</p>
                </div>
                <div className="p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] space-y-1">
                  <div className="text-[#22C55E] font-bold font-mono">2. ECS Normalizer</div>
                  <p className="text-[11px] text-[#7D8A99]">Elastic Common Schema parsing, SHA-256 deduplication, DLQ fallback</p>
                </div>
                <div className="p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] space-y-1">
                  <div className="text-[#A855F7] font-bold font-mono">3. Detection & Graph</div>
                  <p className="text-[11px] text-[#7D8A99]">148 SIGMA rules evaluator + MITRE ATT&CK correlation graph</p>
                </div>
                <div className="p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] space-y-1">
                  <div className="text-[#F59E0B] font-bold font-mono">4. Dual-Custody SOAR</div>
                  <p className="text-[11px] text-[#7D8A99]">Human analyst approval, 30-min expiration, automated rollback</p>
                </div>
              </div>
            </div>

            {/* 10-State Incident Lifecycle */}
            <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-6 space-y-4 shadow-lg">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Activity className="w-5 h-5 text-[#22C55E]" />
                <span>{isAm ? 'የ10-ደረጃ የአደጋ ቁጥጥር ሂደት (10-State Lifecycle)' : '10-State Incident Lifecycle Engine'}</span>
              </h3>
              <p className="text-xs text-[#7D8A99]">
                {isAm 
                  ? 'እያንዳንዱ የሳይበር አደጋ መነሻው ከታወቀበት እስከሚዘጋ ድረስ ጥብቅ የደህንነት ደረጃዎችን ያልፋል፡' 
                  : 'Every incident follows a deterministic state machine strictly audited for enterprise compliance:'}
              </p>
              <div className="flex flex-wrap gap-2 text-xs font-mono">
                {[
                  { state: 'NEW', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20' },
                  { state: 'TRIAGED', color: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' },
                  { state: 'ANALYZING', color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' },
                  { state: 'CORRELATED', color: 'bg-purple-500/10 text-purple-400 border-purple-500/20' },
                  { state: 'INVESTIGATING', color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' },
                  { state: 'CONTAINMENT_PROPOSED', color: 'bg-orange-500/10 text-orange-400 border-orange-500/20' },
                  { state: 'CONTAINED', color: 'bg-red-500/10 text-red-400 border-red-500/20' },
                  { state: 'REMEDIATING', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
                  { state: 'RESOLVED', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
                  { state: 'CLOSED', color: 'bg-green-500/10 text-green-400 border-green-500/20' },
                ].map((s, idx) => (
                  <div key={s.state} className="flex items-center space-x-1">
                    <span className={`px-2.5 py-1 rounded border text-[11px] ${s.color}`}>
                      {idx + 1}. {s.state}
                    </span>
                    {idx < 9 && <span className="text-[#526171]">→</span>}
                  </div>
                ))}
              </div>
            </div>

            {/* Dual-Custody SOAR Rule Box */}
            <div className="bg-[#FF1744]/5 border border-[#FF1744]/30 rounded-xl p-5 space-y-2">
              <div className="flex items-center space-x-2 text-sm font-bold text-[#FF1744]">
                <AlertTriangle className="w-4 h-4" />
                <span>{isAm ? 'የባለሁለት-ደረጃ ማጽደቂያ ህግጋት (Dual-Custody SOAR Controls)' : 'Dual-Custody Containment Protection Guardrails'}</span>
              </div>
              <p className="text-xs text-[#E6EDF3] leading-relaxed">
                {isAm 
                  ? 'የኢትዮጵያ ወሳኝ ሲስተሞችን ከኔትወርክ ማግለል (Isolate Host)፣ አይፒ አድራሻን ማገድ (Block IP) እና አካውንት ማገድን የመሳሰሉ እርምጃዎች የሰው ማረጋገጫ ይፈልጋሉ። እርምጃውን የጠየቀ ባለሙያ ራሱ ማጽደቅ አይችልም። እርምጃው በ30 ደቂቃ ውስጥ ካልጸደቀ በራሱ ጊዜ ይሰረዛል።'
                  : 'Destructive mitigation playbooks require certified Security Analyst sign-off. Anti-self-approval is cryptographically enforced. Actions automatically expire after 30 minutes if unapproved, and every execution maintains a tamper-evident SHA-256 audit ledger with instant rollback capability.'}
              </p>
            </div>

            {/* Core API Catalog */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Terminal className="w-5 h-5 text-[#00D9FF]" />
                <h3 className="text-lg font-bold text-white">
                  {isAm ? 'ዋና ዋና የFastAPI ኤፒአይ ኤንድፖይንቶች' : 'Core API Endpoints Catalog'}
                </h3>
              </div>
              <div className="border border-[#1E2A38] rounded-xl overflow-hidden bg-[#111923]">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-[#1E2A38] bg-[#070B12] text-[#7D8A99] font-mono">
                      <th className="py-2.5 px-3">Method</th>
                      <th className="py-2.5 px-3">Endpoint</th>
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Purpose</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1E2A38] text-[#E6EDF3] font-mono text-[11px]">
                    <tr className="hover:bg-[#1E2A38]/30">
                      <td className="py-2.5 px-3 text-[#22C55E] font-bold">POST</td>
                      <td className="py-2.5 px-3 text-white">/api/auth/login</td>
                      <td className="py-2.5 px-3 text-[#7D8A99]">Auth</td>
                      <td className="py-2.5 px-3 text-[#7D8A99] font-sans">JWT login with refresh rotation</td>
                    </tr>
                    <tr className="hover:bg-[#1E2A38]/30">
                      <td className="py-2.5 px-3 text-[#22C55E] font-bold">POST</td>
                      <td className="py-2.5 px-3 text-white">/api/v1/events/ingest</td>
                      <td className="py-2.5 px-3 text-[#7D8A99]">Ingest</td>
                      <td className="py-2.5 px-3 text-[#7D8A99] font-sans">51k+ EPS collector endpoint with DLQ</td>
                    </tr>
                    <tr className="hover:bg-[#1E2A38]/30">
                      <td className="py-2.5 px-3 text-[#00D9FF] font-bold">GET</td>
                      <td className="py-2.5 px-3 text-white">/api/incidents</td>
                      <td className="py-2.5 px-3 text-[#7D8A99]">Incidents</td>
                      <td className="py-2.5 px-3 text-[#7D8A99] font-sans">Active incidents with tenant isolation</td>
                    </tr>
                    <tr className="hover:bg-[#1E2A38]/30">
                      <td className="py-2.5 px-3 text-[#F59E0B] font-bold">PATCH</td>
                      <td className="py-2.5 px-3 text-white">/api/incidents/{'{id}'}/transition</td>
                      <td className="py-2.5 px-3 text-[#7D8A99]">Lifecycle</td>
                      <td className="py-2.5 px-3 text-[#7D8A99] font-sans">Formal state machine transition</td>
                    </tr>
                    <tr className="hover:bg-[#1E2A38]/30">
                      <td className="py-2.5 px-3 text-[#22C55E] font-bold">POST</td>
                      <td className="py-2.5 px-3 text-white">/api/phishing/analyze</td>
                      <td className="py-2.5 px-3 text-[#7D8A99]">Forensics</td>
                      <td className="py-2.5 px-3 text-[#7D8A99] font-sans">SPF/DKIM/DMARC & Amharic lure scan</td>
                    </tr>
                    <tr className="hover:bg-[#1E2A38]/30">
                      <td className="py-2.5 px-3 text-[#22C55E] font-bold">POST</td>
                      <td className="py-2.5 px-3 text-white">/api/response/execute</td>
                      <td className="py-2.5 px-3 text-[#7D8A99]">SOAR</td>
                      <td className="py-2.5 px-3 text-[#7D8A99] font-sans">Dual-custody action dispatch</td>
                    </tr>
                    <tr className="hover:bg-[#1E2A38]/30">
                      <td className="py-2.5 px-3 text-[#00D9FF] font-bold">GET</td>
                      <td className="py-2.5 px-3 text-white">/health/ready</td>
                      <td className="py-2.5 px-3 text-[#7D8A99]">Probes</td>
                      <td className="py-2.5 px-3 text-[#7D8A99] font-sans">PostgreSQL & Redis readiness probe</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Test Suite Verification Card */}
            <div className="bg-[#111923] border border-[#22C55E]/30 rounded-xl p-5 flex items-center justify-between">
              <div className="space-y-1">
                <div className="text-sm font-bold text-white flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
                  <span>279 / 279 Automated Pytest Suite (100% Green)</span>
                </div>
                <p className="text-xs text-[#7D8A99]">
                  {isAm 
                    ? 'ሁሉም የዩኒት፣ የኢንተግሬሽን፣ የኤአይ እና የደህንነት ፈተናዎች ሙሉ በሙሉ በተሳካ ሁኔታ አልፈዋል።' 
                    : 'Comprehensive coverage: unit, pipeline integration, prompt-injection, tenant isolation, and audit scenarios.'}
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-[#22C55E] bg-[#22C55E]/10 px-3 py-1.5 rounded-lg border border-[#22C55E]/30">
                100% PASS
              </span>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 4: CONTACT & INSA */}
        {/* ========================================================================= */}
        {currentView === 'contact' && (
          <div className="space-y-8 max-w-3xl mx-auto">
            <div className="space-y-3 text-center">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#00D9FF]/10 border border-[#00D9FF]/30 text-[#00D9FF] text-xs font-mono mx-auto">
                <PhoneCall className="w-3.5 h-3.5" />
                <span>{isAm ? 'ይፋዊ ግንኙነት እና የኢንሳ መመሪያ' : 'Official Channels & INSA Directives'}</span>
              </div>
              <h2 className="text-3xl font-extrabold text-white">
                {isAm ? 'የኢንሳ መመሪያ እና የኢትዮ-ሰርት ግንኙነት' : 'INSA Regulatory & Incident Disclosure'}
              </h2>
              <p className="text-xs sm:text-sm text-[#7D8A99] leading-relaxed max-w-xl mx-auto">
                {isAm
                  ? 'የኢትዮ-ሳይበርጋርድ መድረክ ከኢንፎርሜሽን መረብ ደህንነት አስተዳደር (ኢንሳ) የደህንነት መመሪያዎች ጋር የተጣጣመ ሲሆን፣ ለማንኛውም አደጋ ጥቆማ እና ትብብር ዝግጁ ነው።'
                  : 'Aligned with the Information Network Security Administration (INSA) national cybersecurity framework and Ethio-CERT emergency coordination procedures.'}
              </p>
            </div>

            {/* INSA & Emergency Hotline Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-[#111923] border border-[#1E2A38] p-5 rounded-xl space-y-3">
                <div className="text-sm font-bold text-[#00D9FF] flex items-center space-x-2">
                  <Shield className="w-4 h-4" />
                  <span>{isAm ? 'የኢንሳ የሳይበር አደጋ ሪፖርት' : 'Ethio-CERT Emergency Contact'}</span>
                </div>
                <div className="space-y-2 text-xs text-[#E6EDF3]">
                  <div><strong>Hotline / ስልክ:</strong> <span className="font-mono text-[#00D9FF]">8888 / 933</span></div>
                  <div><strong>Email:</strong> <span className="font-mono text-[#00D9FF]">cert@insa.gov.et</span></div>
                  <div><strong>Portal:</strong> <span className="font-mono text-[#7D8A99]">https://insa.gov.et</span></div>
                  <div className="text-[11px] text-[#7D8A99] pt-1">
                    {isAm ? 'ለብሄራዊ ወሳኝ መሰረተ-ልማቶች የ24/7 ፈጣን ምላሽ ማዕከል' : '24/7 National Cyber Incident Reporting & Triage'}
                  </div>
                </div>
              </div>

              <div className="bg-[#111923] border border-[#1E2A38] p-5 rounded-xl space-y-3">
                <div className="text-sm font-bold text-[#22C55E] flex items-center space-x-2">
                  <Mail className="w-4 h-4" />
                  <span>{isAm ? 'የኢትዮ-ሳይበርጋርድ የፕሮጀክት ግንኙነት' : 'ETHIO-CYBERGUARD Research Desk'}</span>
                </div>
                <div className="space-y-2 text-xs text-[#E6EDF3]">
                  <div><strong>General Inquiries:</strong> <span className="font-mono text-[#00D9FF]">inquiries@ethio-cyberguard.et</span></div>
                  <div><strong>Location:</strong> <span className="font-mono text-white">Addis Ababa, Ethiopia (አዲስ አበባ)</span></div>
                  <div><strong>License:</strong> <span className="font-mono text-[#7D8A99]">Apache-2.0 Open Source</span></div>
                  <div className="text-[11px] text-[#7D8A99] pt-1">
                    {isAm ? 'የዩኒቨርሲቲ እና የባንኮች የሙከራ አጋርነት' : 'Academic & Institutional Proof-of-Concept Inquiries'}
                  </div>
                </div>
              </div>
            </div>

            {/* Repositories & Mirrors */}
            <div className="bg-[#111923] border border-[#1E2A38] p-5 rounded-xl space-y-3">
              <div className="text-sm font-bold text-white flex items-center space-x-2">
                <Globe className="w-4 h-4 text-[#00D9FF]" />
                <span>{isAm ? 'የGitHub ሪፖዚተሪዎች እና የቀጥታ ማሳያዎች' : 'Public GitHub Repositories & Live Mirrors'}</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] gap-2">
                  <div>
                    <span className="font-bold text-white block">AbeniYirgalem / ETHIO-CYBERGUARD (Upstream)</span>
                    <span className="text-[11px] text-[#7D8A99]">Main source repository and core CI/CD engine</span>
                  </div>
                  <a 
                    href="https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD" 
                    target="_blank" 
                    rel="noreferrer"
                    className="text-[#00D9FF] hover:underline font-mono text-[11px] flex items-center space-x-1"
                  >
                    <span>Visit Repo</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] gap-2">
                  <div>
                    <span className="font-bold text-white block">Mr-Nobody-Anonymous / ETHIO-CYBERGUARD (Live Deployment)</span>
                    <span className="text-[11px] text-[#7D8A99]">Active GitHub Pages hosting target</span>
                  </div>
                  <a 
                    href="https://mr-nobody-anonymous.github.io/ETHIO-CYBERGUARD/" 
                    target="_blank" 
                    rel="noreferrer"
                    className="text-[#00D9FF] hover:underline font-mono text-[11px] flex items-center space-x-1"
                  >
                    <span>Open Live Pages</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ========================================================================= */}
      {/* IMAGE ENLARGEMENT MODAL */}
      {/* ========================================================================= */}
      {selectedImageModal && (
        <div 
          className="fixed inset-0 bg-black/90 flex items-center justify-center p-4 z-50 backdrop-blur-sm"
          onClick={() => setSelectedImageModal(null)}
        >
          <div 
            className="bg-[#111923] border border-[#1E2A38] rounded-2xl max-w-4xl w-full p-4 space-y-3 shadow-2xl relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center pb-2 border-b border-[#1E2A38]">
              <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                <Shield className="w-4 h-4 text-[#00D9FF]" />
                <span>{selectedImageModal.title}</span>
              </h4>
              <button 
                onClick={() => setSelectedImageModal(null)}
                className="p-1 rounded-lg text-[#7D8A99] hover:text-white hover:bg-[#1E2A38] transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="max-h-[75vh] overflow-auto rounded-lg">
              <img 
                src={selectedImageModal.src} 
                alt={selectedImageModal.alt} 
                className="w-full h-auto object-contain rounded-lg"
              />
            </div>
            <div className="text-right pt-1">
              <button 
                onClick={() => setSelectedImageModal(null)}
                className="px-4 py-1.5 bg-[#1E2A38] hover:bg-[#1E2A38]/80 text-xs text-white rounded-lg transition"
              >
                {isAm ? 'ዝጋ' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SIGN IN MODAL */}
      {/* ========================================================================= */}
      {showLoginModal && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm"
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
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-[#00D9FF]" />
            <span className="text-white font-bold">ETHIO-CYBERGUARD</span>
            <span>—</span>
            <span>{isAm ? 'ብሄራዊ የሳይበር ደህንነት እና ጥበቃ ማዕከል' : 'National Cyber Defense Platform'}</span>
          </div>
          <p>{t.publicPage.footerText}</p>
        </div>
      </footer>
    </div>
  );
};
