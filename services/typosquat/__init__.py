"""
ETHIO-CYBERGUARD - Typosquatting & Brand Defense Monitor
Inspired by openSquat, tailored for Ethiopian banking, government, and telecom sectors.
"""

from .domain_monitor import TyposquatMonitor, TyposquatFinding

__all__ = ["TyposquatMonitor", "TyposquatFinding"]
