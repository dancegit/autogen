import logging
import os
import traceback
import yaml
from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from autogen_magentic_one.magentic_one_helper import MagenticOneHelper
import modal

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MagenticOneHelper
    magnetic_one = MagenticOneHelper(logs_dir="/tmp/magentic_one_logs")
    await magnetic_one.initialize()
    yield
    # Cleanup code (if any) can go here

def create_app():
    fastapi_app = FastAPI(lifespan=lifespan)
    
    # Initialize MagenticOneHelper
    magnetic_one = MagenticOneHelper(logs_dir="/tmp/magentic_one_logs")
    
    # Mount static files and templates
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    templates_dir = os.path.join(base_dir, "templates")
    logger.debug(f"Base directory: {base_dir}")
    logger.debug(f"Static directory: {static_dir}")
    logger.debug(f"Templates directory: {templates_dir}")
    
    if os.path.exists(static_dir):
        fastapi_app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"Mounted static files from {static_dir}")
    else:
        logger.error(f"Static directory '{static_dir}' does not exist")
    
    # Check if asyncapi-docs directory exists before mounting
    asyncapi_docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asyncapi-docs")
    logger.debug(f"AsyncAPI docs directory: {asyncapi_docs_dir}")
    if os.path.exists(asyncapi_docs_dir):
        fastapi_app.mount("/asyncapi-docs", StaticFiles(directory=asyncapi_docs_dir), name="asyncapi-docs")
        logger.info(f"Mounted AsyncAPI docs from {asyncapi_docs_dir}")
    else:
        logger.warning(f"Directory '{asyncapi_docs_dir}' does not exist. Skipping mount.")
    
    if os.path.exists(templates_dir):
        templates = Jinja2Templates(directory=templates_dir)
        logger.info(f"Loaded templates from {templates_dir}")
    else:
        logger.error(f"Templates directory '{templates_dir}' does not exist")

    @fastapi_app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @fastapi_app.get("/api/health")
    async def health_check():
        return {"status": "ok"}

    @fastapi_app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                if data.get('type') == 'ping':
                    await websocket.send_json({"type": "pong"})
                elif data.get('type') == 'task':
                    result = await magnetic_one.run_task(data.get('content'))
                    await websocket.send_json({"type": "result", "data": result})
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message type",
                        "details": f"Received: {data}"
                    })
        except Exception as e:
            logger.exception("WebSocket error")
            await websocket.send_json({
                "type": "error",
                "message": str(e),
                "details": traceback.format_exc()
            })

    return fastapi_app

    @fastapi_app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @fastapi_app.get("/asyncapi", include_in_schema=False)
    async def get_asyncapi_spec():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, 'asyncapi.yaml'), 'r') as f:
            asyncapi_spec = yaml.safe_load(f)
        return JSONResponse(content=asyncapi_spec)

    return fastapi_app

# Use modal.asgi_app decorator with App instead of Stub
app = modal.App("autogen-magentic-one")

@app.function()
@modal.asgi_app()
def asgi_app():
    return create_app()

if __name__ == "__main__":
    app.run()
