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
- type: "status" - Sent to update the client on the current status of the task
- type: "final_answer" - Sent when the task is completed with a final answer
- type: "log" - Sent to provide detailed logs of the task execution
- type: "agent_called" - Sent when a specific agent is called during task execution
- type: "orchestrator_output" - Sent to provide output from the orchestrator
- type: "agent_output" - Sent to provide output from individual agents
- type: "active_agents" - Sent to update the list of currently active agents
- type: "retry" - Sent when a task execution is being retried

Args:
    websocket (WebSocket): The WebSocket connection object.

Raises:
    WebSocketDisconnect: When the WebSocket connection is closed by the client.

## Messages

Message types:

