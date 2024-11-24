import asyncio
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, AgentProxy
from autogen_ext.code_executors import DockerCommandLineCodeExecutor
from autogen_magentic_one.agents.coder import Coder, Executor
from autogen_magentic_one.agents.file_surfer import FileSurfer
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from autogen_magentic_one.utils import create_completion_client_from_env
from modal import Stub, asgi_app
from modal_deployment import app as modal_app, image
import os
import sys


app = FastAPI()

@modal_app.function(image=image)
@asgi_app()
def fastapi_app():
    return app

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AutoGen Magentic One</title>
    </head>
    <body>
        <h1>Welcome to AutoGen Magentic One</h1>
        <form action="/run_task" method="post">
            <label for="task">Enter your task:</label><br>
            <textarea id="task" name="task" rows="4" cols="50"></textarea><br>
            <input type="submit" value="Run Task">
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/run_task")
async def run_task(task: str = Form(...)):
    runtime = SingleThreadedAgentRuntime()
    client = create_completion_client_from_env(model="gpt-4")
    print(f"CHAT_COMPLETION_KWARGS_JSON: {os.environ.get('CHAT_COMPLETION_KWARGS_JSON', 'Not set')}")

    try:
        try:
            code_executor = DockerCommandLineCodeExecutor(work_dir="/tmp")
            await code_executor.start()
        except Exception as e:
            logging.warning(f"Failed to start Docker executor: {e}. Falling back to local execution.")
            code_executor = None

        await Coder.register(runtime, "Coder", lambda: Coder(model_client=client))
        await Executor.register(
            runtime,
            "Executor",
            lambda: Executor("An agent for executing code", executor=code_executor),
        )
        await MultimodalWebSurfer.register(runtime, "WebSurfer", MultimodalWebSurfer)
        await FileSurfer.register(runtime, "file_surfer", lambda: FileSurfer(model_client=client))

        agent_list = [
            AgentProxy(AgentId("WebSurfer", "default"), runtime),
            AgentProxy(AgentId("Coder", "default"), runtime),
            AgentProxy(AgentId("Executor", "default"), runtime),
            AgentProxy(AgentId("file_surfer", "default"), runtime),
        ]

        await LedgerOrchestrator.register(
            runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=client,
                max_rounds=30,
                max_time=25 * 60,
                return_final_answer=True,
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), runtime)

        runtime.start()

            actual_surfer = await runtime.try_get_underlying_agent_instance(agent_list[0].id, type=MultimodalWebSurfer)
            try:
                await actual_surfer.init(
                    model_client=client,
                    downloads_folder="/tmp",
                    start_page="https://www.bing.com",
                    browser_channel="chromium",
                    headless=True,
                    debug_dir="/tmp",
                    to_save_screenshots=False,
                )
            except Exception as e:
                logging.error(f"Failed to initialize MultimodalWebSurfer: {e}")
                logging.error("Falling back to text-only mode")
                # Remove WebSurfer from agent_list
                agent_list = [agent for agent in agent_list if agent.id.type != "WebSurfer"]

            response = await runtime.send_message(RequestReplyMessage(task), orchestrator.id)
            await runtime.stop_when_idle()

            return {"result": response.content}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    import sys
    import os

    # Activate the virtual environment
    venv_path = "/root/autogen/python/.venv"
    activate_this = os.path.join(venv_path, "bin", "activate_this.py")
    if os.path.exists(activate_this):
        exec(open(activate_this).read(), {'__file__': activate_this})
        print(f"Activated virtual environment: {venv_path}")
    else:
        print(f"Warning: Virtual environment activation script not found at {activate_this}")
        print("Falling back to system Python")

    # Print Python path for debugging
    print("Python sys.path:")
    for path in sys.path:
        print(f"  {path}")

    uvicorn.run(app, host="0.0.0.0", port=8000)
