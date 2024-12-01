import logging
import os
import traceback
from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from asyncapi import AsyncAPI
from autogen_magentic_one.magentic_one_helper import MagenticOneHelper
import modal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    fastapi_app = FastAPI()
    
    # Initialize MagenticOneHelper
    magnetic_one = MagenticOneHelper(logs_dir="/tmp/magentic_one_logs")

    # Load AsyncAPI specification
    base_dir = os.path.dirname(os.path.abspath(__file__))
    async_api = AsyncAPI.from_yaml(os.path.join(base_dir, 'asyncapi.yaml'))

    # Mount static files and templates
    static_dir = os.path.join(base_dir, "static")
    templates_dir = os.path.join(base_dir, "templates")
    fastapi_app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=templates_dir)

    @fastapi_app.on_event("startup")
    async def startup_event():
        await magnetic_one.initialize()

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
                    await websocket.send_json(async_api.get_message('Pong').payload)
                elif data.get('type') == 'task':
                    result = await magnetic_one.run_task(data.get('content'))
                    await websocket.send_json(async_api.get_message('Result').payload(data=result))
                else:
                    await websocket.send_json(async_api.get_message('Error').payload(
                        message="Invalid message type",
                        details=f"Received: {data}"
                    ))
        except Exception as e:
            logger.exception("WebSocket error")
            await websocket.send_json(async_api.get_message('Error').payload(
                message=str(e),
                details=traceback.format_exc()
            ))

    @fastapi_app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @fastapi_app.get("/asyncapi", include_in_schema=False)
    async def get_asyncapi_spec():
        return async_api.to_dict()

    return fastapi_app

# Use modal.asgi_app decorator with App instead of Stub
app = modal.App("autogen-magentic-one")

@app.function()
@modal.asgi_app()
def asgi_app():
    return create_app()

if __name__ == "__main__":
    app.run()
