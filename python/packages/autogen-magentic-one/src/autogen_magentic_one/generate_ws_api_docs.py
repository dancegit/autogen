import ast
import inspect
import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_websocket_endpoint(file_path):
    logger.debug(f"Parsing file: {file_path}")
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            logger.debug(f"File content length: {len(content)}")
            tree = ast.parse(content)
    except Exception as e:
        logger.error(f"Error reading or parsing file: {e}")
        return None

    websocket_function = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'websocket_endpoint':
            websocket_function = node
            logger.debug("Found websocket_endpoint function")
            break

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
    for node in ast.walk(websocket_function):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'send_text':
            logger.debug("Found send_text call")
            if len(node.args) > 0 and isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name) and node.args[0].func.id == 'json':
                try:
                    message = ast.literal_eval(node.args[0].args[0])
                    if isinstance(message, dict) and 'type' in message:
                        api_docs["messages"].append({
                            "type": message['type'],
                            "description": f"Message of type '{message['type']}'.",
                            "example": message
                        })
                        logger.debug(f"Added message type: {message['type']}")
                except Exception as e:
                    logger.error(f"Error parsing message: {e}")

    logger.debug(f"Parsed {len(api_docs['messages'])} messages")
    return api_docs

def generate_markdown_docs(api_docs):
    markdown = f"# WebSocket API Documentation\n\n"
    markdown += f"Endpoint: `{api_docs['endpoint']}`\n\n"
    markdown += f"Method: {api_docs['method']}\n\n"
    markdown += f"Description: {api_docs['description']}\n\n"
    markdown += "## Messages\n\n"

    for message in api_docs['messages']:
        markdown += f"### {message['type']}\n\n"
        markdown += f"Description: {message['description']}\n\n"
        markdown += "Example:\n```json\n"
        markdown += json.dumps(message['example'], indent=2)
        markdown += "\n```\n\n"

    return markdown

def main():
    current_dir = Path(__file__).parent
    web_interface_path = current_dir / "web_interface.py"
    
    logger.info(f"Starting WebSocket API documentation generation")
    logger.debug(f"Current directory: {current_dir}")
    logger.debug(f"Web interface path: {web_interface_path}")
    
    try:
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
