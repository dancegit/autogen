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
    for node in ast.walk(websocket_function):
        if isinstance(node, ast.Dict) and any(key.value == 'type' for key in node.keys):
            try:
                message = ast.literal_eval(node)
                if isinstance(message, dict) and 'type' in message:
                    message_type = message['type']
                    if message_type not in message_types:
                        message_types.add(message_type)
                        api_docs["messages"].append({
                            "type": message_type,
                            "description": f"Message of type '{message_type}'.",
                            "example": message
                        })
                        logger.debug(f"Added message type: {message_type}")
            except Exception as e:
                logger.error(f"Error parsing message: {e}")

    logger.debug(f"Parsed {len(api_docs['messages'])} messages")
    return api_docs

def generate_markdown_docs(api_docs: Dict[str, Any]) -> str:
    markdown = f"# WebSocket API Documentation\n\n"
    markdown += f"Endpoint: `{api_docs['endpoint']}`\n\n"
    markdown += f"Method: {api_docs['method']}\n\n"
    markdown += f"Description: {api_docs['description']}\n\n"
    markdown += "## Messages\n\n"

    markdown += "### Incoming Messages (Client to Server)\n\n"
    markdown += "1. Task Execution\n   ```json\n   {\n     \"type\": \"task\",\n     \"content\": \"Your task description here\"\n   }\n   ```\n\n"
    markdown += "2. Ping (to keep connection alive)\n   ```json\n   {\n     \"type\": \"ping\"\n   }\n   ```\n\n"

    markdown += "### Outgoing Messages (Server to Client)\n\n"
    for i, message in enumerate(api_docs['messages'], 1):
        markdown += f"{i}. {message['type']}\n   ```json\n"
        markdown += json.dumps(message['example'], indent=3)
        markdown += "\n   ```\n\n"

    markdown += "## Error Handling\n\n"
    markdown += "The server may disconnect the WebSocket connection in case of critical errors. Clients should implement reconnection logic with exponential backoff.\n\n"

    markdown += "## Rate Limiting\n\n"
    markdown += "To prevent abuse, implement appropriate rate limiting on the client side. The server may enforce its own rate limits and disconnect clients that exceed these limits.\n\n"

    markdown += "## Example Usage\n\n"
    markdown += "1. Connect to the WebSocket endpoint.\n"
    markdown += "2. Send a task:\n   ```json\n   {\n     \"type\": \"task\",\n     \"content\": \"Analyze the sentiment of the following text: 'I love this product!'\"\n   }\n   ```\n"
    markdown += "3. Listen for incoming messages and handle them according to their types.\n"
    markdown += "4. Send periodic ping messages to keep the connection alive.\n\n"

    markdown += "## Notes\n\n"
    markdown += "- All messages are in JSON format.\n"
    markdown += "- The server may send multiple messages of various types during the execution of a single task.\n"
    markdown += "- Clients should be prepared to handle all message types, even if they're not explicitly using all of them.\n"

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
