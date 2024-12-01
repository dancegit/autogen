import modal
import os
import pathlib
import sys
import subprocess
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory of this file
current_dir = pathlib.Path(__file__).parent.resolve()

logger.info(f"Current directory: {current_dir}")
logger.info("Contents of current directory:")
for item in current_dir.iterdir():
    logger.info(f"  {item}")

# Add the necessary paths to the Python path
autogen_path = current_dir.parent  # Go up one level to reach the autogen root
packages_path = current_dir / "packages"
autogen_magentic_one_path = packages_path / "autogen-magentic-one"

# Define the base image
base_image = (modal.Image
    .debian_slim()
    .apt_install(["wget", "gnupg", "ffmpeg"])
    .run_commands(
        "wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list",
        "apt-get update",
        "apt-get install -y google-chrome-stable"
    ))

app = modal.App("autogen-magentic-one")

# Create a single mount for the autogen folder
autogen_mount = modal.Mount.from_local_dir(
    current_dir.parent,
    remote_path="/root/autogen",
    condition=lambda path: not any(excluded in path for excluded in [".github", "dotnet", "venv", ".venv", r"\.aider.*", r"docs(?!/blob/modalComDocs)"])
)

# Combine all mounts
project_mounts = [autogen_mount]

# Use the base_image and extend it with our specific requirements
image = (
    base_image
    .copy_mount(autogen_mount, remote_path="/")
    .workdir("/root/autogen/python")
    .run_commands(
        "python3 -m venv .venv",
        "touch /root/.bashrc",
        "echo 'export PATH=/root/autogen/python/.venv/bin:$PATH' >> /root/.bashrc",
        "echo 'alias python=/root/autogen/python/.venv/bin/python' >> /root/.bashrc",
        "echo 'alias pip=/root/autogen/python/.venv/bin/pip' >> /root/.bashrc",
        ". /root/.bashrc",
        "/root/autogen/python/.venv/bin/pip install --upgrade pip",
        "/root/autogen/python/.venv/bin/pip install uv",
        "ls -la /root/autogen/python/packages",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-core",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-ext",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-magentic-one",
        "/root/autogen/python/.venv/bin/pip install -r /root/autogen/python/packages/autogen-magentic-one/requirements.txt",
        "/root/autogen/python/.venv/bin/pip install grpclib PyGithub",
        "/root/autogen/python/.venv/bin/pip install /root/autogen/python/packages/autogen-agentchat",
        "/root/autogen/python/.venv/bin/pip install /root/autogen/python/packages/agbench",
        "/root/autogen/python/.venv/bin/pip install /root/autogen/python/packages/autogen-studio",
        "/root/autogen/python/.venv/bin/pip install tenacity",
        "/root/autogen/python/.venv/bin/pip install playwright",
        r"/root/autogen/python/.venv/bin/playwright install --with-deps chromium",
        r"/root/autogen/python/.venv/bin/playwright install-deps",
        r"/root/autogen/python/.venv/bin/playwright install chromium",
        r"/root/autogen/python/.venv/bin/python -m playwright install",
        r"/root/autogen/python/.venv/bin/python -m playwright install-deps",
        r"/root/autogen/python/.venv/bin/python -m playwright install chromium"
    )
    .workdir("/root")
    .env({
        "BING_API_KEY": os.environ.get("BING_API_KEY", ""),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "CHAT_COMPLETION_KWARGS_JSON": '{"model": "gpt-4"}',
        "PATH": "/root/autogen/python/.venv/bin:${PATH}"
    })
)

logger.info("Environment variables:")
logger.info(f"BING_API_KEY: {'Set' if os.environ.get('BING_API_KEY') else 'Not set'}")
logger.info(f"OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
logger.info(f"CHAT_COMPLETION_KWARGS_JSON: {os.environ.get('CHAT_COMPLETION_KWARGS_JSON', 'Not set')}")

@app.function(
    image=image,
    gpu="T4",
    timeout=600,
    memory=1024,
    cpu=1,
    mounts=project_mounts
)
def run_magentic_one(task: str):
    from autogen_magentic_one import MagenticOneHelper
    helper = MagenticOneHelper(logs_dir="/tmp/magentic_one_logs")
    result = helper.run(task)
    return result

import yaml
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

@app.function(image=image, mounts=project_mounts, keep_warm=1)
@modal.asgi_app()
def modal_fastapi_app():
    try:
        import autogen_magentic_one
        logger.info(f"autogen_magentic_one path: {autogen_magentic_one.__file__}")
        from autogen_magentic_one.web_interface import create_app
        
        fastapi_app = create_app()
        templates = Jinja2Templates(directory=os.path.join(os.path.dirname(autogen_magentic_one.__file__), "templates"))

        @fastapi_app.get("/asyncapi", include_in_schema=False)
        async def get_asyncapi_spec():
            asyncapi_path = os.path.join(os.path.dirname(autogen_magentic_one.__file__), "asyncapi.yaml")
            with open(asyncapi_path, "r") as f:
                asyncapi_spec = yaml.safe_load(f)
            return JSONResponse(content=asyncapi_spec)

        @fastapi_app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html(request: Request):
            return templates.TemplateResponse(
                "swagger-ui.html",
                {"request": request, "asyncapi_url": "/asyncapi"}
            )

        return fastapi_app
    except ImportError as e:
        logger.error(f"Error importing app: {e}")
        logger.error("Detailed sys.path:")
        for i, path in enumerate(sys.path):
            logger.error(f"  {i}: {path}")
            if os.path.exists(path):
                logger.error(f"    Contents: {os.listdir(path)}")
            else:
                logger.error("    Path does not exist")

        autogen_magentic_one_dir = os.path.join(current_dir, "packages", "autogen-magentic-one")
        if os.path.exists(autogen_magentic_one_dir):
            logger.info(f"autogen_magentic_one directory exists: {autogen_magentic_one_dir}")
            logger.info("Contents:")
            for item in os.listdir(autogen_magentic_one_dir):
                logger.info(f"  {item}")

            logger.info("Attempting to install autogen_magentic_one package...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", autogen_magentic_one_dir])
            logger.info("autogen_magentic_one package installed successfully.")

            import autogen_magentic_one
            from autogen_magentic_one.web_interface import create_app
            
            return create_app()
        else:
            logger.error(f"autogen_magentic_one directory does not exist: {autogen_magentic_one_dir}")

        raise ImportError("Failed to import autogen_magentic_one after attempted installation")

@app.local_entrypoint()
def main(task: str):
    result = run_magentic_one.remote(task)
    logger.info(result)
    logger.info(f"WebSocket URL: {modal_fastapi_app.web_url}/ws")
    logger.info(f"WebSocket API Documentation: {modal_fastapi_app.web_url}/ws-api-docs")

if __name__ == "__main__":
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info("Contents of current directory:")
    for item in os.listdir():
        logger.info(f"  {item}")
    logger.info("To deploy this app, run the following command:")
    logger.info(f"modal deploy {__file__}")

    try:
        import autogen_magentic_one
        logger.info(f"autogen_magentic_one is installed at: {autogen_magentic_one.__file__}")
        logger.info(f"autogen_magentic_one version: {autogen_magentic_one.__version__}")
    except ImportError as e:
        logger.warning(f"Warning: autogen_magentic_one is not installed. Error: {e}")
    except AttributeError:
        logger.warning("Warning: autogen_magentic_one is installed but __version__ is not available")
