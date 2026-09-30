"""
ETHIO-CYBERGUARD - Automated Phishing Email & Header Analysis Engine
Analyzes raw email content or individual headers and body text.
Detects SPF/DKIM/DMARC anomalies, malicious URLs, credential harvesting cues,
and regional scam keywords in English and Amharic (Telebirr, CBE, INSA, etc.).
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import re
import email
from email import policy
from urllib.parse import urlparse


@dataclass
class Indicator:
    rule: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    score_impact: int
    amharic_description: Optional[str] = None


@dataclass
class PhishingAnalysisResult:
    is_phishing: bool
    risk_score: int  # 0-100
    verdict: str  # CLEAN, SUSPICIOUS, HIGH_RISK, CRITICAL_PHISHING
    sender: str
    sender_domain: str
    reply_to: Optional[str]
    subject: str
    auth_results: Dict[str, str]  # spf, dkim, dmarc
    indicators: List[Dict[str, Any]]
    extracted_urls: List[Dict[str, Any]]
    regional_context: Dict[str, Any]
    summary_en: str
    summary_am: str
    recommended_actions: List[str]


class PhishingAnalyzer:
    """
    Automated Phishing Analyzer tailored for corporate and Ethiopian national infrastructure.
    Detects financial impersonation (CBE, Telebirr, Awash, Dashen, Zemen, BOA),
    government spoofing (INSA, Gov.et, Revenue Ministry), and common cyber fraud patterns.
    """

    ETHIOPIAN_TARGET_BRANDS = {
        "telebirr": {"name": "Telebirr / Ethio Telecom", "official_domains": ["telebirr.et", "ethiotelecom.et"]},
        "cbe": {"name": "Commercial Bank of Ethiopia", "official_domains": ["combanketh.et", "cbe.com.et"]},
        "ethiotelecom": {"name": "Ethio Telecom", "official_domains": ["ethiotelecom.et", "telecom.net.et"]},
        "insa": {"name": "Information Network Security Administration", "official_domains": ["insa.gov.et"]},
        "chapa": {"name": "Chapa Financial Technologies", "official_domains": ["chapa.co"]},
        "awash": {"name": "Awash Bank", "official_domains": ["awashbank.com"]},
        "dashen": {"name": "Dashen Bank", "official_domains": ["dashenbanksc.com"]},
        "abyssinia": {"name": "Bank of Abyssinia", "official_domains": ["bankofabyssinia.com"]},
        "zemen": {"name": "Zemen Bank", "official_domains": ["zemenbank.com"]},
        "ministry": {"name": "Ethiopian Government Ministries", "official_domains": ["gov.et", "mof.gov.et", "mor.gov.et"]}
    }

    AMHARIC_SCAM_PATTERNS = [
        (r"ቴሌብር|ቴሌ\s*ብር|telebirr", "Telebirr keyword in message", "የቴሌብር ስም የተጠቀሰበት መልዕክት", 15),
        (r"የኢትዮጵያ ንግድ ባንክ|ንግድ ባንክ|cbe|combank", "CBE Bank impersonation", "የኢትዮጵያ ንግድ ባንክ የማስመሰል ሙከራ", 20),
        (r"አካውንትዎ\s*(?:ታግዷል|ተዘግቷል|ይዘጋል)|መለያዎ ታግዷል", "Account suspension threat in Amharic", "አካውንትዎ እንደታገደ የሚገልጽ አስፈሪ መልዕክት", 35),
        (r"የይለፍ\s*ቃል|የምስጢር\s*ቁጥር|ፒን|pin|otp|ኦቲፒ", "Credential/PIN harvesting attempt", "የምስጢር ቁጥር ወይም ፒን የመጠየቅ ሙከራ", 40),
        (r"የሽልማት\s*አሸናፊ|ብር\s*ተሸልመዋል|ሽልማትዎን\s*ይውሰዱ|lottery", "Fake lottery / prize scheme", "የሀሰት የሽልማት እና የገንዘብ ማታለያ", 30),
        (r"አስቸኳይ|በ24\s*ሰዓት|ወዲያውኑ|አሁኑኑ", "Urgency tactic in Amharic", "አስቸኳይ እርምጃ እንዲወስዱ የሚገፋፋ ቋንቋ", 20),
        (r"ማረጋገጫ|ያረጋግጡ|ለማረጋገጥ\s*ይጫኑ", "Verification lure in Amharic", "ማረጋገጫ ለማድረግ የሚያታልል ጥሪ", 15),
    ]

    ENGLISH_URGENCY_KEYWORDS = [
        "urgent action required", "account suspended", "immediate verification",
        "unauthorized transaction", "24 hours to respond", "security alert",
        "password expired", "payroll update", "invoice attached", "funds on hold",
        "tax refund notice", "confirm your identity", "suspended immediately"
    ]

    SUSPICIOUS_TLDS = {".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq", ".work", ".click", ".link", ".buzz", ".guru"}

    def analyze(self, raw_content: str, subject: Optional[str] = None, sender: Optional[str] = None) -> PhishingAnalysisResult:
        """
        Analyze a raw email string or RFC-822 email message.
        """
        parsed_email = None
        body = ""
        headers: Dict[str, str] = {}

        if "Received:" in raw_content or "From:" in raw_content or "MIME-Version:" in raw_content:
            try:
                parsed_email = email.message_from_string(raw_content, policy=policy.default)
                headers = {k.lower(): str(v) for k, v in parsed_email.items()}
                subject = subject or str(parsed_email.get("subject", ""))
                sender = sender or str(parsed_email.get("from", ""))
                
                # Extract body
                if parsed_email.is_multipart():
                    for part in parsed_email.walk():
                        content_type = part.get_content_type()
                        if content_type in ["text/plain", "text/html"]:
                            try:
                                body += part.get_payload(decode=True).decode(errors="ignore") + "\n"
                            except Exception:
                                pass
                else:
                    body = parsed_email.get_payload(decode=True).decode(errors="ignore")
            except Exception:
                body = raw_content
        else:
            body = raw_content

        subject = subject or ""
        sender = sender or ""

        # Extract sender domain
        sender_match = re.search(r"[\w\.-]+@([\w\.-]+)", sender)
        sender_domain = sender_match.group(1).lower() if sender_match else ""

        # Reply-To header check
        reply_to = headers.get("reply-to", "")
        reply_to_match = re.search(r"[\w\.-]+@([\w\.-]+)", reply_to)
        reply_to_domain = reply_to_match.group(1).lower() if reply_to_match else None

        indicators: List[Indicator] = []
        score = 0

        # 1. SPF / DKIM / DMARC checks
        auth_results = self._analyze_auth_headers(headers, raw_content)
        
        if auth_results["spf"] == "fail":
            indicators.append(Indicator("SPF_FAIL", "HIGH", "SPF record check failed: sender IP is unauthorized.", 25, "የላኪው የአይፒ አድራሻ ህጋዊ የSPF ፍቃድ የለውም።"))
            score += 25
        elif auth_results["spf"] == "softfail":
            indicators.append(Indicator("SPF_SOFTFAIL", "MEDIUM", "SPF softfail: sender not explicitly authorized.", 15, "ላኪው ሙሉ በሙሉ የተረጋገጠ አይደለም (Softfail)።"))
            score += 15

        if auth_results["dkim"] == "fail":
            indicators.append(Indicator("DKIM_FAIL", "HIGH", "Cryptographic DKIM signature verification failed.", 25, "የመልዕክቱ የዲጂታል ፊርማ (DKIM) አልተመሳሰለም ወይም ተቀይሯል።"))
            score += 25

        if auth_results["dmarc"] == "fail":
            indicators.append(Indicator("DMARC_FAIL", "CRITICAL", "DMARC policy failed: sender identity alignment rejected.", 30, "የDMARC ፖሊሲ አልተሳካም፤ ላኪው ሌላ ድርጅት አስመስሎ እየላከ ነው።"))
            score += 30

        # 2. Reply-To Mismatch
        if reply_to_domain and sender_domain and reply_to_domain != sender_domain:
            indicators.append(Indicator("REPLY_TO_MISMATCH", "HIGH", f"Reply-To domain '{reply_to_domain}' mismatches sender '{sender_domain}'.", 25, f"መልስ የሚላክበት አድራሻ ({reply_to_domain}) ከላኪው የተለየ ነው።"))
            score += 25

        # 3. URL Extraction and analysis
        extracted_urls = self._extract_and_analyze_urls(body, raw_content)
        for u in extracted_urls:
            if u.get("is_suspicious"):
                score += u.get("risk_weight", 15)
                indicators.append(Indicator(
                    rule=f"SUSPICIOUS_URL_{u['category'].upper()}",
                    severity="HIGH" if u.get("risk_weight", 15) >= 20 else "MEDIUM",
                    description=f"Suspicious link detected: {u['url']} ({u['reason']})",
                    score_impact=u.get("risk_weight", 15),
                    amharic_description=f"አጠራጣሪ አገናኝ/ሊንክ ተገኝቷል፡ {u['url']}"
                ))

        # 4. English Urgency & Scare Tactics
        text_to_scan = f"{subject} {body}".lower()
        urgency_matches = [phrase for phrase in self.ENGLISH_URGENCY_KEYWORDS if phrase in text_to_scan]
        if urgency_matches:
            weight = min(len(urgency_matches) * 10, 30)
            score += weight
            indicators.append(Indicator(
                rule="URGENCY_SCARE_TACTICS",
                severity="MEDIUM",
                description=f"Psychological urgency cues detected: {', '.join(urgency_matches[:3])}",
                score_impact=weight,
                amharic_description=f"ሰውን የሚያስደነግጡ እና አጣዳፊ እርምጃ የሚጠይቁ ቃላት ተገኝተዋል፡ {', '.join(urgency_matches[:3])}"
            ))

        # 5. Amharic Regional Scam Analysis
        amharic_matches = []
        for pattern, desc, am_desc, pts in self.AMHARIC_SCAM_PATTERNS:
            if re.search(pattern, f"{subject} {body}", re.IGNORECASE):
                amharic_matches.append((desc, am_desc, pts))
                score += pts
                indicators.append(Indicator(
                    rule="AMHARIC_SCAM_TRIGGER",
                    severity="HIGH" if pts >= 30 else "MEDIUM",
                    description=f"Regional Amharic threat indicator: {desc}",
                    score_impact=pts,
                    amharic_description=am_desc
                ))

        # 6. Ethiopian Brand Impersonation Check
        brand_impersonation = self._check_brand_impersonation(f"{subject} {body}", sender_domain, extracted_urls)
        if brand_impersonation:
            score += 35
            indicators.append(Indicator(
                rule="REGIONAL_BRAND_IMPERSONATION",
                severity="CRITICAL",
                description=f"Impersonating {brand_impersonation['brand']} without official authorization ({sender_domain or 'unknown sender'}).",
                score_impact=35,
                amharic_description=f"{brand_impersonation['brand']}ን የማስመሰል ከፍተኛ አደጋ ያለው የማታለያ ሙከራ።"
            ))

        # Cap score at 100
        final_score = min(max(score, 0), 100)

        # Verdict
        if final_score >= 70:
            verdict = "CRITICAL_PHISHING"
            is_phishing = True
        elif final_score >= 40:
            verdict = "HIGH_RISK"
            is_phishing = True
        elif final_score >= 20:
            verdict = "SUSPICIOUS"
            is_phishing = False
        else:
            verdict = "CLEAN"
            is_phishing = False

        # Recommended Actions
        actions = []
        if is_phishing:
            actions.append("Do NOT click any links, open attachments, or reply to this message.")
            actions.append("Block sender address and domain across Microsoft 365 / Google Workspace / Postfix MTA.")
            actions.append("Add extracted malicious domains to enterprise DNS blackholes and perimeter firewalls.")
            if brand_impersonation:
                actions.append(f"Notify {brand_impersonation['brand']} security team and INSA CERT regarding active brand abuse.")
        elif verdict == "SUSPICIOUS":
            actions.append("Exercise caution. Verify sender via secondary out-of-band communication channel (e.g. phone call).")
            actions.append("Inspect any hyperlinks manually before entering credentials.")
        else:
            actions.append("No immediate threat detected. Standard email hygiene applies.")

        # Summaries
        summary_en = (
            f"Analysis completed with a threat score of {final_score}/100 ({verdict}). "
            f"Found {len(indicators)} risk indicator(s) and {len(extracted_urls)} extracted URL(s). "
            + (f"Detected unauthorized brand spoofing of {brand_impersonation['brand']}." if brand_impersonation else "No overt brand spoofing confirmed.")
        )

        summary_am = (
            f"የደህንነት ምርመራው የተጠናቀቀ ሲሆን የአደጋ ደረጃው {final_score}/100 ({verdict}) ነው። "
            f"{len(indicators)} አጠራጣሪ ምልክቶች እና {len(extracted_urls)} ሊንኮች ተገኝተዋል። "
            + (f"የ{brand_impersonation['brand']}ን ስም ያለአግባብ የመጠቀም ሙከራ ታይቷል።" if brand_impersonation else "የተረጋገጠ የማስመሰል ምልክት አልተገኘም።")
        )

        return PhishingAnalysisResult(
            is_phishing=is_phishing,
            risk_score=final_score,
            verdict=verdict,
            sender=sender,
            sender_domain=sender_domain,
            reply_to=reply_to,
            subject=subject,
            auth_results=auth_results,
            indicators=[{
                "rule": ind.rule,
                "severity": ind.severity,
                "description": ind.description,
                "score_impact": ind.score_impact,
                "amharic_description": ind.amharic_description
            } for ind in indicators],
            extracted_urls=extracted_urls,
            regional_context={
                "targeted_brand": brand_impersonation["brand"] if brand_impersonation else None,
                "amharic_detected": len(amharic_matches) > 0,
                "amharic_indicators_count": len(amharic_matches),
            },
            summary_en=summary_en,
            summary_am=summary_am,
            recommended_actions=actions
        )

    def _analyze_auth_headers(self, headers: Dict[str, str], raw: str) -> Dict[str, str]:
        auth = {"spf": "unknown", "dkim": "unknown", "dmarc": "unknown"}
        
        # Check received-spf
        received_spf = headers.get("received-spf", "")
        if "pass" in received_spf.lower():
            auth["spf"] = "pass"
        elif "fail" in received_spf.lower() and "softfail" not in received_spf.lower():
            auth["spf"] = "fail"
        elif "softfail" in received_spf.lower():
            auth["spf"] = "softfail"
        elif "neutral" in received_spf.lower() or "none" in received_spf.lower():
            auth["spf"] = "neutral"

        # Check authentication-results
        auth_results = headers.get("authentication-results", "")
        if "spf=pass" in auth_results:
            auth["spf"] = "pass"
        elif "spf=fail" in auth_results:
            auth["spf"] = "fail"
        elif "spf=softfail" in auth_results:
            auth["spf"] = "softfail"

        if "dkim=pass" in auth_results:
            auth["dkim"] = "pass"
        elif "dkim=fail" in auth_results:
            auth["dkim"] = "fail"
        elif "dkim-signature" in headers:
            auth["dkim"] = "present_unverified"

        if "dmarc=pass" in auth_results:
            auth["dmarc"] = "pass"
        elif "dmarc=fail" in auth_results:
            auth["dmarc"] = "fail"

        return auth

    def _extract_and_analyze_urls(self, body: str, raw: str) -> List[Dict[str, Any]]:
        url_regex = r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]+(?::\d+)?(?:/[^\s\"'<>]*)?"
        matches = list(set(re.findall(url_regex, f"{body} {raw}")))
        results = []

        for u in matches:
            parsed = urlparse(u)
            hostname = parsed.hostname or ""
            is_ip = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname))
            is_suspicious_tld = any(hostname.endswith(tld) for tld in self.SUSPICIOUS_TLDS)
            
            # Check if domain mimics Ethiopian brands
            brand_in_domain = False
            for b in self.ETHIOPIAN_TARGET_BRANDS.keys():
                if b in hostname.lower():
                    # check if official
                    official = any(hostname.lower().endswith(off) for off in self.ETHIOPIAN_TARGET_BRANDS[b]["official_domains"])
                    if not official:
                        brand_in_domain = True
                        break

            is_suspicious = False
            reason = "Benign link structure"
            risk_weight = 0
            category = "legitimate"

            if is_ip:
                is_suspicious = True
                reason = "Direct IP address used instead of legitimate registered domain"
                risk_weight = 30
                category = "ip_host"
            elif brand_in_domain:
                is_suspicious = True
                reason = "Unofficial domain containing Ethiopian bank or telecom brand name"
                risk_weight = 35
                category = "typosquat_spoof"
            elif is_suspicious_tld:
                is_suspicious = True
                reason = f"High-risk free or disposable TLD ({parsed.hostname})"
                risk_weight = 20
                category = "risky_tld"
            elif any(kw in parsed.path.lower() for kw in ["/login", "/verify", "/reset", "/otp", "/secure-update", "/claim"]):
                is_suspicious = True
                reason = "Potential credential harvesting or authentication lure path"
                risk_weight = 15
                category = "credential_lure"

            results.append({
                "url": u,
                "domain": hostname,
                "path": parsed.path,
                "is_ip": is_ip,
                "is_suspicious": is_suspicious,
                "reason": reason,
                "risk_weight": risk_weight,
                "category": category
            })

        return results

    def _check_brand_impersonation(self, text: str, sender_domain: str, urls: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()
        for key, info in self.ETHIOPIAN_TARGET_BRANDS.items():
            brand_in_text = key in text_lower or info["name"].lower() in text_lower
            brand_in_sender = bool(sender_domain and key in sender_domain.lower())
            
            if brand_in_text or brand_in_sender:
                is_official_sender = any(sender_domain.endswith(dom) for dom in info["official_domains"]) if sender_domain else False
                if not is_official_sender:
                    return {"brand": info["name"], "key": key}
        return None
