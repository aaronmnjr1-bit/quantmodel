from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    """Manages all active WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self._connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self._connections)}")

    async def broadcast(self, payload: Any) -> None:
        if not self._connections:
            return
        message = json.dumps(payload, default=str)
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_to(self, websocket: WebSocket, payload: Any) -> None:
        try:
            await websocket.send_text(json.dumps(payload, default=str))
        except Exception as exc:
            logger.warning(f"Failed to send to client: {exc}")
            self.disconnect(websocket)

    async def handle_client_message(self, websocket: WebSocket, raw: str) -> None:
        try:
            data = json.loads(raw)
            msg_type = data.get("type", "")
            if msg_type == "ping":
                await self.send_to(websocket, {"type": "pong"})
        except json.JSONDecodeError:
            pass

    @property
    def connection_count(self) -> int:
        return len(self._connections)
