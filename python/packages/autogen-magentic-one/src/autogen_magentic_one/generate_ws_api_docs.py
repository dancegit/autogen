import ast
import inspect
import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_websocket_endpoint(file_path: Path) -> Dict[str, Any]:
    logger.debug(f"Parsing file: {file_path}")
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            logger.debug(f"File content length: {len(content)}")
            tree = ast.parse(content)
    except Exception as e:
        logger.error(f"Error reading or parsing file: {e}")
        return None

    websocket_function = next((node for node in ast.walk(tree) 
                               if isinstance(node, ast.AsyncFunctionDef) and node.name == 'websocket_endpoint'), None)

    if not websocket_function:
        logger.warning("websocket_endpoint function not found")
        return None

    api_docs = {
        "endpoint": "/ws",
        "method": "WebSocket",
        "description": ast.get_docstring(websocket_function) or "WebSocket endpoint for real-time communication.",
        "messages": []
    }

    logger.debug("Parsing websocket_endpoint function")
    message_types = set()
    
    def extract_message_types(node):
        if isinstance(node, ast.Dict) and any(isinstance(key, ast.Constant) and key.value == 'type' for key in node.keys):
            try:
                message_type = next((value.value for key, value in zip(node.keys, node.values) 
                                     if isinstance(key, ast.Constant) and key.value == 'type' 
                                     and isinstance(value, ast.Constant)), None)
                if message_type and message_type not in message_types:
                    message_types.add(message_type)
                    api_docs["messages"].append({
                        "type": message_type,
                        "description": f"Message of type '{message_type}'.",
                        "example": {"type": message_type}
                    })
                    logger.debug(f"Added message type: {message_type}")
            except Exception as e:
                logger.error(f"Error parsing message: {e}")
        elif isinstance(node, ast.Str):
            # Check for message types in string literals
            potential_types = ['error', 'loaded_agents', 'warning', 'pong', 'ping', 'status', 'final_answer', 'log', 'agent_called', 'orchestrator_output', 'agent_output', 'active_agents', 'retry', 'agents_loaded']
            for msg_type in potential_types:
                if msg_type in node.s and msg_type not in message_types:
                    message_types.add(msg_type)
                    api_docs["messages"].append({
                        "type": msg_type,
                        "description": f"Message of type '{msg_type}'.",
                        "example": {"type": msg_type}
                    })
                    logger.debug(f"Added message type from string: {msg_type}")

    for node in ast.walk(websocket_function):
        extract_message_types(node)

    logger.debug(f"Parsed {len(api_docs['messages'])} messages")
    return api_docs

def generate_example_messages(api_docs: Dict[str, Any]) -> Dict[str, Any]:
    example_messages = {
        'error': {
            "type": "error",
            "message": "An error occurred during task execution",
            "details": "Traceback: ..."
        },
        'loaded_agents': {
            "type": "loaded_agents",
            "agents": ["Agent1", "Agent2", "Agent3"]
        },
        'warning': {
            "type": "warning",
            "message": "Warning: Task execution may be slow due to high load"
        },
        'pong': {
            "type": "pong"
        },
        'ping': {
            "type": "ping"
        },
        'status': {
            "type": "status",
            "message": "Task execution 50% complete"
        },
        'final_answer': {
            "type": "final_answer",
            "message": "The sentiment of the text is positive."
        },
        'log': {
            "type": "log",
            "data": {
                "agent": "Agent1",
                "message": "Processing input data..."
            }
        },
        'agent_called': {
            "type": "agent_called",
            "agent": "Agent2"
        },
        'orchestrator_output': {
            "type": "orchestrator_output",
            "message": "Orchestrator: Delegating task to Agent3"
        },
        'agent_output': {
            "type": "agent_output",
            "agent": "Agent3",
            "message": "Agent3: Task completed successfully"
        },
        'active_agents': {
            "type": "active_agents",
            "agents": ["Agent1", "Agent3"]
        },
        'retry': {
            "type": "retry",
            "attempt": 2,
            "max_retries": 3
        },
        'agents_loaded': {
            "type": "agents_loaded",
            "agents": ["Agent1", "Agent2", "Agent3"]
        }
    }

    for message in api_docs['messages']:
        message_type = message['type']
        if message_type in example_messages:
            message['example'] = example_messages[message_type]
        else:
            # Generate a generic example for unknown message types
            message['example'] = {
                "type": message_type,
                "message": f"Example message for {message_type}",
                "data": {"key": "value"}
            }

    return api_docs

