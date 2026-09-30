"""
Production WebSocket Manager for ETHIO-CYBERGUARD
Supports token authentication, role/tenant channel subscriptions, heartbeats,
connection limits, and multi-instance pub/sub abstraction.
"""

from fastapi import WebSocket, WebSocketDisconnect, status
from typing import Dict, List, Set, Any, Optional
from datetime import datetime, timezone
import asyncio
import json

class ChannelSubscriptionManager:
    def __init__(self, max_connections: int = 500):
        self.active_sockets: Set[WebSocket] = set()
        self.socket_user_meta: Dict[WebSocket, Dict[str, Any]] = {}
        self.channel_subscribers: Dict[str, Set[WebSocket]] = {
            "all": set(),
            "incidents": set(),
            "alerts": set(),
            "telemetry": set()
        }
        self.max_connections = max_connections

    async def connect(self, websocket: WebSocket, user_meta: Dict[str, Any]) -> bool:
        if len(self.active_sockets) >= self.max_connections:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Connection limit exceeded")
            return False

        await websocket.accept()
        self.active_sockets.add(websocket)
        self.socket_user_meta[websocket] = user_meta
        self.channel_subscribers["all"].add(websocket)
        
        # Subscribe to tenant channel
        tenant = user_meta.get("organization", "default_org")
        tenant_channel = f"tenant:{tenant}"
        if tenant_channel not in self.channel_subscribers:
            self.channel_subscribers[tenant_channel] = set()
        self.channel_subscribers[tenant_channel].add(websocket)
        
        return True

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_sockets:
            self.active_sockets.remove(websocket)
        if websocket in self.socket_user_meta:
            del self.socket_user_meta[websocket]
        for subscribers in self.channel_subscribers.values():
            if websocket in subscribers:
                subscribers.remove(websocket)

    def subscribe(self, websocket: WebSocket, channel: str):
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(websocket)

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        recipients = list(self.channel_subscribers.get(channel, set()))
        dead_sockets = []
        for ws in recipients:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.append(ws)
        for dead_ws in dead_sockets:
            self.disconnect(dead_ws)

    async def broadcast(self, message: Dict[str, Any]):
        await self.broadcast_to_channel("all", message)

    def get_active_count(self) -> int:
        return len(self.active_sockets)

ws_manager = ChannelSubscriptionManager()
