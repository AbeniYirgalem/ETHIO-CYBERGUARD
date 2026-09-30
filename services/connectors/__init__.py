"""
External Integrations & Connectors for ETHIO-CYBERGUARD
"""

from .base import BaseConnector, CircuitBreakerState
from .firewall import FirewallConnector
from .edr import EDRConnector
from .email_gateway import EmailGatewayConnector
from .dns import DNSSinkholeConnector

CONNECTOR_REGISTRY = {
    "conn-fw-01": FirewallConnector(),
    "conn-edr-01": EDRConnector(),
    "conn-mail-01": EmailGatewayConnector(),
    "conn-dns-01": DNSSinkholeConnector()
}

__all__ = [
    "BaseConnector",
    "CircuitBreakerState",
    "FirewallConnector",
    "EDRConnector",
    "EmailGatewayConnector",
    "DNSSinkholeConnector",
    "CONNECTOR_REGISTRY"
]
