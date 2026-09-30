"""
Base External Integration Connector for ETHIO-CYBERGUARD
Provides health checks, circuit breakers, timeout handling, retries, and audit logging.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class CircuitBreakerState:
    CLOSED = "CLOSED" # Normal operation
    OPEN = "OPEN" # Failing, fast-rejecting
    HALF_OPEN = "HALF_OPEN" # Testing recovery

class BaseConnector(ABC):
    def __init__(self, connector_id: str, name: str, connector_type: str, timeout_seconds: float = 5.0):
        self.connector_id = connector_id
        self.name = name
        self.connector_type = connector_type
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.failure_threshold = 3
        self.circuit_state = CircuitBreakerState.CLOSED
        self.last_failure_time: Optional[float] = None
        self.recovery_timeout_seconds = 30.0

    def check_circuit(self) -> bool:
        """Returns True if request can proceed, False if circuit is OPEN."""
        now = time.time()
        if self.circuit_state == CircuitBreakerState.OPEN:
            if self.last_failure_time and (now - self.last_failure_time > self.recovery_timeout_seconds):
                self.circuit_state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        self.circuit_state = CircuitBreakerState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.circuit_state = CircuitBreakerState.OPEN

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Performs connectivity & credential validation."""
        pass

    @abstractmethod
    def execute_action(self, action: str, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes containment or enforcement action."""
        pass
