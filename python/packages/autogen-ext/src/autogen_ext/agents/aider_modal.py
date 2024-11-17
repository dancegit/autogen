import modal
from typing import List, Dict, Any
from fastapi import FastAPI

app = modal.App("aider-agent")

def create_aider_image():
    return (
        modal.Image.debian_slim()
        .pip_install("aider-chat", "modal", "fastapi")
        .run_commands("mkdir -p /root/workspace")
    )

aider_image = create_aider_image()

@app.function(
    image=aider_image,
    secrets=[modal.Secret.from_name("aider-secrets")],
    mounts=[modal.Mount.from_local_dir(".", remote_path="/root/workspace")]
)
def run_aider(message: str, config: dict) -> str:
    import os
    import subprocess
    
    os.chdir("/root/workspace")
    
    cmd = [
        "aider",
        "--model", config.get("model_name", "gpt-4"),
        "--no-git",
        "--input-history-file", "/dev/null",
        "--chat-history-file", "/dev/null",
        "--message", message
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

@app.function(
    image=aider_image,
    secrets=[modal.Secret.from_name("aider-secrets")],
    mounts=[modal.Mount.from_local_dir(".", remote_path="/root/workspace")]
)
def list_files() -> List[str]:
    import os
    return os.listdir("/root/workspace")

@app.function(
    image=aider_image,
    secrets=[modal.Secret.from_name("aider-secrets")],
    mounts=[modal.Mount.from_local_dir(".", remote_path="/root/workspace")]
)
def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

@app.function(
    image=aider_image,
    secrets=[modal.Secret.from_name("aider-secrets")],
    mounts=[modal.Mount.from_local_dir(".", remote_path="/root/workspace")]
)
def write_file(file_path: str, content: str) -> bool:
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except Exception:
        return False

@app.function()
@modal.asgi_app()
def fastapi_app():
    app = FastAPI()

    @app.post("/aider_chat")
    async def aider_chat(message: str, config: Dict[str, Any]) -> Dict[str, str]:
        result = run_aider.remote(message, config)
        return {"response": result}

    @app.get("/get_files")
    async def get_files() -> Dict[str, List[str]]:
        files = list_files.remote()
        return {"files": files}

    @app.get("/get_file_content")
    async def get_file_content(file_path: str) -> Dict[str, str]:
        content = read_file.remote(file_path)
        return {"content": content}

    @app.post("/update_file")
    async def update_file(file_path: str, content: str) -> Dict[str, bool]:
        success = write_file.remote(file_path, content)
        return {"success": success}

    return app

if __name__ == "__main__":
    app.serve()
