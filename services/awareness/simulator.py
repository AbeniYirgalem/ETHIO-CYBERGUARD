"""
ETHIO-CYBERGUARD - Cyber Awareness Training & Phishing Simulation Engine
Provides localized corporate awareness campaigns in English and Amharic,
tracks employee susceptibility, reporting rates, and micro-learning modules.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CampaignTemplate:
    id: str
    title_en: str
    title_am: str
    target_vector: str  # SMS, Email, QR Code, Portal
    difficulty: str  # Easy, Moderate, Advanced
    spoofed_sender: str
    subject_en: str
    subject_am: str
    body_en: str
    body_am: str
    clues: List[str]
    category: str


class AwarenessSimulator:
    """
    Simulates enterprise phishing campaigns and tracks cybersecurity culture metrics.
    """

    CAMPAIGNS: List[CampaignTemplate] = [
        CampaignTemplate(
            id="camp-telebirr-prize",
            title_en="Telebirr 10,000 Birr Anniversary Prize Scam",
            title_am="የ10,000 ብር የቴሌብር አመታዊ ሽልማት ማታለያ",
            target_vector="SMS / Mobile Message",
            difficulty="Moderate",
            spoofed_sender="telebirr-award@telecom-promo.xyz",
            subject_en="Congratulations! You have been selected for 10,000 Birr Telebirr Bonus",
            subject_am="እንኳን ደስ አሎት! የ10,000 ብር የቴሌብር ቦነስ አሸንፈዋል",
            body_en=(
                "Dear Valued Customer, Congratulations! Your active phone number has won 10,000 ETB "
                "in the National Digital Economy promotion. To claim your reward directly into your Telebirr wallet, "
                "click: http://telebirr-claim.xyz/verify?id=92849 within 24 hours. Enter your registered PIN to verify."
            ),
            body_am=(
                "ክቡር ደንበኛችን እንኳን ደስ አሎት! በብሔራዊ የዲጂታል ኢኮኖሚ ማበረታቻ ፕሮግራም የ10,000 ብር ተሸላሚ ሆነዋል። "
                "ሽልማቱን በቀጥታ ወደ ቴሌብር አካውንትዎ ለማስገባት በ24 ሰዓት ውስጥ http://telebirr-claim.xyz/verify?id=92849 ይጫኑና "
                "የቴሌብር ፒን ቁጥርዎን በማስገባት ያረጋግጡ።"
            ),
            clues=[
                "Official Telebirr domain is telebirr.et, NOT telebirr-claim.xyz.",
                "Ethio Telecom / Telebirr will NEVER ask for your secret PIN or OTP.",
                "High psychological urgency ('within 24 hours') is a classic phishing indicator."
            ],
            category="Financial & Mobile Money Fraud"
        ),
        CampaignTemplate(
            id="camp-cbe-kyc",
            title_en="Commercial Bank of Ethiopia (CBE) Birr Security Re-verification",
            title_am="የኢትዮጵያ ንግድ ባንክ አስቸኳይ የደህንነት ማረጋገጫ",
            target_vector="Email",
            difficulty="Advanced",
            spoofed_sender="security-alert@combanketh-portal.com",
            subject_en="URGENT: Temporary Restriction on CBE Birr / Internet Banking Account",
            subject_am="አስቸኳይ፡ በኢትዮጵያ ንግድ ባንክ መለያዎ ላይ የተጣለ ጊዜያዊ እገዳ",
            body_en=(
                "Dear CBE Customer, Under National Bank of Ethiopia Directive No. SBB/89/2026, "
                "all internet banking and CBE Birr users must complete biometric re-verification by 5:00 PM today. "
                "Failure to comply will result in suspension of debit cards and fund transfers. "
                "Complete KYC now: https://cbe-ebanking-auth.net/portal/kyc"
            ),
            body_am=(
                "ክቡር የኢትዮጵያ ንግድ ባንክ ደንበኛ፡ በብሔራዊ ባንክ መመሪያ ቁጥር SBB/89/2026 መሰረት ሁሉም የኦንላይን ባንኪንግ "
                "እና CBE Birr ተጠቃሚዎች ዛሬ ከቀኑ 11:00 ሰዓት በፊት የማንነት ማረጋገጫ (KYC) ማጠናቀቅ አለባቸው። "
                "ይህን ካላደረጉ ካርድዎ እና የገንዘብ ዝውውርዎ ይታገዳል። አሁኑኑ ያረጋግጡ፡ https://cbe-ebanking-auth.net/portal/kyc"
            ),
            clues=[
                "The sender domain is combanketh-portal.com, whereas the real CBE domain is combanketh.et.",
                "Banks do not issue 2-hour ultimatums threatening immediate account freeze via unverified links.",
                "Always check the URL in the browser address bar before typing passwords."
            ],
            category="Banking Credential Harvesting"
        ),
        CampaignTemplate(
            id="camp-aau-sso",
            title_en="Addis Ababa University (AAU) Academic Portal Password Reset",
            title_am="የአዲስ አበባ ዩኒቨርሲቲ የፖርታል የይለፍ ቃል ማደሻ",
            target_vector="Email",
            difficulty="Easy",
            spoofed_sender="helpdesk@aau-auth.org",
            subject_en="Action Required: Your AAU Academic Staff & Student Password Has Expired",
            subject_am="አስቸኳይ፡ የአዲስ አበባ ዩኒቨርሲቲ የይለፍ ቃልዎ ጊዜው አልቋል",
            body_en=(
                "University IT Service Notice: Your campus portal account password expires today. "
                "To maintain uninterrupted access to the digital library, registrar grade records, and campus WiFi, "
                "synchronize your password here: https://portal-aau.org/login"
            ),
            body_am=(
                "የዩኒቨርሲቲው አይቲ ማስታወቂያ፡ የካምፓስ ፖርታል አካውንትዎ የይለፍ ቃል ዛሬ ያበቃል። "
                "የዲጂታል ላይብረሪ፣ የሬጅስትራር ውጤቶች እና የካምፓስ ዋይፋይ እንዳይቋረጥብዎ የይለፍ ቃልዎን እዚህ ያድሱ፡ https://portal-aau.org/login"
            ),
            clues=[
                "Official university domain is aau.edu.et, not aau-auth.org or portal-aau.org.",
                "Look for generic greetings rather than addressing you by official university matriculation ID."
            ],
            category="Higher Education & Student Portal Phishing"
        ),
        CampaignTemplate(
            id="camp-payroll-bonus",
            title_en="HR Ethiopian New Year (Enkutatash) Performance Bonus",
            title_am="የአዲሱ ዓመት (እንቁጣጣሽ) የስራ አፈጻጸም ቦነስ ማስታወቂያ",
            target_vector="Email",
            difficulty="Moderate",
            spoofed_sender="payroll@company-hr-portal.com",
            subject_en="Confidential: 2026/2019 Enkutatash Bonus & Salary Adjustment Schedule",
            subject_am="ሚስጥራዊ፡ የ2019 የእንቁጣጣሽ ቦነስ እና የደመወዝ ጭማሪ ሰነድ",
            body_en=(
                "Good day team, Management has approved special holiday performance bonuses for eligible staff. "
                "Review your individual bonus calculation and direct deposit bank account details in the attached spreadsheet: "
                "Download: http://196.188.42.10/payroll/bonus_breakdown.xlsx.exe"
            ),
            body_am=(
                "ውድ የስራ ባልደረቦች፡ የድርጅቱ ማኔጅመንት የአዲሱን ዓመት አስመልክቶ ልዩ የቦነስ አበል ፈቅዷል። "
                "የተመደበልዎትን ቦነስ እና የሚገባበትን የባንክ ሂሳብ ዝርዝር ለማየት የተያያዘውን ሰነድ ያውርዱ፡ "
                "http://196.188.42.10/payroll/bonus_breakdown.xlsx.exe"
            ),
            clues=[
                "The link is a direct IP address with a double extension (.xlsx.exe) containing executable malware.",
                "Payroll discussions are communicated through official internal channels, not anonymous external links.",
                "Curiosity/greed lure exploiting holidays and bonuses."
            ],
            category="Executive & Internal Payroll Impersonation"
        )
    ]

    ORGANIZATION_STATS = {
        "organization_name": "Ethiopian Corporate Sector Average",
        "total_employees_simulated": 1420,
        "overall_phish_prone_percentage": 14.8,
        "reporting_rate_percentage": 52.4,
        "national_benchmark_comparison": "Top 15% (Significantly better than 28% national average)",
        "departments": [
            {
                "department": "Finance & Accounting",
                "employees": 180,
                "click_rate": 18.2,
                "compromised_rate": 6.1,
                "reported_rate": 58.0,
                "risk_rating": "MODERATE"
            },
            {
                "department": "IT & Infrastructure",
                "employees": 120,
                "click_rate": 4.1,
                "compromised_rate": 0.8,
                "reported_rate": 84.5,
                "risk_rating": "LOW"
            },
            {
                "department": "Human Resources",
                "employees": 95,
                "click_rate": 19.5,
                "compromised_rate": 8.4,
                "reported_rate": 46.2,
                "risk_rating": "HIGH"
            },
            {
                "department": "Customer Operations & Branch",
                "employees": 725,
                "click_rate": 22.0,
                "compromised_rate": 11.2,
                "reported_rate": 39.8,
                "risk_rating": "CRITICAL"
            },
            {
                "department": "Executive Leadership",
                "employees": 30,
                "click_rate": 13.3,
                "compromised_rate": 3.3,
                "reported_rate": 60.0,
                "risk_rating": "MODERATE"
            }
        ]
    }

    def get_campaigns(self) -> List[Dict[str, Any]]:
        """Return all available awareness simulation templates."""
        return [
            {
                "id": c.id,
                "title_en": c.title_en,
                "title_am": c.title_am,
                "target_vector": c.target_vector,
                "difficulty": c.difficulty,
                "spoofed_sender": c.spoofed_sender,
                "subject_en": c.subject_en,
                "subject_am": c.subject_am,
                "body_en": c.body_en,
                "body_am": c.body_am,
                "clues": c.clues,
                "category": c.category
            }
            for c in self.CAMPAIGNS
        ]

    def get_org_metrics(self) -> Dict[str, Any]:
        """Return organizational simulation metrics and department risk profiles."""
        return self.ORGANIZATION_STATS

    def launch_simulation(self, campaign_id: str, department: str = "All") -> Dict[str, Any]:
        """Simulate sending a campaign to an organizational unit."""
        campaign = next((c for c in self.CAMPAIGNS if c.id == campaign_id), self.CAMPAIGNS[0])
        return {
            "status": "LAUNCHED",
            "campaign_id": campaign.id,
            "campaign_title": campaign.title_en,
            "target_department": department,
            "estimated_recipients": 1420 if department == "All" else 250,
            "tracking_active": True,
            "message": f"Simulation '{campaign.title_en}' dispatched successfully. Click tracking and instant training landing pages activated."
        }