def generate_markdown_docs(api_docs: Dict[str, Any]) -> str:
    markdown = f"# WebSocket API Documentation\n\n"
    markdown += f"Endpoint: `{api_docs['endpoint']}`\n\n"
    markdown += f"Method: {api_docs['method']}\n\n"
    markdown += f"Description: {api_docs['description']}\n\n"
    markdown += "## Messages\n\n"

    markdown += "### Incoming Messages (Client to Server)\n\n"
    markdown += "1. Task Execution\n   ```json\n   {\n     \"type\": \"task\",\n     \"content\": \"Your task description here\"\n   }\n   ```\n   Description: Send a task to be executed by the server.\n\n"
    markdown += "2. Ping (to keep connection alive)\n   ```json\n   {\n     \"type\": \"ping\"\n   }\n   ```\n   Description: Keep the WebSocket connection alive.\n\n"

    markdown += "### Outgoing Messages (Server to Client)\n\n"
    for i, message in enumerate(api_docs['messages'], 1):
        markdown += f"{i}. {message['type']}\n   ```json\n"
        markdown += json.dumps(message['example'], indent=3)
        markdown += "\n   ```\n"
        markdown += f"   Description: {message['description']}\n\n"

    markdown += "## Connection Lifecycle\n\n"
    markdown += "1. Client establishes a WebSocket connection to the server.\n"
    markdown += "2. Client sends a task message to initiate processing.\n"
    markdown += "3. Server processes the task and sends various message types as updates.\n"
    markdown += "4. Client sends periodic ping messages to keep the connection alive.\n"
    markdown += "5. Server sends a final_answer message when the task is complete.\n"
    markdown += "6. Client can send a new task or close the connection.\n\n"

    markdown += "## Error Handling\n\n"
    markdown += "- The server may send error messages with details about any issues encountered.\n"
    markdown += "- The server may disconnect the WebSocket connection in case of critical errors.\n"
    markdown += "- Clients should implement reconnection logic with exponential backoff.\n\n"

    markdown += "## Rate Limiting\n\n"
    markdown += "- To prevent abuse, implement appropriate rate limiting on the client side.\n"
    markdown += "- The server may enforce its own rate limits and disconnect clients that exceed these limits.\n\n"

    markdown += "## Example Usage\n\n"
    markdown += "1. Connect to the WebSocket endpoint.\n"
    markdown += "2. Send a task:\n   ```json\n   {\n     \"type\": \"task\",\n     \"content\": \"Analyze the sentiment of the following text: 'I love this product!'\"\n   }\n   ```\n"
    markdown += "3. Listen for incoming messages and handle them according to their types:\n"
    markdown += "   - Update UI with status messages\n"
    markdown += "   - Display agent outputs and logs\n"
    markdown += "   - Handle and display the final answer\n"
    markdown += "4. Send periodic ping messages to keep the connection alive.\n"
    markdown += "5. Handle any error messages and implement appropriate error recovery.\n\n"

    markdown += "## Notes\n\n"
    markdown += "- All messages are in JSON format.\n"
    markdown += "- The server may send multiple messages of various types during the execution of a single task.\n"
    markdown += "- Clients should be prepared to handle all message types, even if they're not explicitly using all of them.\n"
    markdown += "- Consider implementing a timeout mechanism on the client side for long-running tasks.\n"

    return markdown

def main() -> bool:
    current_dir = Path(__file__).parent
    web_interface_path = current_dir / "web_interface.py"
    
    logger.info(f"Starting WebSocket API documentation generation")
    logger.debug(f"Current directory: {current_dir}")
    logger.debug(f"Web interface path: {web_interface_path}")
    
    try:
        if not web_interface_path.exists():
            logger.error(f"Web interface file not found: {web_interface_path}")
            return False

        api_docs = parse_websocket_endpoint(web_interface_path)
        
        if api_docs:
            api_docs = generate_example_messages(api_docs)
            markdown_docs = generate_markdown_docs(api_docs)
            output_path = current_dir / "ws_api_docs.md"
            
            with open(output_path, 'w') as f:
                f.write(markdown_docs)
            
            logger.info(f"WebSocket API documentation generated: {output_path}")
            return True
        else:
            logger.error("Failed to generate WebSocket API documentation: No API docs parsed.")
            return False
    except Exception as e:
        logger.exception(f"Error generating WebSocket API documentation: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    logger.info(f"Exiting with code {exit_code}")
    sys.exit(exit_code)
