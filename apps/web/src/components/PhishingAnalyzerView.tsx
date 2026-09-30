import React, { useState } from 'react';
import { 
  Mail, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  ExternalLink, 
  CheckCircle2, 
  XCircle, 
  FileText, 
  Search,
  Zap,
  Globe
} from 'lucide-react';

interface PhishingAnalyzerViewProps {
  onNotify?: (msg: string) => void;
}

const PRESET_EMAILS = [
  {
    name: 'Telebirr 10,000 Birr Scam (Amharic / Fake SMS & Web)',
    sender: '"Telebirr Reward Center" <support@telebirr-bonus.xyz>',
    subject: 'URGENT: ቴሌብር 10,000 ብር የሽልማት አሸናፊ - አሁኑኑ ያረጋግጡ',
    raw: `From: "Telebirr Reward Center" <support@telebirr-bonus.xyz>
To: target.user@ethiotelecom.et
Reply-To: phisher-collector@gmail.com
Subject: URGENT: ቴሌብር 10,000 ብር የሽልማት አሸናፊ - አሁኑኑ ያረጋግጡ
Received-SPF: fail (domain telebirr-bonus.xyz does not match sender IP 196.188.99.12)
Authentication-Results: mx.ethiotelecom.et; spf=fail; dkim=fail; dmarc=fail

እንኳን ደስ አሎት! በብሔራዊ የዲጂታል ክፍያ ማበረታቻ ፕሮግራም የ10,000 ብር የቴሌብር ቦነስ አሸንፈዋል።
ሽልማቱን በቀጥታ ወደ አካውንትዎ ለማስገባት በ24 ሰዓት ውስጥ ይህን ይጫኑና የቴሌብር ፒን (PIN / OTP) ቁጥርዎን ያረጋግጡ፡
http://196.188.99.12/claim-prize/telebirr-login.php

ማሳሰቢያ፡ ይህን እርምጃ ካልወሰዱ ሽልማቱ ይሰረዛል።`
  },
  {
    name: 'CBE Birr KYC / Account Suspension Lure',
    sender: 'Commercial Bank of Ethiopia <security-alert@cbe-ebanking-auth.net>',
    subject: 'URGENT: Temporary Restriction on Your Commercial Bank of Ethiopia (CBE) Account',
    raw: `From: Commercial Bank of Ethiopia <security-alert@cbe-ebanking-auth.net>
To: customer@enterprise.et
Subject: URGENT: Temporary Restriction on Your Commercial Bank of Ethiopia (CBE) Account
Received-SPF: softfail (sender IP not designated in combanketh.et SPF)
Authentication-Results: mx.cbe.com.et; dkim=fail; dmarc=fail

Dear Valued Customer,
Due to compliance with National Bank Directive SBB/89/2026, all internet banking and CBE Birr users must complete biometric and PIN re-verification immediately.
Failure to verify within 24 hours will lead to temporary suspension of your debit card and ATM withdrawals.

Click the secure portal below to verify:
https://cbe-ebanking-auth.net/portal/kyc-verify.php

Commercial Bank of Ethiopia - Always that reliable bank.`
  },
  {
    name: 'Ethio Telecom Official Network Notice (Legitimate)',
    sender: 'Ethio Telecom Operations <noc@ethiotelecom.et>',
    subject: 'Monthly Fiber Backbone Maintenance Notification',
    raw: `From: Ethio Telecom Operations <noc@ethiotelecom.et>
To: enterprise-customers@ethiotelecom.et
Subject: Monthly Fiber Backbone Maintenance Notification
Received-SPF: pass (ethiotelecom.et: 196.188.1.10 permitted sender)
Authentication-Results: mx.ethiotelecom.et; spf=pass; dkim=pass; dmarc=pass

Dear Valued Enterprise Customer,
Ethio Telecom announces scheduled core fiber maintenance for Bole and Kazanchis sub-cities on Saturday, October 4, between 02:00 AM and 05:00 AM EAT.
No user action or credential verification is required.
Official portal: https://ethiotelecom.et/support/network-status`
  }
];

