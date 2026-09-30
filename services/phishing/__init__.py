"""
ETHIO-CYBERGUARD Phishing Analysis Package
Complete forensic inspection suite for email headers, links, attachments, authentication, and regional lures.
"""

from .email_analyzer import PhishingAnalyzer
from .eml_parser import EMLParser
from .auth_verifier import EmailAuthVerifier
from .risk_scorer import PhishingRiskScorer
from .parser import EmailParser
from .spf import SPFVerifier
from .dkim import DKIMVerifier
from .dmarc import DMARCVerifier
from .header_analysis import HeaderAnalyzer
from .url_analysis import URLAnalyzer
from .attachment_analysis import AttachmentAnalyzer
from .amharic_detection import AmharicDetector
from .risk_scoring import ExplainableRiskScorer

__all__ = [
    "PhishingAnalyzer",
    "EMLParser",
    "EmailAuthVerifier",
    "PhishingRiskScorer",
    "EmailParser",
    "SPFVerifier",
    "DKIMVerifier",
    "DMARCVerifier",
    "HeaderAnalyzer",
    "URLAnalyzer",
    "AttachmentAnalyzer",
    "AmharicDetector",
    "ExplainableRiskScorer"
]
