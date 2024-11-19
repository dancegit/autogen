import modal
import os

app = modal.App("autogen-magentic-one")

# Create a mount for the entire project
project_mount = modal.Mount.from_local_dir("../", remote_path="/root/autogen")

# Install autogen-magentic-one from the local directory, playwright, and necessary browser dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("pip==23.2.1")  # Use a stable, recent version of pip
    .copy_mount(project_mount, remote_path="/root/autogen")
    .run_commands(
        "cd /root/autogen/packages/autogen-magentic-one && pip install -e .[all]",
        "cd /root/autogen/packages/autogen-magentic-one && pip install -e .",
        "playwright install --with-deps chromium"
    )
    .run_commands(
        "ls -R /root/autogen"  # Debug: List contents of the directory
    )
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
    cpu=1,
    mounts=[project_mount]
)
def run_magentic_one(task: str):
    from autogen_magentic_one import MagenticOneHelper
    helper = MagenticOneHelper()
    result = helper.run(task)
    return result

@app.function(image=image, mounts=[project_mount])
@modal.asgi_app()
def fastapi_app():
    from autogen_magentic_one.web_interface import app
    return app

@app.local_entrypoint()
def main(task: str):
    result = run_magentic_one.remote(task)
    print(result)

if __name__ == "__main__":
    print("To deploy this app, run the following command:")
    print("modal deploy " + __file__)