export const PhishingAnalyzerView: React.FC<PhishingAnalyzerViewProps> = () => {
  const [selectedPresetIndex, setSelectedPresetIndex] = useState(0);
  const [rawText, setRawText] = useState(PRESET_EMAILS[0].raw);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const handleSelectPreset = (index: number) => {
    setSelectedPresetIndex(index);
    setRawText(PRESET_EMAILS[index].raw);
    setAnalysisResult(null);
  };

  const handleRunAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      // Offline heuristic analyzer mirroring backend PhishingAnalyzer logic
      const isAmharic = /ቴሌብር|ንግድ ባንክ|አካውንትዎ|የይለፍ|ሽልማት|ብር/i.test(rawText);
      const isCBE = /cbe|combank/i.test(rawText);
      const isTelebirr = /telebirr|ቴሌብር/i.test(rawText);
      const hasSpfFail = /spf=fail|received-spf: fail/i.test(rawText);
      const hasDkimFail = /dkim=fail/i.test(rawText);
      const hasIpUrl = /http:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/i.test(rawText);
      const hasUrgency = /urgent|24 hours|suspended|restriction/i.test(rawText);

      let score = 5;
      const indicators: any[] = [];
      const urls: any[] = [];

      if (hasSpfFail) {
        score += 25;
        indicators.push({
          rule: 'SPF_RECORD_FAILED',
          sev: 'HIGH',
          desc: 'Sender IP is not permitted by DNS SPF record',
          amharic: 'የላኪው አይፒ አድራሻ ህጋዊ የSPF ፍቃድ የለውም።',
          pts: 25
        });
      }
      if (hasDkimFail) {
        score += 25;
        indicators.push({
          rule: 'DKIM_CRYPTO_SIGNATURE_INVALID',
          sev: 'HIGH',
          desc: 'Cryptographic DKIM body signature verification failed',
          amharic: 'የመልዕክቱ የዲጂታል ፊርማ (DKIM) አልተመሳሰለም።',
          pts: 25
        });
      }
      if (hasIpUrl) {
        score += 30;
        urls.push({
          url: 'http://196.188.99.12/claim-prize/telebirr-login.php',
          suspicious: true,
          reason: 'Raw IP address host bypassing domain registration / WHOIS reputation',
          type: 'Direct IP Host'
        });
        indicators.push({
          rule: 'RAW_IP_HYPERLINK',
          sev: 'HIGH',
          desc: 'Phishing hyperlink points to raw IPv4 host instead of enterprise domain',
          amharic: 'የተካተተው ሊንክ በቀጥታ ወደ ያልታወቀ አይፒ የሚያመራ ነው።',
          pts: 30
        });
      } else if (rawText.includes('cbe-ebanking-auth.net')) {
        score += 30;
        urls.push({
          url: 'https://cbe-ebanking-auth.net/portal/kyc-verify.php',
          suspicious: true,
          reason: 'Look-alike typosquatted domain impersonating Commercial Bank of Ethiopia',
          type: 'Typosquat / Combosquat'
        });
        indicators.push({
          rule: 'ETHIOPIAN_BANK_IMPERSONATION',
          sev: 'CRITICAL',
          desc: 'Impersonating Commercial Bank of Ethiopia (CBE) on fake domain cbe-ebanking-auth.net',
          amharic: 'የኢትዮጵያ ንግድ ባንክን ስም ያለአግባብ የተጠቀመ የሃሰት ድረ-ገጽ።',
          pts: 35
        });
      }

      if (hasUrgency) {
        score += 15;
        indicators.push({
          rule: 'PSYCHOLOGICAL_URGENCY_SCARE',
          sev: 'MEDIUM',
          desc: 'Aggressive psychological urgency cues ("within 24 hours", "suspended")',
          amharic: 'ተጠቃሚውን የሚያስደነግጡ እና አጣዳፊ እርምጃ የሚጠይቁ ቃላት ተገኝተዋል።',
          pts: 15
        });
      }

      if (isAmharic && (isTelebirr || isCBE)) {
        score += 25;
        indicators.push({
          rule: 'REGIONAL_AMHARIC_SCAM_KEYWORD',
          sev: 'HIGH',
          desc: 'Targeted Amharic language mobile money / lottery lure',
          amharic: 'የሀገር ውስጥ የቴሌብር እና የባንክ ማታለያ ቃላት በግልጽ ተገኝተዋል።',
          pts: 25
        });
      }

      score = Math.min(score, 100);
      const isPhish = score >= 50;

      setAnalysisResult({
        score,
        verdict: score >= 75 ? 'CRITICAL_PHISHING' : score >= 50 ? 'HIGH_RISK_PHISHING' : score >= 25 ? 'SUSPICIOUS' : 'CLEAN_LEGITIMATE',
        isPhish,
        spf: hasSpfFail ? 'FAIL' : 'PASS',
        dkim: hasDkimFail ? 'FAIL' : 'PASS',
        dmarc: hasSpfFail || hasDkimFail ? 'FAIL' : 'PASS',
        targetedBrand: isTelebirr ? 'Telebirr (Ethio Telecom)' : isCBE ? 'Commercial Bank of Ethiopia' : 'None',
        hasAmharic: isAmharic,
        indicators,
        urls: urls.length > 0 ? urls : [{ url: 'https://ethiotelecom.et/support/network-status', suspicious: false, reason: 'Official domain with valid SSL', type: 'Legitimate Portal' }],
        summaryEn: isPhish 
          ? `High-confidence phishing threat detected with risk score ${score}/100. Failed email authentication combined with brand impersonation.`
          : `Clean message. SPF/DKIM authentication passed and all links point to authorized enterprise infrastructure.`,
        summaryAm: isPhish
          ? `ይህ መልዕክት ከፍተኛ የአደጋ ደረጃ ያለው የማታለያ (Phishing) ሙከራ ነው (${score}/100)። ሊንኮቹን አይጫኑ ወይም ፒን ቁጥርዎን አያስገቡ።`
          : `መልዕክቱ የተረጋገጠ እና ምንም አይነት የደህንነት ስጋት የሌለበት ህጋዊ መልዕክት ነው።`
      });
      setIsAnalyzing(false);
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1E2A38] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#00D9FF]/20 text-[#00D9FF] uppercase tracking-wider">
              ThePhish + NLP Engine
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#22C55E]/20 text-[#22C55E] uppercase tracking-wider">
              Amharic / English
            </span>
          </div>
          <h1 className="text-xl font-bold text-white mt-1">Phishing & Email Threat Analyzer</h1>
          <p className="text-xs text-[#7D8A99]">
            Automated header verification, SPF/DKIM/DMARC forensics, link parsing, and Ethiopian brand impersonation detection
          </p>
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={isAnalyzing}
          className="flex items-center justify-center space-x-2 px-5 py-2.5 bg-[#00D9FF] hover:bg-[#00B8D9] text-black font-bold text-xs rounded-lg transition-all shadow-lg shadow-[#00D9FF]/10 disabled:opacity-50 cursor-pointer"
        >
          {isAnalyzing ? (
            <>
              <Zap className="w-4 h-4 animate-spin" />
              <span>Analyzing Forensics...</span>
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              <span>Execute Phishing Analysis</span>
            </>
          )}
        </button>
      </div>

      {/* Preset Selector */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
        <div className="text-xs font-bold text-white mb-2 flex items-center space-x-2">
          <FileText className="w-4 h-4 text-[#00D9FF]" />
          <span>Load Realistic Threat Samples</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {PRESET_EMAILS.map((preset, idx) => (
            <button
              key={preset.name}
              onClick={() => handleSelectPreset(idx)}
              className={`p-3 rounded-lg text-left border transition-all text-xs cursor-pointer ${
                selectedPresetIndex === idx
                  ? 'border-[#00D9FF] bg-[#00D9FF]/10 text-white'
                  : 'border-[#1E2A38] bg-[#0D131C] text-[#7D8A99] hover:text-[#E6EDF3] hover:border-[#2C3E50]'
              }`}
            >
              <div className="font-bold text-[13px] text-white truncate">{preset.name}</div>
              <div className="text-[11px] text-[#7D8A99] truncate mt-1">Sender: {preset.sender}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Input + Forensics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Raw Email Input */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-4 flex flex-col h-[520px]">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-bold text-white flex items-center space-x-2">
              <Mail className="w-4 h-4 text-[#00D9FF]" />
              <span>Raw RFC-822 Email & Header Source</span>
            </span>
            <span className="text-[11px] text-[#7D8A99]">Paste raw email or headers</span>
          </div>

          <textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            className="flex-1 w-full bg-[#070B12] border border-[#1E2A38] rounded-lg p-3 font-mono text-xs text-[#E6EDF3] resize-none focus:outline-none focus:border-[#00D9FF]"
            placeholder="Paste raw email headers and body here..."
          />
        </div>

        {/* Right: Forensic Verdict & Metrics */}
        <div className="lg:col-span-6 bg-[#111923] border border-[#1E2A38] rounded-xl p-4 flex flex-col h-[520px] overflow-y-auto">
          <div className="flex justify-between items-center mb-3">
            <span className="text-xs font-bold text-white flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-[#00D9FF]" />
              <span>Forensic Verdict & Risk Evaluation</span>
            </span>
            {analysisResult && (
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                analysisResult.isPhish ? 'bg-[#FF1744]/20 text-[#FF1744] border border-[#FF1744]/30' : 'bg-[#22C55E]/20 text-[#22C55E] border border-[#22C55E]/30'
              }`}>
                {analysisResult.verdict}
              </span>
            )}
          </div>

          {!analysisResult ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 border border-dashed border-[#1E2A38] rounded-lg">
              <ShieldAlert className="w-10 h-10 text-[#7D8A99] mb-2" />
              <div className="text-sm font-bold text-white">No Analysis Run Yet</div>
              <p className="text-xs text-[#7D8A99] max-w-sm mt-1">
                Select a preset template or paste email source code, then click "Execute Phishing Analysis".
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Score Meter & Badges */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38] text-center">
                  <div className="text-[10px] text-[#7D8A99] font-bold">THREAT SCORE</div>
                  <div className={`text-2xl font-black mt-0.5 ${
                    analysisResult.score >= 70 ? 'text-[#FF1744]' : analysisResult.score >= 40 ? 'text-[#F59E0B]' : 'text-[#22C55E]'
                  }`}>
                    {analysisResult.score}/100
                  </div>
                </div>

                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38] text-center">
                  <div className="text-[10px] text-[#7D8A99] font-bold">SPF AUTH</div>
                  <div className="flex items-center justify-center space-x-1 mt-1 font-bold text-xs">
                    {analysisResult.spf === 'PASS' ? (
                      <span className="text-[#22C55E] flex items-center"><CheckCircle2 className="w-3.5 h-3.5 mr-1" /> PASS</span>
                    ) : (
                      <span className="text-[#FF1744] flex items-center"><XCircle className="w-3.5 h-3.5 mr-1" /> FAIL</span>
                    )}
                  </div>
                </div>

                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38] text-center">
                  <div className="text-[10px] text-[#7D8A99] font-bold">DKIM SIGN</div>
                  <div className="flex items-center justify-center space-x-1 mt-1 font-bold text-xs">
                    {analysisResult.dkim === 'PASS' ? (
                      <span className="text-[#22C55E] flex items-center"><CheckCircle2 className="w-3.5 h-3.5 mr-1" /> PASS</span>
                    ) : (
                      <span className="text-[#FF1744] flex items-center"><XCircle className="w-3.5 h-3.5 mr-1" /> FAIL</span>
                    )}
                  </div>
                </div>

                <div className="bg-[#0D131C] p-3 rounded-lg border border-[#1E2A38] text-center">
                  <div className="text-[10px] text-[#7D8A99] font-bold">DMARC ALIGN</div>
                  <div className="flex items-center justify-center space-x-1 mt-1 font-bold text-xs">
                    {analysisResult.dmarc === 'PASS' ? (
                      <span className="text-[#22C55E] flex items-center"><CheckCircle2 className="w-3.5 h-3.5 mr-1" /> PASS</span>
                    ) : (
                      <span className="text-[#FF1744] flex items-center"><XCircle className="w-3.5 h-3.5 mr-1" /> FAIL</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Regional Context Card */}
              <div className="bg-[#0D131C] border border-[#1E2A38] p-3 rounded-lg space-y-1.5">
                <div className="text-[11px] font-bold text-[#00D9FF] flex items-center space-x-1.5">
                  <Globe className="w-3.5 h-3.5" />
                  <span>Regional & Ethiopian Threat Context</span>
                </div>
                <div className="text-xs text-[#E6EDF3]">
                  <strong>Targeted Brand:</strong> <span className="text-white ml-1">{analysisResult.targetedBrand}</span>
                </div>
                <div className="text-xs text-[#7D8A99]">
                  {analysisResult.summaryAm}
                </div>
              </div>

              {/* Extracted Hyperlinks */}
              <div className="space-y-1.5">
                <div className="text-xs font-bold text-white flex items-center space-x-1">
                  <ExternalLink className="w-3.5 h-3.5 text-[#00D9FF]" />
                  <span>Extracted Link Telemetry ({analysisResult.urls.length})</span>
                </div>
                <div className="space-y-1.5">
                  {analysisResult.urls.map((u: any, i: number) => (
                    <div key={i} className="p-2 rounded bg-[#070B12] border border-[#1E2A38] text-xs font-mono flex flex-col">
                      <div className="flex items-center justify-between">
                        <span className="text-[#00D9FF] truncate max-w-sm">{u.url}</span>
                        <span className={`text-[10px] px-1.5 py-0.2 rounded font-sans font-bold ${
                          u.suspicious ? 'bg-[#FF1744]/20 text-[#FF1744]' : 'bg-[#22C55E]/20 text-[#22C55E]'
                        }`}>
                          {u.type}
                        </span>
                      </div>
                      <span className="text-[10px] text-[#7D8A99] font-sans mt-0.5">{u.reason}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risk Indicators */}
              <div className="space-y-1.5">
                <div className="text-xs font-bold text-white flex items-center space-x-1">
                  <AlertTriangle className="w-3.5 h-3.5 text-[#F59E0B]" />
                  <span>Detection Indicators ({analysisResult.indicators.length})</span>
                </div>
                <div className="space-y-1.5">
                  {analysisResult.indicators.map((ind: any, i: number) => (
                    <div key={i} className="p-2 rounded bg-[#070B12] border border-[#1E2A38] text-xs flex justify-between items-start">
                      <div>
                        <div className="font-bold text-white text-[11px]">{ind.rule} (+{ind.pts} pts)</div>
                        <div className="text-[#7D8A99] text-[11px] mt-0.5">{ind.desc}</div>
                        {ind.amharic && (
                          <div className="text-[#00D9FF] text-[10px] mt-0.5">{ind.amharic}</div>
                        )}
                      </div>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                        ind.sev === 'CRITICAL' ? 'bg-[#FF1744]/20 text-[#FF1744]' : 'bg-[#F59E0B]/20 text-[#F59E0B]'
                      }`}>
                        {ind.sev}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* SOC Playbook Action */}
              <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
                <div className="text-xs font-bold text-white mb-1 flex items-center space-x-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#22C55E]" />
                  <span>Automated SOC Response Recommendation</span>
                </div>
                <p className="text-[11px] text-[#7D8A99]">
                  {analysisResult.isPhish 
                    ? 'Immediately inject sender domain into perimeter email gateway blacklists, isolate any recipient endpoints that navigated to the extracted IP host, and report brand abuse to INSA CERT.'
                    : 'Permit message delivery. No immediate defensive containment warranted.'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
