import ast
import inspect
import json
from pathlib import Path

def parse_websocket_endpoint(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    websocket_function = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'websocket_endpoint':
            websocket_function = node
            break

    if not websocket_function:
        return None

    api_docs = {
        "endpoint": "/ws",
        "method": "WebSocket",
        "description": ast.get_docstring(websocket_function) or "WebSocket endpoint for real-time communication.",
        "messages": []
    }

    for node in ast.walk(websocket_function):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'send_text':
            if len(node.args) > 0 and isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name) and node.args[0].func.id == 'json':
                message = ast.literal_eval(node.args[0].args[0])
                if isinstance(message, dict) and 'type' in message:
                    api_docs["messages"].append({
                        "type": message['type'],
                        "description": f"Message of type '{message['type']}'.",
                        "example": message
                    })

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
    
    api_docs = parse_websocket_endpoint(web_interface_path)
    
    if api_docs:
        markdown_docs = generate_markdown_docs(api_docs)
        output_path = current_dir / "ws_api_docs.md"
        
        with open(output_path, 'w') as f:
            f.write(markdown_docs)
        
        print(f"WebSocket API documentation generated: {output_path}")
    else:
        print("Failed to generate WebSocket API documentation.")

if __name__ == "__main__":
    main()
