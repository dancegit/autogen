import modal
import os
import pathlib
import sys

# Get the directory of this file
current_dir = pathlib.Path(__file__).parent.resolve()

# Add the submodules directory to the Python path
sys.path.append(str(current_dir.parent / "submodules" / "modal_com_custom_sandboxes" / "src"))

from modal_sandbox.images.base_image import get_base_image

app = modal.App("autogen-magentic-one")

# Create mounts for specific directories
python_mount = modal.Mount.from_local_dir(current_dir, remote_path="/root/autogen/python")
sandboxes_mount = modal.Mount.from_local_dir(current_dir.parent / "submodules" / "modal_com_custom_sandboxes", remote_path="/root/autogen/submodules/modal_com_custom_sandboxes", condition=lambda _: (current_dir.parent / "submodules" / "modal_com_custom_sandboxes").exists())
devcontainer_mount = modal.Mount.from_local_dir(current_dir.parent / ".devcontainer", remote_path="/root/autogen/.devcontainer")
protos_mount = modal.Mount.from_local_dir(current_dir.parent / "protos", remote_path="/root/autogen/protos")
build_script_mount = modal.Mount.from_local_file(current_dir.parent / "build_autogen_magentic_one.sh", remote_path="/root/autogen/build_autogen_magentic_one.sh")

# Combine all mounts
project_mounts = [python_mount, sandboxes_mount, devcontainer_mount, protos_mount, build_script_mount]

# Use the base_image and extend it with our specific requirements
image = (
    get_base_image()
    .pip_install("uv")
    .copy_mount(python_mount, remote_path="/root/autogen/python")
    .copy_mount(sandboxes_mount, remote_path="/root/autogen/submodules/modal_com_custom_sandboxes")
    .copy_mount(devcontainer_mount, remote_path="/root/autogen/.devcontainer")
    .copy_mount(protos_mount, remote_path="/root/autogen/protos")
    .copy_mount(build_script_mount, remote_path="/root/autogen/build_autogen_magentic_one.sh")
    .run_commands(
        "cd /root/autogen/python",
        "uv --version",  # Check if uv is installed correctly
        "uv sync --all-extras",
        "source .venv/bin/activate",
        "cd packages/autogen-magentic-one",
        "pip install -e .",
        "cd /root/autogen/python",
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
    mounts=project_mounts
)
def run_magentic_one(task: str):
    from autogen_magentic_one import MagenticOneHelper
    helper = MagenticOneHelper()
    result = helper.run(task)
    return result

@app.function(image=image, mounts=project_mounts)
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
