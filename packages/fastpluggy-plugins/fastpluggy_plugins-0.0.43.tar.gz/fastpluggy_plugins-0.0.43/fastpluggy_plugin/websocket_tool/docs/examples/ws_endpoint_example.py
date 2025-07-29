# Example of using the ConnectionManager with handler registry and event hooks
import json
import logging
from typing import Dict, Any

from fastapi import WebSocket, WebSocketDisconnect
from fastpluggy.fastpluggy import FastPluggy
from websocket_tool.schema.ws_message import WebSocketMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example handlers for different message types
async def handle_ping(client_id: str, data: Dict[str, Any]):
    """Handler for ping messages"""
    logger.info(f"Handling ping from {client_id}")
    manager = FastPluggy.get_global("ws_manager")
    
    # Create pong response
    ping_id = data.get('meta', {}).get('ping_id', 'unknown')
    reply = WebSocketMessage(
        type="pong",
        content=f"Pong response to {ping_id}",
        meta={
            "ping_id": ping_id,
            "from": "server"
        }
    )
    
    # Send response
    await manager.send_to_client(reply, client_id)

async def handle_chat(client_id: str, data: Dict[str, Any]):
    """Handler for chat messages"""
    logger.info(f"Handling chat message from {client_id}")
    manager = FastPluggy.get_global("ws_manager")
    
    # Extract message content
    message = data.get('content', '')
    
    # Create broadcast message
    broadcast_msg = WebSocketMessage(
        type="chat",
        content=message,
        meta={
            "from": client_id,
            "broadcast": True
        }
    )
    
    # Broadcast to all clients
    await manager.broadcast(broadcast_msg)

# Example hooks


async def on_client_connected(client_id: str):
    """Hook called when a client connects"""
    logging.info(f"Client connected hook: {client_id}")
    manager = FastPluggy.get_global("ws_manager")

    # Send welcome message
    welcome_msg = WebSocketMessage(
        type="system",
        content=f"Welcome {client_id}!",
        meta={
            "event": "connected"
        }
    )

    await manager.send_to_client(welcome_msg, client_id)


async def on_client_disconnected(client_id: str, reason):
    """Hook called when a client disconnects"""
    logging.info(f"Client disconnected hook: {client_id}, reason: {reason}")

async def on_message_received(client_id: str, msg_type: str, payload: dict):
    """Hook called when a message is successfully sent"""
    logger.debug(f"Message sent to {client_id}, type: {msg_type}")

# Function to register handlers and hooks
def setup_websocket_handlers():
    """Register handlers and hooks with the connection manager"""
    manager = FastPluggy.get_global("ws_manager")
    if not manager:
        logger.error("WebSocket manager not available")
        return
    
    # Register message handlers
    manager.register_handler("ping", handle_ping)
    manager.register_handler("chat", handle_chat)
    
    # Register event hooks
    manager.add_hook("client_connected", on_client_connected)
    manager.add_hook("client_disconnected", on_client_disconnected)
    manager.add_hook("message_received", on_message_received)
    
    logger.info("WebSocket handlers and hooks registered")

# Modified websocket endpoint using the handler registry
async def websocket_endpoint_example(websocket: WebSocket, client_id: str = None):
    """Example WebSocket endpoint using handler registry and hooks"""
    manager = FastPluggy.get_global("ws_manager")
    if not manager:
        logger.error("WebSocket manager not available")
        await websocket.close(code=1011, reason="Server error")
        return
    
    # Extract client_id from query params if not provided
    if client_id is None:
        client_id = websocket.query_params.get("clientId")
    
    logger.info(f"WebSocket connection attempt: {client_id or 'anonymous'}")
    
    # Use the connection context manager for automatic cleanup
    async with manager.connection_context(websocket, client_id):
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                logger.debug(f"Received from {client_id or 'anonymous'}: {data}")
                
                # Process message using handler registry
                success = await manager.process_message(client_id, data)
                
                if not success:
                    # Fallback for unhandled message types
                    try:
                        payload = json.loads(data)
                        reply = WebSocketMessage(
                            type="error",
                            content="Unhandled message type",
                            meta={
                                "original_type": payload.get("type", "unknown")
                            }
                        )
                        await manager.send_to_client(reply, client_id)
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid JSON from {client_id}")
                
        except WebSocketDisconnect:
            logger.info(f"Client {client_id or 'anonymous'} disconnected normally")
        except Exception as e:
            logger.error(f"WebSocket error for {client_id or 'anonymous'}: {e}")

# Usage example
if __name__ == "__main__":
    # This would typically be called during application startup
    setup_websocket_handlers()