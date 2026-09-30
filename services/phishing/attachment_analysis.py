"""
ETHIO-CYBERGUARD Attachment Safety & Malware Indicator Engine
Detects dangerous extensions, macro-enabled documents, archive payloads, and double extensions.
"""

from typing import List, Dict, Any

class AttachmentAnalyzer:
    """Evaluates attachment safety and potential payload vectors."""

    DANGEROUS_EXTENSIONS = {
        ".exe", ".scr", ".bat", ".cmd", ".vbs", ".js", ".hta", ".iso", ".img", 
        ".ps1", ".wsf", ".jar", ".cpl", ".msi"
    }
    MACRO_EXTENSIONS = {".docm", ".xlsm", ".pptm", ".dotm", ".xltm"}
    ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz"}

    @staticmethod
    def inspect_attachment(filename: str, size_bytes: int = 0) -> Dict[str, Any]:
        fn_lower = filename.lower()
        
        # Check double extensions (e.g. invoice.pdf.exe)
        parts = fn_lower.split(".")
        has_double_ext = len(parts) > 2 and f".{parts[-1]}" in AttachmentAnalyzer.DANGEROUS_EXTENSIONS

        is_dangerous = any(fn_lower.endswith(ext) for ext in AttachmentAnalyzer.DANGEROUS_EXTENSIONS)
        has_macro = any(fn_lower.endswith(ext) for ext in AttachmentAnalyzer.MACRO_EXTENSIONS)
        is_archive = any(fn_lower.endswith(ext) for ext in AttachmentAnalyzer.ARCHIVE_EXTENSIONS)

        points = 0
        reasons = []
        if is_dangerous:
            points += 40
            reasons.append(f"Executable or dangerous script extension detected ({parts[-1]})")
        if has_double_ext:
            points += 50
            reasons.append("Deceptive double file extension observed (e.g., .pdf.exe)")
        if has_macro:
            points += 30
            reasons.append("VBA Macro-enabled Office document file type")
        if is_archive and size_bytes > 0 and size_bytes < 50000:
            points += 15
            reasons.append("Small archive file commonly used to evade basic content filters")

        return {
            "filename": filename,
            "size_bytes": size_bytes,
            "is_dangerous": points >= 30,
            "risk_points": points,
            "reasons": reasons
        }
