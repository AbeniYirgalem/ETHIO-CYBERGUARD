"""
ETHIO-CYBERGUARD RFC-822 EML File Parser
Extracts headers, authentication chains, body text, attachments, and URLs from raw email messages.
"""

from typing import Dict, Any, List, Optional
import email
from email import policy
import re
from urllib.parse import urlparse


class EMLParser:
    """
    Robust RFC-822 email parser for corporate and national MTA feeds.
    """

    URL_REGEX = re.compile(r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]+(?::\d+)?(?:/[^\s\"'<>]*)?")

    def parse(self, raw_eml_content: str) -> Dict[str, Any]:
        parsed = email.message_from_string(raw_eml_content, policy=policy.default)
        
        headers: Dict[str, str] = {k.lower(): str(v) for k, v in parsed.items()}
        subject = str(parsed.get("subject", ""))
        sender = str(parsed.get("from", ""))
        to = str(parsed.get("to", ""))
        reply_to = str(parsed.get("reply-to", ""))
        return_path = str(parsed.get("return-path", ""))
        date_str = str(parsed.get("date", ""))
        message_id = str(parsed.get("message-id", ""))

        # Extract text body and attachments
        body_text = ""
        attachments = []

        if parsed.is_multipart():
            for part in parsed.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))
                filename = part.get_filename()

                if filename or "attachment" in disposition:
                    attachments.append({
                        "filename": filename or "unnamed_attachment",
                        "content_type": content_type,
                        "size": len(part.get_payload(decode=True) or b"")
                    })
                elif content_type in ["text/plain", "text/html"]:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_text += payload.decode(errors="ignore") + "\n"
        else:
            payload = parsed.get_payload(decode=True)
            body_text = payload.decode(errors="ignore") if payload else raw_eml_content

        # Extract URLs, domains, and IPs
        urls = list(set(self.URL_REGEX.findall(f"{body_text} {raw_eml_content}")))
        domains = []
        ips = []

        for u in urls:
            try:
                host = urlparse(u).hostname or ""
                if host:
                    domains.append(host.lower())
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
                        ips.append(host)
            except Exception:
                pass

        return {
            "from": sender,
            "to": to,
            "reply_to": reply_to,
            "return_path": return_path,
            "subject": subject,
            "date": date_str,
            "message_id": message_id,
            "headers": headers,
            "body": body_text,
            "attachments": attachments,
            "urls": urls,
            "domains": list(set(domains)),
            "ips": list(set(ips))
        }
