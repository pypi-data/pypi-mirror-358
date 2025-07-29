# WebSocket Handler Registry and Event Hooks

This document explains the new features added to the ConnectionManager: handler registry and event hooks.

## Overview

The ConnectionManager has been enhanced with two new features:

1. **Handler Registry**: A system to register message handlers for specific message types, allowing for more organized and modular code.
2. **Event Hooks**: A mechanism to register callback functions that are triggered on specific events (connection, disconnection, message received/failed).

These features simplify WebSocket handling by:
- Decoupling message handling logic from the WebSocket endpoint
- Providing a standardized way to react to WebSocket events
- Making the code more maintainable and testable

## Handler Registry

The handler registry allows you to register functions that handle specific message types.

### How to Register Handlers

```python
# Get the connection manager
manager = FastPluggy.get_global("ws_manager")

# Register a handler for a specific message type
manager.register_handler("ping", handle_ping)
manager.register_handler("chat", handle_chat)
```

### Handler Function Signature

Handler functions should have the following signature:

```python
async def handle_message_type(client_id: str, data: Dict[str, Any]):
    """Handle a specific message type"""
    # Your handling logic here
```

### Processing Messages with Handlers

Use the `process_message` method to process incoming messages using the registered handlers:

```python
# In your WebSocket endpoint
data = await websocket.receive_text()
success = await manager.process_message(client_id, data)
```

## Event Hooks

Event hooks allow you to register callback functions that are triggered on specific events.

### Available Events

- `client_connected`: Called when a client connects
- `client_disconnected`: Called when a client disconnects
- `message_received`: Called when a message is successfully sent to a client
- `message_failed`: Called when sending a message to a client fails

### How to Register Hooks

```python
# Get the connection manager
manager = FastPluggy.get_global("ws_manager")

# Register hooks for specific events
manager.add_hook("client_connected", on_client_connected)
manager.add_hook("client_disconnected", on_client_disconnected)
manager.add_hook("message_received", on_message_received)
manager.add_hook("message_failed", on_message_failed)
```

### Hook Function Signatures

Each hook type has a specific signature:

```python
# Client connected hook
async def on_client_connected(client_id: str):
    """Called when a client connects"""
    # Your logic here

# Client disconnected hook
async def on_client_disconnected(client_id: str, reason: DisconnectReason):
    """Called when a client disconnects"""
    # Your logic here

# Message received hook
async def on_message_received(client_id: str, msg_type: str, payload: dict):
    """Called when a message is successfully sent"""
    # Your logic here

# Message failed hook
async def on_message_failed(client_id: str, msg_type: str, payload: dict):
    """Called when sending a message fails"""
    # Your logic here
```

## Example Usage

### Basic WebSocket Endpoint

```python
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """WebSocket endpoint using handler registry and hooks"""
    manager = FastPluggy.get_global("ws_manager")
    
    # Use the connection context manager
    async with manager.connection_context(websocket, client_id):
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                # Process message using handler registry
                await manager.process_message(client_id, data)
                
        except WebSocketDisconnect:
            pass
```

### Setting Up Handlers and Hooks

```python
def setup_websocket_handlers():
    """Register handlers and hooks with the connection manager"""
    manager = FastPluggy.get_global("ws_manager")
    
    # Register message handlers
    manager.register_handler("ping", handle_ping)
    manager.register_handler("chat", handle_chat)
    
    # Register event hooks
    manager.add_hook("client_connected", on_client_connected)
    manager.add_hook("client_disconnected", on_client_disconnected)
```

## Complete Examples

For complete examples of how to use these features, see:

1. `websocket_tool/examples/ws_endpoint_example.py`: Example for a basic WebSocket endpoint
2. `audio-transcript/fp-server/examples/audio_live_ws_example.py`: Example for audio transcription WebSocket

## Implementation Details

The implementation adds the following to the ConnectionManager:

1. Handler registry dictionary and methods:
   - `register_handler(msg_type, handler)`
   - `get_handler(msg_type)`
   - `process_message(client_id, message_data)`

2. Event hook lists and methods:
   - `add_hook(event, hook)`
   - `_call_client_connected_hooks(connection_key)`
   - `_call_client_disconnected_hooks(connection_key, reason)`
   - `_call_message_received_hooks(client_id, msg_type, payload)`
   - `_call_message_failed_hooks(client_id, msg_type, payload)`

3. Integration with existing methods:
   - `connect`: Calls client_connected hooks
   - `_disconnect_client`: Calls client_disconnected hooks
   - `send_to_client`: Calls message_received/failed hooks
   - `_safe_send_with_metadata`: Calls message_received/failed hooks

## Benefits

1. **Modularity**: Message handling logic is separated from connection management
2. **Extensibility**: Easy to add new message types and event reactions
3. **Maintainability**: Cleaner code with clear separation of concerns
4. **Testability**: Handlers and hooks can be tested independently
5. **Flexibility**: Can be used with different WebSocket endpoints and use cases