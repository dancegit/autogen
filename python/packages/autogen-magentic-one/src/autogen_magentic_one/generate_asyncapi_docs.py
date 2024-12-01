import yaml
from pathlib import Path
import subprocess

def generate_asyncapi_docs():
    asyncapi_spec = {
        "asyncapi": "2.5.0",
        "info": {
            "title": "AutoGen Magentic-One WebSocket API",
            "version": "1.0.0",
            "description": "WebSocket API for real-time communication with AutoGen Magentic-One"
        },
        "servers": {
            "production": {
                "url": "wss://your-modal-app-url.modal.run/ws",
                "protocol": "wss"
            }
        },
        "channels": {
            "/": {
                "publish": {
                    "message": {
                        "oneOf": [
                            {"$ref": "#/components/messages/TaskExecution"},
                            {"$ref": "#/components/messages/Ping"}
                        ]
                    }
                },
                "subscribe": {
                    "message": {
                        "oneOf": [
                            {"$ref": "#/components/messages/Result"},
                            {"$ref": "#/components/messages/Error"},
                            {"$ref": "#/components/messages/Status"},
                            {"$ref": "#/components/messages/AgentsLoaded"},
                            {"$ref": "#/components/messages/Pong"},
                            {"$ref": "#/components/messages/Warning"},
                            {"$ref": "#/components/messages/Retry"}
                        ]
                    }
                }
            }
        },
        "components": {
            "messages": {
                "TaskExecution": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["task"]},
                            "content": {"type": "string"}
                        },
                        "required": ["type", "content"]
                    }
                },
                "Ping": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["ping"]}
                        },
                        "required": ["type"]
                    }
                },
                "Result": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["result"]},
                            "data": {"type": "object"}
                        },
                        "required": ["type", "data"]
                    }
                },
                "Error": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["error"]},
                            "message": {"type": "string"},
                            "details": {"type": "string"}
                        },
                        "required": ["type", "message"]
                    }
                },
                "Status": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["status"]},
                            "message": {"type": "string"}
                        },
                        "required": ["type", "message"]
                    }
                },
                "AgentsLoaded": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["agents_loaded"]},
                            "agents": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["type", "agents"]
                    }
                },
                "Pong": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["pong"]}
                        },
                        "required": ["type"]
                    }
                },
                "Warning": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["warning"]},
                            "message": {"type": "string"}
                        },
                        "required": ["type", "message"]
                    }
                },
                "Retry": {
                    "payload": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["retry"]},
                            "attempt": {"type": "integer"},
                            "max_retries": {"type": "integer"}
                        },
                        "required": ["type", "attempt", "max_retries"]
                    }
                }
            }
        }
    }

    current_dir = Path(__file__).parent
    output_path = current_dir / "asyncapi.yaml"

    with open(output_path, 'w') as f:
        yaml.dump(asyncapi_spec, f, sort_keys=False)

    print(f"AsyncAPI specification generated: {output_path}")

import shutil

def is_asyncapi_cli_installed():
    return shutil.which("asyncapi") is not None

def generate_asyncapi_documentation(yaml_path):
    if not is_asyncapi_cli_installed():
        print("AsyncAPI CLI is not installed. Please install it using:")
        print("npm install -g @asyncapi/cli")
        print("Then run this script again.")
        return

    # Ensure the asyncapi-docs directory exists
    os.makedirs("./asyncapi-docs", exist_ok=True)

    html_cmd = f"asyncapi generate html {yaml_path} -o ./asyncapi-docs"
    md_cmd = f"asyncapi generate markdown {yaml_path} -o ./asyncapi-docs/asyncapi.md"
    
    try:
        subprocess.run(html_cmd, shell=True, check=True)
        subprocess.run(md_cmd, shell=True, check=True)
        print("AsyncAPI documentation generated in ./asyncapi-docs")
    except subprocess.CalledProcessError as e:
        print(f"Error generating AsyncAPI documentation: {e}")
        print("Please make sure AsyncAPI CLI is correctly installed and accessible.")

if __name__ == "__main__":
    generate_asyncapi_docs()
    generate_asyncapi_documentation("asyncapi.yaml")
