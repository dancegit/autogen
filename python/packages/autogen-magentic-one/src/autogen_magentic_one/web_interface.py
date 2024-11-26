import asyncio
import logging
from fastapi import FastAPI, Request, Form, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modal import asgi_app, Function
from modal_deployment import app as modal_app, image, project_mounts
import os
import sys
import json
from autogen_magentic_one.magentic_one_helper import MagenticOneHelper

app = FastAPI()
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

if not os.path.exists(static_dir):
    os.makedirs(static_dir)
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@modal_app.function(image=image)
@asgi_app()
def fastapi_app():
    return app

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@modal_app.function(
    image=image,
    gpu="T4",
    timeout=600,
    memory=1024,
    cpu=1,
    mounts=project_mounts
)
async def _run_task(task: str, websocket: WebSocket):
    logs_dir = "/tmp/magentic_one_logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    magnetic_one = MagenticOneHelper(logs_dir=logs_dir)
    await magnetic_one.initialize()
    await websocket.send_text(json.dumps({"type": "status", "message": "MagenticOne initialized."}))

    task_future = asyncio.create_task(magnetic_one.run_task(task))

    async for log_entry in magnetic_one.stream_logs():
        await websocket.send_text(json.dumps({"type": "log", "data": log_entry}))

    await task_future

    final_answer = magnetic_one.get_final_answer()
    if final_answer is not None:
        await websocket.send_text(json.dumps({"type": "final_answer", "message": final_answer}))
    else:
        await websocket.send_text(json.dumps({"type": "error", "message": "No final answer found in logs."}))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    task = await websocket.receive_text()
    
    try:
        await _run_task.remote(task, websocket)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
