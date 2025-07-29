# WebSocketTool Plugin for FastPluggy

The WebSocketTool plugin provides real-time WebSocket communication capabilities for FastPluggy applications. It enables bidirectional communication between the server and clients, supports message broadcasting, targeted messaging, and integrates with the task worker system for real-time task monitoring.

## Installation

### Requirements

- FastPluggy framework >=0.0.3
- UI Tools plugin >=0.0.3

### Installation Steps

1. Install the plugin package:

```bash
pip install fastpluggy-websocket-tool
```

2. Add the plugin to your FastPluggy configuration:

```python
from fastpluggy.fastpluggy import FastPluggy
from fastpluggy_plugin.websocket_tool.plugin import WebSocketToolPlugin

app = FastPluggy()
app.register_module(WebSocketToolPlugin())
```

## Configuration

The WebSocketTool plugin can be configured through the `WebSocketSettings` class:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `max_queue_size` | int | 10000 | Maximum size of the message queue |
| `enable_heartbeat` | bool | True | Enable heartbeat mechanism to monitor connection health |
| `heartbeat_interval` | int | 30 | Seconds between heartbeat pings |
| `heartbeat_timeout` | int | 60 | Seconds before a connection is considered timed out |

Example configuration:

```python
from fastpluggy.fastpluggy import FastPluggy
from fastpluggy_plugin.websocket_tool.plugin import WebSocketToolPlugin
from fastpluggy_plugin.websocket_tool.config import WebSocketSettings

# Custom settings
custom_settings = WebSocketSettings(
    max_queue_size=20000,
    heartbeat_interval=15,
    heartbeat_timeout=45
)

app = FastPluggy()
app.register_module(WebSocketToolPlugin(module_settings=custom_settings))
```

## Core Components

### ConnectionManager

The `ConnectionManager` class is the central component that manages WebSocket connections. It provides:

- Connection tracking with metadata
- Message broadcasting to all clients
- Targeted messaging to specific clients
- Heartbeat mechanism for connection health monitoring
- Asynchronous message queue for handling high volumes
- Connection statistics and health monitoring

### WebSocketMessage

The `WebSocketMessage` class defines the structure of messages sent over WebSockets:

```python
@dataclass
class WebSocketMessage:
    type: str  # e.g. "log", "status", "message", "heartbeat"
    content: Any  # Main message content
    meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### AsyncWidget

The `AsyncWidget` class provides asynchronous loading of UI components:

- Initially renders a spinner while content loads
- Processes subwidgets in the background
- Delivers rendered HTML via WebSockets when ready
- Improves UI responsiveness for complex or slow-loading components

## API Reference

### WebSocket Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ws/{client_id}` | WebSocket | Connect with a specific client ID |
| `/ws` | WebSocket | Connect with an auto-generated client ID |

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ws/send-message` | POST | Send a message to one or all clients |
| `/ws/stats` | GET | Get WebSocket manager statistics |
| `/ws/clients` | GET | List all connected WebSocket clients |
| `/ws/clients/{client_id}` | DELETE | Disconnect a specific client |
| `/ws/health` | GET | Health check endpoint for monitoring |

### Admin Interface

The plugin provides an admin dashboard accessible through the FastPluggy admin interface:

- WebSocket clients monitoring dashboard
- Connection statistics and health metrics
- Client management (disconnect clients)
- Message broadcasting interface

## Integration with Other Modules

### Tasks Worker Integration

When the Tasks Worker module is available, the WebSocketTool plugin automatically:

1. Registers a WebSocketNotifier for task events
2. Streams task logs in real-time to WebSocket clients
3. Sends task completion notifications
4. Provides real-time monitoring of task execution

Example of receiving task events in the browser:

```javascript
// Connect to WebSocket
const socket = new WebSocket(`ws://${window.location.host}/ws/client-123`);

// Listen for task events
socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'task_success') {
        console.log('Task completed successfully:', data.meta.task_id);
    } else if (data.type === 'logs') {
        console.log(`[${data.meta.level}] ${data.content}`);
    }
});
```

## Client-Side Usage

### Connecting to WebSocket

```javascript
// Connect with a specific client ID
const socket = new WebSocket(`ws://${window.location.host}/ws/client-123`);

// Or connect anonymously
const socket = new WebSocket(`ws://${window.location.host}/ws`);

// Handle connection events
socket.addEventListener('open', (event) => {
    console.log('Connected to WebSocket server');
});

socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    console.log('Message from server:', data);
});

socket.addEventListener('close', (event) => {
    console.log('Disconnected from WebSocket server');
});
```

### Handling Heartbeats

The server sends periodic ping messages to check connection health. Clients should respond with pong messages:

```javascript
socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    
    // Respond to ping messages
    if (data.type === 'ping') {
        socket.send(JSON.stringify({
            type: 'pong',
            content: 'pong',
            meta: {
                ping_id: data.meta.ping_id,
                timestamp: Date.now()
            }
        }));
    }
});
```

### Using AsyncWidget

The AsyncWidget allows for asynchronous loading of UI components:

```python
from fastpluggy.core.widgets import TableWidget
from fastpluggy_plugin.websocket_tool.extra_widget.async_widget import AsyncWidget

# Create an AsyncWidget with subwidgets
async_widget = AsyncWidget(
    subwidgets=[
        TableWidget(
            title="Large Data Table",
            data=large_dataset,
            # ... other options
        )
    ]
)

# Use in your view
return view_builder.generate(
    request,
    title="Dashboard",
    widgets=[async_widget]
)
```

## Advanced Usage

### Custom WebSocket Message Handlers

You can extend the WebSocket functionality by implementing custom message handlers:

```python
from fastpluggy.fastpluggy import FastPluggy
from fastpluggy_plugin.websocket_tool.schema.ws_message import WebSocketMessage

# Get the WebSocket manager
ws_manager = FastPluggy.get_global("ws_manager")

# Create and send a custom message
custom_message = WebSocketMessage(
    type="custom_event",
    content="Something important happened!",
    meta={
        "event_id": "12345",
        "severity": "high"
    }
)

# Broadcast to all clients
ws_manager.notify(custom_message)

# Or send to a specific client
ws_manager.notify(custom_message, connection_key="client-123")
```

### Health Monitoring

The plugin provides health monitoring endpoints that can be integrated with monitoring systems:

```bash
# Check WebSocket system health
curl http://your-app/ws/health

# Get detailed statistics
curl http://your-app/ws/stats

# List connected clients
curl http://your-app/ws/clients
```

## Troubleshooting

### Common Issues

1. **Connection Failures**: Ensure the WebSocket endpoint is accessible and not blocked by proxies or firewalls.

2. **Message Queue Overflow**: If you see queue overflow errors, consider:
   - Increasing `max_queue_size` in settings
   - Optimizing message frequency
   - Adding more server resources

3. **High Heartbeat Timeouts**: If many connections are timing out:
   - Check network stability
   - Increase `heartbeat_timeout` for unstable networks
   - Ensure clients are responding to ping messages

### Logging

The plugin uses the standard logging system. To enable debug logs:

```python
import logging
logging.getLogger("fastpluggy_plugin.websocket_tool").setLevel(logging.DEBUG)
```

## License

This plugin is licensed under the same license as the FastPluggy framework.