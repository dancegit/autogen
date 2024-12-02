# WebSocket API Documentation

Endpoint: `/ws`

Method: WebSocket

Description: WebSocket endpoint for real-time communication.

## Messages

### Incoming Messages (Client to Server)

1. Task Execution
   ```json
   {
     "type": "task",
     "content": "Your task description here"
   }
   ```
   Description: Send a task to be executed by the server.

2. Ping (to keep connection alive)
   ```json
   {
     "type": "ping"
   }
   ```
   Description: Keep the WebSocket connection alive.

### Outgoing Messages (Server to Client)

1. ping
   ```json
{
   "type": "ping"
}
   ```
   Description: Message of type 'ping'.

2. error
   ```json
{
   "type": "error",
   "message": "An error occurred during task execution",
   "details": "Traceback: ..."
}
   ```
   Description: Message of type 'error'.

3. pong
   ```json
{
   "type": "pong"
}
   ```
   Description: type

4. result
   ```json
{
   "type": "result",
   "message": "Example message for result",
   "data": {
      "key": "value"
   }
}
   ```
   Description: type

## Connection Lifecycle

1. Client establishes a WebSocket connection to the server.
2. Client sends a task message to initiate processing.
3. Server processes the task and sends various message types as updates.
4. Client sends periodic ping messages to keep the connection alive.
5. Server sends a final_answer message when the task is complete.
6. Client can send a new task or close the connection.

## Error Handling

- The server may send error messages with details about any issues encountered.
- The server may disconnect the WebSocket connection in case of critical errors.
- Clients should implement reconnection logic with exponential backoff.

## Rate Limiting

- To prevent abuse, implement appropriate rate limiting on the client side.
- The server may enforce its own rate limits and disconnect clients that exceed these limits.

## Example Usage

1. Connect to the WebSocket endpoint.
2. Send a task:
   ```json
   {
     "type": "task",
     "content": "Analyze the sentiment of the following text: 'I love this product!'"
   }
   ```
3. Listen for incoming messages and handle them according to their types:
   - Update UI with status messages
   - Display agent outputs and logs
   - Handle and display the final answer
4. Send periodic ping messages to keep the connection alive.
5. Handle any error messages and implement appropriate error recovery.

## Notes

- All messages are in JSON format.
- The server may send multiple messages of various types during the execution of a single task.
- Clients should be prepared to handle all message types, even if they're not explicitly using all of them.
- Consider implementing a timeout mechanism on the client side for long-running tasks.
