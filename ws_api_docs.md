# WebSocket API Documentation

Endpoint: `/ws`

Method: WebSocket

Description: WebSocket endpoint for real-time communication.

This endpoint handles the WebSocket connection for the MagenticOne application.
It manages the connection lifecycle, processes incoming tasks, and sends responses back to the client.

Messages:
- type: "error" - Sent when an error occurs during initialization or task execution
- type: "loaded_agents" - Sent to inform about the loaded agents
- type: "warning" - Sent when there are no loaded agents
- type: "pong" - Sent in response to a ping message
- type: "ping" - Sent to keep the connection alive
- Other message types are handled by the _run_task function

Args:
    websocket (WebSocket): The WebSocket connection object.

Raises:
    WebSocketDisconnect: When the WebSocket connection is closed by the client.

## Messages

