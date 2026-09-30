"""
ETHIO-CYBERGUARD Phishing Email Parser
Extracts headers, bodies (plain text / HTML), attachments, and metadata from raw emails or .eml files.
"""

from typing import Dict, Any, List, Optional
import email
from email import policy
from .eml_parser import EMLParser

class EmailParser:
    """Wrapper and extension over core EMLParser for standardized ingestion."""

    def __init__(self):
        self.raw_parser = EMLParser()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        return self.raw_parser.parse_eml(raw_content)

    def extract_headers_dict(self, raw_content: str) -> Dict[str, str]:
        msg = email.message_from_string(raw_content, policy=policy.default)
        headers = {}
        for k, v in msg.items():
            headers[k] = str(v)
        return headers
