import modal
import os

app = modal.App("autogen-magentic-one")

# Install autogen-magentic-one from the local directory, playwright, and necessary browser dependencies
image = (
    modal.Image.debian_slim()
    .pip_install(".")  # Install the current directory (autogen-magentic-one)
    .pip_install("playwright", "fastapi", "jinja2", "python-multipart")
    .run_commands("playwright install --with-deps chromium")
    .env({
        "BING_API_KEY": os.environ.get("BING_API_KEY", ""),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "CHAT_COMPLETION_KWARGS_JSON": os.environ.get("CHAT_COMPLETION_KWARGS_JSON", "")
    })
)

@app.function(
    image=image,
    gpu="T4",
    timeout=600,
    memory=1024,
    cpu=1
)
def run_magentic_one(task: str):
    from autogen_magentic_one import MagenticOneHelper
    helper = MagenticOneHelper()
    result = helper.run(task)
    return result

@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    from autogen_magentic_one.web_interface import app
    return app

@app.local_entrypoint()
def main(task: str):
    result = run_magentic_one.remote(task)
    print(result)

if __name__ == "__main__":
    modal.runner.deploy_app(app)
