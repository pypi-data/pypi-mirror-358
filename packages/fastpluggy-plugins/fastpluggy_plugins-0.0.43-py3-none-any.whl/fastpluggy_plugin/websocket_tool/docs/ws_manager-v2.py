import asyncio
import time
import uuid
import logging
from typing import Optional, Callable, Dict, List, Tuple

from fastapi import WebSocket, WebSocketDisconnect

from .schema import ConnectionMetadata, DisconnectReason
from .schema.ws_message import WebSocketMessage
from .config import WebSocketSettings

logger = logging.getLogger(__name__)

class ConnectionManagerV2:
    def __init__(self):
        self.settings = WebSocketSettings()

        self.queue: asyncio.Queue[Tuple[WebSocketMessage, Optional[str]]] = asyncio.Queue(
            maxsize=self.settings.max_queue_size
        )

        self.active_connections: Dict[str, ConnectionMetadata] = {}

        self.handlers: Dict[str, Callable] = {}

        self.on_client_connected_hooks: List[Callable] = []
        self.on_client_disconnected_hooks: List[Callable] = []
        self.on_message_received_hooks: List[Callable] = []
        self.on_message_failed_hooks: List[Callable] = []

        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._shutdown = False

    # ---------- Handler registry ----------
    def register_handler(self, msg_type: str, handler: Callable):
        logger.info(f"Registered WS handler for type: {msg_type}")
        self.handlers[msg_type] = handler

    def get_handler(self, msg_type: str) -> Optional[Callable]:
        return self.handlers.get(msg_type)

    # ---------- Hook registration ----------
    def add_hook(self, event: str, hook: Callable):
        if event == "client_connected":
            self.on_client_connected_hooks.append(hook)
        elif event == "client_disconnected":
            self.on_client_disconnected_hooks.append(hook)
        elif event == "message_received":
            self.on_message_received_hooks.append(hook)
        elif event == "message_failed":
            self.on_message_failed_hooks.append(hook)

    # ---------- Core connection mgmt ----------
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        if self._shutdown:
            logger.warning("Reject WS connect: shutting down")
            return False

        if self.loop is None:
            self.loop = asyncio.get_event_loop()

        await websocket.accept()

        connection_key = client_id if client_id else f"anon-{uuid.uuid4()}"
        metadata = ConnectionMetadata(websocket=websocket)
        self.active_connections[connection_key] = metadata

        logger.info(f"[WS] Connected: {connection_key}")

        # Call hooks:
        for hook in self.on_client_connected_hooks:
            await hook(connection_key)

        return True

    async def disconnect(self, websocket_or_client_id, reason: DisconnectReason = DisconnectReason.SERVER_DISCONNECT):
        if isinstance(websocket_or_client_id, str):
            await self._disconnect_client(websocket_or_client_id, reason)
        else:
            for key, meta in list(self.active_connections.items()):
                if meta.websocket == websocket_or_client_id:
                    await self._disconnect_client(key, reason)
                    break

    async def _disconnect_client(self, connection_key: str, reason: DisconnectReason):
        meta = self.active_connections.pop(connection_key, None)
        if meta:
            try:
                await meta.websocket.close()
            except Exception:
                pass

            logger.info(f"[WS] Disconnected: {connection_key} ({reason.value})")

            for hook in self.on_client_disconnected_hooks:
                await hook(connection_key, reason)

    # ---------- Send ----------
    async def send_to_client(self, message: WebSocketMessage, connection_key: Optional[str] = None):
        payload = message.to_json()
        if connection_key:
            meta = self.active_connections.get(connection_key)
            if meta and meta.is_alive:
                try:
                    await meta.websocket.send_json(payload)
                    await self._call_message_received_hooks(connection_key, message.type, payload)
                    return True
                except WebSocketDisconnect:
                    await self._disconnect_client(connection_key, DisconnectReason.CLIENT_DISCONNECT)
                except Exception as e:
                    logger.warning(f"[WS] Send failed to {connection_key}: {e}")
                    await self._call_message_failed_hooks(connection_key, message.type, payload)
                    await self._disconnect_client(connection_key, DisconnectReason.SEND_ERROR)
            return False
        else:
            await self.broadcast(message)
            return True

    async def broadcast(self, message: WebSocketMessage):
        payload = message.to_json()
        for key, meta in list(self.active_connections.items()):
            if meta.is_alive:
                try:
                    await meta.websocket.send_json(payload)
                    await self._call_message_received_hooks(key, message.type, payload)
                except Exception as e:
                    logger.warning(f"[WS] Broadcast failed to {key}: {e}")
                    await self._call_message_failed_hooks(key, message.type, payload)
                    await self._disconnect_client(key, DisconnectReason.SEND_ERROR)

    # ---------- Hook calls ----------
    async def _call_message_received_hooks(self, client_id, msg_type, payload):
        for hook in self.on_message_received_hooks:
            await hook(client_id, msg_type, payload)

    async def _call_message_failed_hooks(self, client_id, msg_type, payload):
        for hook in self.on_message_failed_hooks:
            await hook(client_id, msg_type, payload)

    # ---------- Utility ----------
    def list_clients(self) -> list[dict]:
        return [
            {
                "client_id": key,
                "is_alive": meta.is_alive,
                "connected_at": meta.connected_at,
                "duration": meta.connection_duration
            }
            for key, meta in self.active_connections.items()
        ]

    def get_stats(self):
        return {
            "total_connections": len(self.active_connections),
            "is_shutdown": self._shutdown
        }

    # ---------- Context manager ----------
    async def connection_context(self, websocket: WebSocket, client_id: Optional[str] = None):
        connected = await self.connect(websocket, client_id)
        try:
            if not connected:
                raise Exception("Failed WS connection")
            yield
        except WebSocketDisconnect:
            logger.info(f"[WS] Client {client_id or 'anonymous'} disconnected (normal)")
        except Exception as e:
            logger.error(f"[WS] Connection error {client_id or 'anonymous'}: {e}")
        finally:
            if connected:
                await self.disconnect(client_id if client_id else websocket, DisconnectReason.CLIENT_DISCONNECT)
