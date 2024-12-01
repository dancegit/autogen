import asyncio
import logging
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import os
import sys
import json
import traceback
from autogen_magentic_one.magentic_one_helper import MagenticOneHelper
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Disable hpack debug logging
logging.getLogger('hpack').setLevel(logging.WARNING)

class WebSocketMessage(BaseModel):
    type: str
    data: dict

def create_app():
    app = FastAPI()
    logger.info("FastAPI app initialized")

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="MagenticOne WebSocket API",
            version="1.0.0",
            description="WebSocket API for MagenticOne",
            routes=app.routes,
        )
        
        openapi_schema["paths"]["/ws"] = {
            "get": {
                "summary": "WebSocket Endpoint",
                "description": "Establishes a WebSocket connection for real-time communication with MagenticOne",
                "responses": {
                    "101": {
                        "description": "WebSocket connection established",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/WebSocketMessage"}
                            }
                        }
                    }
                }
            }
        }
        
        openapi_schema["components"]["schemas"]["WebSocketMessage"] = WebSocketMessage.schema()
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Get the path to the autogen_magentic_one directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    templates_dir = os.path.join(base_dir, "templates")

    if not os.path.exists(static_dir):
        logger.error(f"Static directory not found at {static_dir}")
    if not os.path.exists(templates_dir):
        logger.error(f"Templates directory not found at {templates_dir}")

    try:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        reactflow_dir = os.path.join(static_dir, "reactflow")
        if not os.path.exists(reactflow_dir):
            os.makedirs(reactflow_dir)
            logger.warning(f"Created ReactFlow directory: {reactflow_dir}")
        reactflow_umd_dir = os.path.join(reactflow_dir, "umd")
        if not os.path.exists(reactflow_umd_dir):
            os.makedirs(reactflow_umd_dir)
            logger.warning(f"Created ReactFlow UMD directory: {reactflow_umd_dir}")
        
        # Log the contents of the ReactFlow directory after copying
        logger.info("Contents of ReactFlow directory after copying:")
        for root, dirs, files in os.walk(reactflow_dir):
            for file in files:
                logger.info(f"  {os.path.join(root, file)}")
        templates = Jinja2Templates(directory=templates_dir)
        templates.env.globals["url_for"] = app.url_path_for

        # Log the contents of the ReactFlow directory
        logger.info("Contents of ReactFlow directory:")
        for item in os.listdir(reactflow_dir):
            logger.info(f"  {item}")
    except Exception as e:
        logger.error(f"Error mounting static files or templates: {str(e)}")
        raise

    # Ensure the correct MIME type for JavaScript files
    @app.middleware("http")
    async def add_content_type_header(request, call_next):
        response = await call_next(request)
        if request.url.path.endswith('.js'):
            response.headers["Content-Type"] = "application/javascript"
        return response

    # Log the path of the main.js file
    main_js_path = os.path.join(static_dir, "main.js")
    logger.info(f"main.js path: {main_js_path}")
    if os.path.exists(main_js_path):
        logger.info(f"main.js file exists at {main_js_path}")
        with open(main_js_path, 'r') as f:
            logger.info(f"First 100 characters of main.js: {f.read(100)}")
    else:
        logger.error(f"main.js file not found at {main_js_path}")

    # Log the contents of the static directory
    logger.info("Contents of static directory:")
    for item in os.listdir(static_dir):
        logger.info(f"  {item}")

    # Print the actual paths for debugging
    logger.info(f"Static directory: {static_dir}")
    logger.info(f"Templates directory: {templates_dir}")

    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception as e:
            logger.error(f"Error rendering index.html: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/api/health")
    async def health_check():
        return JSONResponse(content={"status": "ok"})

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def run_openai_task(magnetic_one, task):
        try:
            return await magnetic_one.run_task(task)
        except Exception as e:
            logger.warning(f"Retry attempt for task: {task}. Error: {str(e)}")
            raise

    async def _run_task(task: str, websocket: WebSocket):
        logs_dir = "/tmp/magentic_one_logs"
        os.makedirs(logs_dir, exist_ok=True)

        logger.info(f"Starting task: {task}")
        try:
            magnetic_one = app.state.magnetic_one
            loaded_agents = magnetic_one.get_loaded_agents()
            if loaded_agents:
                await websocket.send_text(json.dumps({"type": "agents_loaded", "agents": loaded_agents}))
            else:
                logger.warning("No agents loaded")
                await websocket.send_text(json.dumps({"type": "warning", "message": "No agents loaded"}))
            await websocket.send_text(json.dumps({"type": "status", "message": "MagenticOne initialized."}))
            logger.info("Using pre-initialized MagenticOne")

            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    task_future = asyncio.create_task(run_openai_task(magnetic_one, task))
                    
                    async for log_entry in magnetic_one.stream_logs():
                        logger.debug(f"Log entry: {log_entry}")
                        try:
                            agent_name = log_entry.get('agent', 'Unknown')
                            if isinstance(agent_name, dict) and 'type' in agent_name:
                                agent_name = agent_name['type']
                            elif isinstance(agent_name, str):
                                agent_name = agent_name.split('.')[-1]  # Get the class name if it's a full path
                            
                            log_entry['agent'] = agent_name
                            await websocket.send_text(json.dumps({"type": "log", "data": log_entry}))
                            if log_entry.get('event') == 'agent_called':
                                await websocket.send_text(json.dumps({"type": "agent_called", "agent": agent_name}))
                            
                            # Send orchestrator output
                            if log_entry.get('event') == 'orchestrator_output':
                                await websocket.send_text(json.dumps({
                                    "type": "orchestrator_output",
                                    "message": log_entry.get('message', '')
                                }))
                            
                            # Send agent output
                            if log_entry.get('event') == 'agent_output':
                                await websocket.send_text(json.dumps({
                                    "type": "agent_output",
                                    "agent": agent_name,
                                    "message": log_entry.get('message', '')
                                }))
                            
                            # Send currently active agents
                            if log_entry.get('event') == 'active_agents_update':
                                await websocket.send_text(json.dumps({
                                    "type": "active_agents",
                                    "agents": log_entry.get('active_agents', [])
                                }))
                        except Exception as e:
                            logger.error(f"Error sending log entry: {str(e)}")

                    await task_future
                    break  # If successful, break out of the retry loop
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Retry attempt {retry_count} for task: {task}. Error: {str(e)}")
                    await websocket.send_text(json.dumps({"type": "retry", "attempt": retry_count, "max_retries": max_retries}))
                    if retry_count >= max_retries:
                        raise  # Re-raise the last exception if all retries are exhausted

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
            error_message = str(e)
            if "Error during task execution" in error_message:
                error_message = f"Task execution error: {error_message}"
            elif "RetryError" in error_message:
                error_message = "Failed to execute task after multiple attempts. Please try again."
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": error_message,
                "details": error_details
            }))

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """
        WebSocket endpoint for real-time communication with MagenticOne.

        This endpoint handles the WebSocket connection for the MagenticOne application.
        It manages the connection lifecycle, processes incoming tasks, and sends responses back to the client.

        Message Types:
        - error: Sent when an error occurs during initialization or task execution
          {type: "error", message: string, details?: string}
        
        - loaded_agents: Sent to inform about the loaded agents
          {type: "loaded_agents", agents: string[]}
        
        - warning: Sent when there are no loaded agents
          {type: "warning", message: string}
        
        - pong: Sent in response to a ping message
          {type: "pong"}
        
        - ping: Sent to keep the connection alive
          {type: "ping"}
        
        - status: Sent to update the client on the current status of the task
          {type: "status", message: string}
        
        - final_answer: Sent when the task is completed with a final answer
          {type: "final_answer", message: string}
        
        - log: Sent to provide detailed logs of the task execution
          {type: "log", data: object}
        
        - agent_called: Sent when a specific agent is called during task execution
          {type: "agent_called", agent: string}
        
        - orchestrator_output: Sent to provide output from the orchestrator
          {type: "orchestrator_output", message: string}
        
        - agent_output: Sent to provide output from individual agents
          {type: "agent_output", agent: string, message: string}
        
        - active_agents: Sent to update the list of currently active agents
          {type: "active_agents", agents: string[]}
        
        - retry: Sent when a task execution is being retried
          {type: "retry", attempt: number, max_retries: number}

        Args:
            websocket (WebSocket): The WebSocket connection object.

        Raises:
            WebSocketDisconnect: When the WebSocket connection is closed by the client.
        """
        try:
            await websocket.accept()
            logger.info("WebSocket connection established")
            logger.info(f"WebSocket connection details: {websocket.client}")

            if hasattr(app.state, 'initialization_error'):
                error_info = app.state.initialization_error
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "MagenticOne initialization failed",
                    "details": error_info
                }))
                return

            if not hasattr(app.state, 'magnetic_one'):
                logger.error("MagenticOne not initialized in app state")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "MagenticOne not initialized"
                }))
                return

            loaded_agents = app.state.magnetic_one.get_loaded_agents()
            if loaded_agents:
                await websocket.send_text(json.dumps({
                    "type": "loaded_agents",
                    "agents": loaded_agents
                }))
            else:
                logger.warning("No agents loaded")
                await websocket.send_text(json.dumps({
                    "type": "warning",
                    "message": "No agents loaded"
                }))

            while True:
                try:
                    task = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                    logger.info(f"Received task: {task}")

                    if task.lower() == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                        continue

                    logger.debug("Calling _run_task")
                    await _run_task(task, websocket)
                    logger.debug("_run_task completed")
                except asyncio.TimeoutError:
                    logger.debug("WebSocket receive timeout, sending ping")
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception as e:
                    logger.error(f"An error occurred in task execution: {e}", exc_info=True)
                    error_details = traceback.format_exc()
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"An error occurred in task execution: {str(e)}",
                        "details": error_details
                    }))
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"An unexpected error occurred in websocket_endpoint: {e}", exc_info=True)
            error_details = traceback.format_exc()
            try:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "details": error_details
                }))
            except:
                logger.error("Failed to send error message over WebSocket")
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
            loaded_agents = magnetic_one.get_loaded_agents()
            logger.info(f"Loaded agents: {loaded_agents}")
        except Exception as e:
            logger.error(f"Failed to initialize MagenticOne: {str(e)}", exc_info=True)
            app.state.magnetic_one = None
            app.state.initialization_error = {
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            # Log the full traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        if not app.state.magnetic_one or 'WebSurfer' not in app.state.magnetic_one.get_loaded_agents():
            logger.warning("WebSurfer agent not initialized. Some functionality may be limited.")

    logger.info("WebSocket endpoint registered")

    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)

def generate_ws_api_docs():
    from .generate_ws_api_docs import main as generate_docs
    generate_docs()
