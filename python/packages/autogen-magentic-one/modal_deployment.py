import modal
import os

app = modal.App("autogen-magentic-one")

# Create a mount for the package files
package_mount = modal.Mount.from_local_dir(".", remote_path="/root/autogen-magentic-one")

# Install autogen-magentic-one from the local directory, playwright, and necessary browser dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("pip==24.3.1")  # Upgrade pip to latest version
    .copy_mount(package_mount)
    .pip_install("/root/autogen-magentic-one")
    .run_commands("cd /root/autogen-magentic-one && pip install .")
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
    cpu=1,
    mounts=[package_mount]
)
def run_magentic_one(task: str):
    from autogen_magentic_one import MagenticOneHelper
    helper = MagenticOneHelper()
    result = helper.run(task)
    return result

@app.function(image=image, mounts=[package_mount])
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
