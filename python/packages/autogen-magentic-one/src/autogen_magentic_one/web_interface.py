import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
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

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@modal_app.function(image=image)
@asgi_app()
def fastapi_app():
    return app

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run_task")
async def run_task(task: str = Form(...)):
    runtime = SingleThreadedAgentRuntime()
    client = create_completion_client_from_env(model="gpt-4o")

    async with DockerCommandLineCodeExecutor(work_dir="/tmp") as code_executor:
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
        await actual_surfer.init(
            model_client=client,
            downloads_folder="/tmp",
            start_page="https://www.bing.com",
            browser_channel="chromium",
            headless=True,
            debug_dir="/tmp",
            to_save_screenshots=False,
        )

        response = await runtime.send_message(RequestReplyMessage(task=task), orchestrator.id)
        await runtime.stop_when_idle()

        return {"result": response.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
