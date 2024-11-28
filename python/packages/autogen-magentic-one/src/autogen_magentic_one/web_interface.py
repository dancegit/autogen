import asyncio
import logging
import modal
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modal import asgi_app, Function
from modal_deployment import app as modal_app, image, project_mounts
import os
import sys
import json
import traceback
from autogen_magentic_one.magentic_one_helper import MagenticOneHelper
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Disable hpack debug logging
logging.getLogger('hpack').setLevel(logging.WARNING)

app = FastAPI()
logger.info("FastAPI app initialized")

# Get the path to the autogen_magentic_one directory
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")

if not os.path.exists(static_dir):
    print(f"Warning: static directory not found at {static_dir}")
if not os.path.exists(templates_dir):
    print(f"Warning: templates directory not found at {templates_dir}")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Log the path of the main.js file
main_js_path = os.path.join(static_dir, "main.js")
logger.info(f"main.js path: {main_js_path}")
if os.path.exists(main_js_path):
    logger.info(f"main.js file exists at {main_js_path}")
    with open(main_js_path, 'r') as f:
        logger.info(f"First 100 characters of main.js: {f.read(100)}")
else:
    logger.warning(f"main.js file not found at {main_js_path}")

# Ensure static files are included in the deployment
static_mount = modal.Mount.from_local_dir(
    static_dir,
    remote_path="/root/autogen/python/packages/autogen-magentic-one/src/autogen_magentic_one/static"
)
project_mounts.append(static_mount)

# Log the contents of the static directory
print("Contents of static directory:")
for item in os.listdir(static_dir):
    print(f"  {item}")

# Print the actual paths for debugging
print(f"Static directory: {static_dir}")
print(f"Templates directory: {templates_dir}")

# Ensure the package data is included
import autogen_magentic_one

@modal_app.function(
    image=image,
    gpu="T4",
    timeout=600,
    memory=1024,
    cpu=1,
    mounts=project_mounts
)
@asgi_app()
def fastapi_app():
    return app

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def _run_task(task: str, websocket: WebSocket):
    logs_dir = "/tmp/magentic_one_logs"
    os.makedirs(logs_dir, exist_ok=True)

    logger.info(f"Starting task: {task}")
    try:
        magnetic_one = app.state.magnetic_one
        loaded_agents = magnetic_one.get_loaded_agents()
        await websocket.send_text(json.dumps({"type": "agents_loaded", "agents": loaded_agents}))
        await websocket.send_text(json.dumps({"type": "status", "message": "MagenticOne initialized."}))
        logger.info("Using pre-initialized MagenticOne")

        task_future = asyncio.create_task(magnetic_one.run_task(task))

        async for log_entry in magnetic_one.stream_logs():
            logger.debug(f"Log entry: {log_entry}")
            try:
                await websocket.send_text(json.dumps({"type": "log", "data": log_entry}))
                if log_entry.get('event') == 'agent_called':
                    await websocket.send_text(json.dumps({"type": "agent_called", "agent": log_entry.get('agent')}))
            except Exception as e:
                logger.error(f"Error sending log entry: {str(e)}")

        await task_future

        final_answer = magnetic_one.get_final_answer()
        if final_answer is not None:
            logger.info(f"Final answer: {final_answer}")
            await websocket.send_text(json.dumps({"type": "final_answer", "message": final_answer}))
        else:
            logger.warning("No final answer found in logs")
            await websocket.send_text(json.dumps({"type": "error", "message": "No final answer found in logs."}))
    except asyncio.CancelledError:
        logger.info("Task was cancelled")
        await websocket.send_text(json.dumps({"type": "error", "message": "Task was cancelled."}))
    except openai.RateLimitError as e:
        logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "OpenAI API rate limit exceeded. Please try again later.",
            "details": str(e)
        }))
    except Exception as e:
        logger.error(f"Error in _run_task: {str(e)}", exc_info=True)
        error_details = traceback.format_exc()
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"An error occurred in _run_task: {str(e)}",
            "details": error_details
        }))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    logger.info(f"WebSocket connection details: {websocket.client}")

    try:
        task = await websocket.receive_text()
        logger.info(f"Received task: {task}")

        try:
            logger.debug("Calling _run_task")
            await _run_task(task, websocket)
            logger.debug("_run_task completed")
        except Exception as e:
            logger.error(f"An error occurred in _run_task: {e}", exc_info=True)
            error_details = traceback.format_exc()
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"An error occurred in _run_task: {str(e)}",
                "details": error_details
            }))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"An unexpected error occurred in websocket_endpoint: {e}", exc_info=True)
        error_details = traceback.format_exc()
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"An unexpected error occurred: {str(e)}",
            "details": error_details
        }))
    finally:
        logger.info("Closing WebSocket connection")
        await websocket.close()

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: Initializing MagenticOne")
    try:
        magnetic_one = MagenticOneHelper(logs_dir="/tmp/magentic_one_logs")
        await magnetic_one.initialize()
        logger.info("MagenticOne initialized successfully")
        app.state.magnetic_one = magnetic_one
    except Exception as e:
        logger.error(f"Failed to initialize MagenticOne: {e}", exc_info=True)
        raise

logger.info("WebSocket endpoint registered")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
