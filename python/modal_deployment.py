import modal
import os
import pathlib
import sys

# Get the directory of this file
current_dir = pathlib.Path(__file__).parent.resolve()

# Print current directory and its contents for debugging
print(f"Current directory: {current_dir}")
print("Contents of current directory:")
for item in current_dir.iterdir():
    print(f"  {item}")

# Add the submodules directory to the Python path
submodules_path = current_dir.parent.parent / "submodules" / "modal_com_custom_sandboxes" / "src"
if submodules_path.exists():
    sys.path.insert(0, str(submodules_path))
    print(f"Added to sys.path: {submodules_path}")
else:
    print(f"Warning: {submodules_path} does not exist")

try:
    from modal_sandbox.images.base_image import get_base_image
except ImportError as e:
    print(f"Error importing get_base_image: {e}")
    print(f"sys.path: {sys.path}")
    print(f"Checking contents of {submodules_path.parent}:")
    if submodules_path.parent.exists():
        for item in submodules_path.parent.iterdir():
            print(f"  {item}")
    else:
        print(f"  {submodules_path.parent} does not exist")
    
    # Fallback to a basic Modal image if get_base_image is not available
    print("Using fallback Modal image")
    def get_base_image():
        return modal.Image.debian_slim().pip_install("modal")

app = modal.App("autogen-magentic-one")

# Create mounts for specific directories
python_mount = modal.Mount.from_local_dir(current_dir.parent.parent.parent, remote_path="/root/autogen/python")
sandboxes_mount = modal.Mount.from_local_dir(submodules_path.parent, remote_path="/root/autogen/submodules/modal_com_custom_sandboxes", condition=lambda _: submodules_path.parent.exists())
devcontainer_mount = modal.Mount.from_local_dir(current_dir.parent.parent.parent.parent / ".devcontainer", remote_path="/root/autogen/.devcontainer")
protos_mount = modal.Mount.from_local_dir(current_dir.parent.parent.parent.parent / "protos", remote_path="/root/autogen/protos")
build_script_mount = modal.Mount.from_local_file(current_dir.parent.parent.parent.parent / "build_autogen_magentic_one.sh", remote_path="/root/autogen/build_autogen_magentic_one.sh")

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
        "ls -la",  # List directory contents to debug
        "pwd",  # Print working directory
        "find /root/autogen -name pyproject.toml",  # Find pyproject.toml files
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
    print("Current working directory:", os.getcwd())
    print("Contents of current directory:")
    for item in os.listdir():
        print(f"  {item}")
    print("To deploy this app, run the following command:")
    print("modal deploy " + __file__)
