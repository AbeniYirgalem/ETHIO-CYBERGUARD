import React, { useState } from 'react';
import { 
  GraduationCap, 
  Send, 
  Users, 
  Eye, 
  Languages, 
  Award,
  Zap
} from 'lucide-react';

interface AwarenessSimulatorViewProps {
  onNotify?: (msg: string) => void;
}

const CAMPAIGN_TEMPLATES = [
  {
    id: 'camp-telebirr-prize',
    titleEn: 'Telebirr 10,000 Birr Anniversary Prize Fraud',
    titleAm: 'የ10,000 ብር የቴሌብር አመታዊ ሽልማት ማታለያ',
    targetVector: 'SMS / Mobile Money',
    difficulty: 'Moderate',
    spoofedSender: 'telebirr-award@telecom-promo.xyz',
    subjectEn: 'Congratulations! You have been selected for 10,000 Birr Telebirr Bonus',
    subjectAm: 'እንኳን ደስ አሎት! የ10,000 ብር የቴሌብር ቦነስ አሸንፈዋል',
    bodyEn: `Dear Valued Customer, Congratulations! Your active phone number has won 10,000 ETB in the National Digital Economy promotion. To claim your reward directly into your Telebirr wallet, click: http://telebirr-claim.xyz/verify?id=92849 within 24 hours. Enter your registered PIN to verify.`,
    bodyAm: `ክቡር ደንበኛችን እንኳን ደስ አሎት! በብሔራዊ የዲጂታል ኢኮኖሚ ማበረታቻ ፕሮግራም የ10,000 ብር ተሸላሚ ሆነዋል። ሽልማቱን በቀጥታ ወደ ቴሌብር አካውንትዎ ለማስገባት በ24 ሰዓት ውስጥ http://telebirr-claim.xyz/verify?id=92849 ይጫኑና የቴሌብር ፒን ቁጥርዎን በማስገባት ያረጋግጡ።`,
    clues: [
      'Official Telebirr domain is telebirr.et, NEVER telebirr-claim.xyz.',
      'Ethio Telecom / Telebirr staff will NEVER ask for your secret PIN or OTP.',
      'Extreme urgency ("within 24 hours") is a standard psychological trap.'
    ],
    category: 'Financial / Mobile Money Fraud'
  },
  {
    id: 'camp-cbe-kyc',
    titleEn: 'Commercial Bank of Ethiopia (CBE) Birr Security Re-verification',
    titleAm: 'የኢትዮጵያ ንግድ ባንክ አስቸኳይ የደህንነት ማረጋገጫ',
    targetVector: 'Email / Web Portal',
    difficulty: 'Advanced',
    spoofedSender: 'security-alert@combanketh-portal.com',
    subjectEn: 'URGENT: Temporary Restriction on CBE Birr / Internet Banking Account',
    subjectAm: 'አስቸኳይ፡ በኢትዮጵያ ንግድ ባንክ መለያዎ ላይ የተጣለ ጊዜያዊ እገዳ',
    bodyEn: `Dear CBE Customer, Under National Bank Directive No. SBB/89/2026, all internet banking and CBE Birr users must complete biometric re-verification by 5:00 PM today. Failure to comply will result in suspension of debit cards and fund transfers. Complete KYC now: https://cbe-ebanking-auth.net/portal/kyc`,
    bodyAm: `ክቡር የኢትዮጵያ ንግድ ባንክ ደንበኛ፡ በብሔራዊ ባንክ መመሪያ ቁጥር SBB/89/2026 መሰረት ሁሉም የኦንላይን ባንኪንግ እና CBE Birr ተጠቃሚዎች ዛሬ ከቀኑ 11:00 ሰዓት በፊት የማንነት ማረጋገጫ (KYC) ማጠናቀቅ አለባቸው። ይህን ካላደረጉ ካርድዎ እና የገንዘብ ዝውውርዎ ይታገዳል። አሁኑኑ ያረጋግጡ፡ https://cbe-ebanking-auth.net/portal/kyc`,
    clues: [
      'Sender domain combanketh-portal.com is NOT the authentic combanketh.et bank domain.',
      'Commercial Bank never communicates urgent account freezes with unverified links.',
      'Always inspect the URL address bar before entering credentials.'
    ],
    category: 'Banking Credential Harvesting'
  },
  {
    id: 'camp-aau-sso',
    titleEn: 'Addis Ababa University (AAU) Academic Portal Password Reset',
    titleAm: 'የአዲስ አበባ ዩኒቨርሲቲ የፖርታል የይለፍ ቃል ማደሻ',
    targetVector: 'Email',
    difficulty: 'Easy',
    spoofedSender: 'helpdesk@aau-auth.org',
    subjectEn: 'Action Required: Your AAU Academic Staff & Student Password Has Expired',
    subjectAm: 'አስቸኳይ፡ የአዲስ አበባ ዩኒቨርሲቲ የይለፍ ቃልዎ ጊዜው አልቋል',
    bodyEn: `University IT Service Notice: Your campus portal account password expires today. To maintain uninterrupted access to the digital library, registrar grade records, and campus WiFi, synchronize your password here: https://portal-aau.org/login`,
    bodyAm: `የዩኒቨርሲቲው አይቲ ማስታወቂያ፡ የካምፓስ ፖርታል አካውንትዎ የይለፍ ቃል ዛሬ ያበቃል። የዲጂታል ላይብረሪ፣ የሬጅስትራር ውጤቶች እና የካምፓስ ዋይፋይ እንዳይቋረጥብዎ የይለፍ ቃልዎን እዚህ ያድሱ፡ https://portal-aau.org/login`,
    clues: [
      'Official AAU domain is aau.edu.et, not portal-aau.org.',
      'Notice generic greeting instead of addressing you by official student/staff ID.'
    ],
    category: 'Higher Education Phishing'
  },
  {
    id: 'camp-payroll-bonus',
    titleEn: 'HR Ethiopian New Year (Enkutatash) Performance Bonus',
    titleAm: 'የአዲሱ ዓመት (እንቁጣጣሽ) የስራ አፈጻጸም ቦነስ ማስታወቂያ',
    targetVector: 'Email & Attachment',
    difficulty: 'Moderate',
    spoofedSender: 'payroll@company-hr-portal.com',
    subjectEn: 'Confidential: 2026 Enkutatash Bonus & Salary Adjustment Schedule',
    subjectAm: 'ሚስጥራዊ፡ የ2019 የእንቁጣጣሽ ቦነስ እና የደመወዝ ጭማሪ ሰነድ',
    bodyEn: `Good day team, Management has approved special holiday performance bonuses for eligible staff. Review your individual bonus calculation and direct deposit bank account details in the attached spreadsheet: Download: http://196.188.42.10/payroll/bonus_breakdown.xlsx.exe`,
    bodyAm: `ውድ የስራ ባልደረቦች፡ የድርጅቱ ማኔጅመንት የአዲሱን ዓመት አስመልክቶ ልዩ የቦነስ አበል ፈቅዷል። የተመደበልዎትን ቦነስ እና የሚገባበትን የባንክ ሂሳብ ዝርዝር ለማየት የተያያዘውን ሰነድ ያውርዱ፡ http://196.188.42.10/payroll/bonus_breakdown.xlsx.exe`,
    clues: [
      'The file has a double extension (.xlsx.exe) which installs malicious trojans.',
      'Direct IP address host indicates an external attacker server.',
      'Greed and curiosity lure leveraging traditional holiday bonuses.'
    ],
    category: 'Executive Impersonation'
  }
];

