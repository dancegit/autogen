# WebSocket API Documentation

Endpoint: `/ws`

Method: WebSocket

Description: WebSocket endpoint for real-time communication with the MagenticOne application. This endpoint manages the connection lifecycle, processes incoming tasks, and sends responses back to the client.

## Connection

To establish a WebSocket connection, connect to: `ws://<your-domain>/ws`

## Messages

### Incoming Messages (Client to Server)

1. Task Execution
   ```json
   {
     "type": "task",
     "content": "Your task description here"
   }
   ```

2. Ping (to keep connection alive)
   ```json
   {
     "type": "ping"
   }
   ```

### Outgoing Messages (Server to Client)

1. Error
   ```json
   {
     "type": "error",
     "message": "Error description",
     "details": "Optional detailed error information"
   }
   ```

2. Loaded Agents
   ```json
   {
     "type": "loaded_agents",
     "agents": ["Agent1", "Agent2", "Agent3"]
   }
   ```

3. Warning
   ```json
   {
     "type": "warning",
     "message": "Warning message"
   }
   ```

4. Pong (response to ping)
   ```json
   {
     "type": "pong"
   }
   ```

5. Status Update
   ```json
   {
     "type": "status",
     "message": "Current status of the task"
   }
   ```

6. Final Answer
   ```json
   {
     "type": "final_answer",
     "message": "The final result of the task"
   }
   ```

7. Log
   ```json
   {
     "type": "log",
     "data": {
       "agent": "AgentName",
       "message": "Log message",
       "timestamp": "2023-01-01T12:00:00Z"
     }
   }
   ```

8. Agent Called
   ```json
   {
     "type": "agent_called",
     "agent": "AgentName"
   }
   ```

9. Orchestrator Output
   ```json
   {
     "type": "orchestrator_output",
     "message": "Output from the orchestrator"
   }
   ```

10. Agent Output
    ```json
    {
      "type": "agent_output",
      "agent": "AgentName",
      "message": "Output from the agent"
    }
    ```

11. Active Agents Update
    ```json
    {
      "type": "active_agents",
      "agents": ["Agent1", "Agent2"]
    }
    ```

12. Retry Attempt
    ```json
    {
      "type": "retry",
      "attempt": 1,
      "max_retries": 3
    }
    ```

## Error Handling

The server may disconnect the WebSocket connection in case of critical errors. Clients should implement reconnection logic with exponential backoff.

## Rate Limiting

To prevent abuse, implement appropriate rate limiting on the client side. The server may enforce its own rate limits and disconnect clients that exceed these limits.

## Example Usage

1. Connect to the WebSocket endpoint.
2. Send a task:
   ```json
   {
     "type": "task",
     "content": "Analyze the sentiment of the following text: 'I love this product!'"
   }
   ```
3. Listen for incoming messages and handle them according to their types.
4. Send periodic ping messages to keep the connection alive.

## Notes

- All messages are in JSON format.
- The server may send multiple messages of various types during the execution of a single task.
- Clients should be prepared to handle all message types, even if they're not explicitly using all of them.