export const AwarenessSimulatorView: React.FC<AwarenessSimulatorViewProps> = () => {
  const [selectedCampaign, setSelectedCampaign] = useState(CAMPAIGN_TEMPLATES[0]);
  const [targetDept, setTargetDept] = useState('All');
  const [languageMode, setLanguageMode] = useState<'EN' | 'AM'>('AM');
  const [isDispatching, setIsDispatching] = useState(false);
  const [dispatchAlert, setDispatchAlert] = useState<string | null>(null);

  const departments = [
    { name: 'Finance & Accounting', employees: 180, clickRate: 18.2, compRate: 6.1, reportRate: 58.0, risk: 'MODERATE' },
    { name: 'IT & Infrastructure', employees: 120, clickRate: 4.1, compRate: 0.8, reportRate: 84.5, risk: 'LOW' },
    { name: 'Human Resources', employees: 95, clickRate: 19.5, compRate: 8.4, reportRate: 46.2, risk: 'HIGH' },
    { name: 'Customer Operations & Branch', employees: 725, clickRate: 22.0, compRate: 11.2, reportRate: 39.8, risk: 'CRITICAL' },
    { name: 'Executive Leadership', employees: 30, clickRate: 13.3, compRate: 3.3, reportRate: 60.0, risk: 'MODERATE' }
  ];

  const handleLaunchCampaign = () => {
    setIsDispatching(true);
    setTimeout(() => {
      setIsDispatching(false);
      setDispatchAlert(`Simulation "${selectedCampaign.titleEn}" successfully dispatched to ${targetDept} (${targetDept === 'All' ? '1,150 employees' : 'Selected division'}). Tracking clicks and reporting in real-time.`);
      setTimeout(() => setDispatchAlert(null), 5000);
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1E2A38] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#00D9FF]/20 text-[#00D9FF] uppercase tracking-wider">
              CyberSatark Simulation Engine
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#22C55E]/20 text-[#22C55E] uppercase tracking-wider">
              Human Defense Layer
            </span>
          </div>
          <h1 className="text-xl font-bold text-white mt-1">Security Awareness & Phishing Simulation</h1>
          <p className="text-xs text-[#7D8A99]">
            Realistic regional phishing simulations in Amharic & English to test, train, and measure employee cyber hygiene
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={targetDept}
            onChange={(e) => setTargetDept(e.target.value)}
            className="bg-[#111923] border border-[#1E2A38] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-[#00D9FF]"
          >
            <option value="All">All Departments (1,150 staff)</option>
            <option value="Finance & Accounting">Finance & Accounting</option>
            <option value="Human Resources">Human Resources</option>
            <option value="Customer Operations & Branch">Customer Operations & Branch</option>
            <option value="Executive Leadership">Executive Leadership</option>
          </select>

          <button
            onClick={handleLaunchCampaign}
            disabled={isDispatching}
            className="flex items-center space-x-1.5 px-4 py-2 bg-[#00D9FF] hover:bg-[#00B8D9] text-black font-bold text-xs rounded-lg transition-all cursor-pointer disabled:opacity-50"
          >
            <Send className={`w-3.5 h-3.5 ${isDispatching ? 'animate-pulse' : ''}`} />
            <span>Launch Simulation</span>
          </button>
        </div>
      </div>

      {dispatchAlert && (
        <div className="p-3 bg-[#22C55E]/10 border border-[#22C55E]/30 rounded-lg text-xs text-[#22C55E] flex items-center justify-between">
          <span>{dispatchAlert}</span>
          <button onClick={() => setDispatchAlert(null)} className="text-[#22C55E] hover:underline">Dismiss</button>
        </div>
      )}

      {/* Top Cards: Benchmarking */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">OVERALL PHISH-PRONE %</div>
          <div className="text-2xl font-black text-[#F59E0B] mt-1 font-mono">14.8%</div>
          <div className="text-[10px] text-[#22C55E] mt-1">↓ 13.4% better than 28.2% national average</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">REPORTING RATE</div>
          <div className="text-2xl font-black text-[#22C55E] mt-1 font-mono">52.4%</div>
          <div className="text-[10px] text-[#00D9FF] mt-1">Staff reported within 15 minutes</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">ACTIVE SIMULATIONS</div>
          <div className="text-2xl font-black text-white mt-1 font-mono">4 Campaigns</div>
          <div className="text-[10px] text-[#7D8A99] mt-1">Localized Amharic & English</div>
        </div>

        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
          <div className="text-[11px] text-[#7D8A99] font-bold">TRAINING COMPLETION</div>
          <div className="text-2xl font-black text-[#00D9FF] mt-1 font-mono">89.2%</div>
          <div className="text-[10px] text-[#00D9FF] mt-1">Mandatory micro-learning completed</div>
        </div>
      </div>

      {/* Campaign Template Picker */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
        <div className="text-xs font-bold text-white mb-2 flex items-center space-x-2">
          <GraduationCap className="w-4 h-4 text-[#00D9FF]" />
          <span>Select Phishing Simulation Template</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {CAMPAIGN_TEMPLATES.map((camp) => (
            <button
              key={camp.id}
              onClick={() => setSelectedCampaign(camp)}
              className={`p-3 rounded-lg text-left border transition-all text-xs cursor-pointer flex flex-col justify-between ${
                selectedCampaign.id === camp.id
                  ? 'border-[#00D9FF] bg-[#00D9FF]/10 text-white'
                  : 'border-[#1E2A38] bg-[#0D131C] text-[#7D8A99] hover:text-[#E6EDF3] hover:border-[#2C3E50]'
              }`}
            >
              <div>
                <span className="px-1.5 py-0.5 rounded bg-[#1E2A38] text-[9px] font-bold text-[#00D9FF]">
                  {camp.targetVector}
                </span>
                <div className="font-bold text-white text-[12px] mt-1.5 leading-snug">{camp.titleEn}</div>
                <div className="text-[11px] text-[#00D9FF] mt-1 font-sans">{camp.titleAm}</div>
              </div>
              <div className="text-[10px] text-[#7D8A99] mt-2 pt-2 border-t border-[#1E2A38] flex justify-between">
                <span>Diff: {camp.difficulty}</span>
                <span>{camp.category}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Campaign Details Preview + Department Risk Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Email / SMS Preview */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-bold text-white flex items-center space-x-2">
              <Eye className="w-4 h-4 text-[#00D9FF]" />
              <span>Simulation Message Preview</span>
            </span>

            {/* Language Toggle */}
            <div className="flex items-center space-x-1 bg-[#070B12] p-1 rounded-lg border border-[#1E2A38]">
              <Languages className="w-3 h-3 text-[#7D8A99] ml-1 mr-1" />
              <button
                onClick={() => setLanguageMode('AM')}
                className={`px-2 py-0.5 text-[10px] rounded font-bold cursor-pointer ${
                  languageMode === 'AM' ? 'bg-[#00D9FF] text-black' : 'text-[#7D8A99]'
                }`}
              >
                አማርኛ (Amharic)
              </button>
              <button
                onClick={() => setLanguageMode('EN')}
                className={`px-2 py-0.5 text-[10px] rounded font-bold cursor-pointer ${
                  languageMode === 'EN' ? 'bg-[#00D9FF] text-black' : 'text-[#7D8A99]'
                }`}
              >
                English
              </button>
            </div>
          </div>

          {/* Email Canvas */}
          <div className="bg-[#070B12] border border-[#1E2A38] rounded-lg p-4 space-y-3 font-mono text-xs">
            <div className="text-[#7D8A99] text-[11px] space-y-1 pb-2 border-b border-[#1E2A38] font-sans">
              <div><strong className="text-white font-mono">From:</strong> {selectedCampaign.spoofedSender}</div>
              <div><strong className="text-white font-mono">Subject:</strong> {languageMode === 'AM' ? selectedCampaign.subjectAm : selectedCampaign.subjectEn}</div>
            </div>

            <div className="text-[#E6EDF3] leading-relaxed font-sans text-xs whitespace-pre-wrap py-2">
              {languageMode === 'AM' ? selectedCampaign.bodyAm : selectedCampaign.bodyEn}
            </div>
          </div>

          {/* Educational Clues */}
          <div className="bg-[#0D131C] border border-[#1E2A38] rounded-lg p-3 space-y-2">
            <div className="text-xs font-bold text-[#F59E0B] flex items-center space-x-1.5">
              <Zap className="w-3.5 h-3.5" />
              <span>Red Flags & Micro-Learning Clues (What Employees Learn)</span>
            </div>
            <ul className="space-y-1.5 text-xs text-[#E6EDF3]">
              {selectedCampaign.clues.map((clue, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-[#00D9FF] font-bold">•</span>
                  <span>{clue}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right: Department Susceptibility Dashboard */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-bold text-white flex items-center space-x-2">
              <Users className="w-4 h-4 text-[#00D9FF]" />
              <span>Department Vulnerability & Phish-Prone Scores</span>
            </span>
            <span className="text-[10px] text-[#7D8A99]">Monthly Assessment</span>
          </div>

          <div className="space-y-3">
            {departments.map((d) => (
              <div key={d.name} className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg text-xs space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="font-bold text-white text-[13px]">{d.name}</span>
                    <span className="text-[#7D8A99] text-[11px] ml-2 font-mono">({d.employees} staff)</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    d.risk === 'CRITICAL' ? 'bg-[#FF1744]/20 text-[#FF1744]' :
                    d.risk === 'HIGH' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' :
                    d.risk === 'MODERATE' ? 'bg-[#00D9FF]/20 text-[#00D9FF]' : 'bg-[#22C55E]/20 text-[#22C55E]'
                  }`}>
                    {d.risk}
                  </span>
                </div>

                {/* Progress bars */}
                <div className="grid grid-cols-3 gap-3 text-[11px]">
                  <div>
                    <span className="text-[#7D8A99] block text-[10px]">Clicked Link</span>
                    <div className="w-full bg-[#1E2A38] h-1.5 rounded-full overflow-hidden mt-1">
                      <div className="bg-[#FF1744] h-full" style={{ width: `${d.clickRate}%` }} />
                    </div>
                    <span className="text-white font-mono font-bold mt-0.5 block">{d.clickRate}%</span>
                  </div>

                  <div>
                    <span className="text-[#7D8A99] block text-[10px]">Entered Credentials</span>
                    <div className="w-full bg-[#1E2A38] h-1.5 rounded-full overflow-hidden mt-1">
                      <div className="bg-[#F59E0B] h-full" style={{ width: `${d.compRate}%` }} />
                    </div>
                    <span className="text-white font-mono font-bold mt-0.5 block">{d.compRate}%</span>
                  </div>

                  <div>
                    <span className="text-[#7D8A99] block text-[10px]">Reported Phish</span>
                    <div className="w-full bg-[#1E2A38] h-1.5 rounded-full overflow-hidden mt-1">
                      <div className="bg-[#22C55E] h-full" style={{ width: `${d.reportRate}%` }} />
                    </div>
                    <span className="text-white font-mono font-bold mt-0.5 block">{d.reportRate}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Gamification Badge */}
          <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-[#22C55E]" />
              <div>
                <div className="text-xs font-bold text-white">Top Security Champion Division</div>
                <div className="text-[11px] text-[#7D8A99]">IT & Infrastructure (84.5% instant report rate)</div>
              </div>
            </div>
            <span className="px-2 py-1 rounded bg-[#22C55E]/10 text-[#22C55E] text-[10px] font-bold">
              Gold Tier
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
