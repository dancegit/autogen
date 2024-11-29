import modal
import os
import pathlib
import sys
import subprocess

# Get the directory of this file
current_dir = pathlib.Path(__file__).parent.resolve()

# Print current directory and its contents for debugging
print(f"Current directory: {current_dir}")
print("Contents of current directory:")
for item in current_dir.iterdir():
    print(f"  {item}")

# Add the necessary paths to the Python path
autogen_path = current_dir.parent  # Go up one level to reach the autogen root
packages_path = current_dir / "packages"
autogen_magentic_one_path = packages_path / "autogen-magentic-one"


# Define the base image
base_image = (modal.Image
    .debian_slim()
    .apt_install(["wget", "gnupg", "ffmpeg"])
    .run_commands(
        "wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list",
        "apt-get update",
        "apt-get install -y google-chrome-stable"
    ))

# Remove the Docker image definition as it's not needed for now

app = modal.App("autogen-magentic-one")
__all__ = ['app', 'image', 'docker_image']

# Create a single mount for the autogen folder
autogen_mount = modal.Mount.from_local_dir(
    current_dir.parent,
    remote_path="/root/autogen",
    condition=lambda path: not any(excluded in path for excluded in [".github", "docs", "dotnet", "venv",".venv",".aider*"])
)

# Combine all mounts
project_mounts = [autogen_mount]

# Use the base_image and extend it with our specific requirements
image = (
    base_image
    .copy_mount(autogen_mount, remote_path="/")
    .workdir("/root/autogen/python")
    .run_commands(
        "python3 -m venv .venv",
        "touch /root/.bashrc",
        "echo 'export PATH=/root/autogen/python/.venv/bin:$PATH' >> /root/.bashrc",
        "echo 'alias python=/root/autogen/python/.venv/bin/python' >> /root/.bashrc",
        "echo 'alias pip=/root/autogen/python/.venv/bin/pip' >> /root/.bashrc",
        ". /root/.bashrc",
        "/root/autogen/python/.venv/bin/pip install --upgrade pip",
        "/root/autogen/python/.venv/bin/pip install uv",
        "ls -la /root/autogen/python/packages",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-core",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-ext",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-magentic-one",
        "/root/autogen/python/.venv/bin/pip install grpclib PyGithub",
        "/root/autogen/python/.venv/bin/pip install /root/autogen/python/packages/autogen-agentchat",
        "/root/autogen/python/.venv/bin/pip install /root/autogen/python/packages/agbench",
        "/root/autogen/python/.venv/bin/pip install /root/autogen/python/packages/autogen-studio",
        "/root/autogen/python/.venv/bin/pip install tenacity",
        "/root/autogen/python/.venv/bin/pip install playwright",
        "/root/autogen/python/.venv/bin/playwright install --with-deps chromium",
        "/root/autogen/python/.venv/bin/playwright install-deps",
        "/root/autogen/python/.venv/bin/playwright install chromium",
        "/root/autogen/python/.venv/bin/python -m playwright install",
        "/root/autogen/python/.venv/bin/python -m playwright install-deps",
        "/root/autogen/python/.venv/bin/python -m playwright install chromium"
    )
    .workdir("/root")
    .run_commands(
        "apt-get install -y nodejs npm",
        "npm init -y",
        "npm install react react-dom @reactflow/core --no-fund --no-audit",
        "mkdir -p /root/autogen/python/packages/autogen-magentic-one/src/autogen_magentic_one/static/reactflow/umd",
        "cp /root/node_modules/react/umd/react.production.min.js /root/autogen/python/packages/autogen-magentic-one/src/autogen_magentic_one/static/reactflow/umd/",
        "cp /root/node_modules/react-dom/umd/react-dom.production.min.js /root/autogen/python/packages/autogen-magentic-one/src/autogen_magentic_one/static/reactflow/umd/",
        "cp /root/node_modules/@reactflow/core/dist/reactflow.production.min.js /root/autogen/python/packages/autogen-magentic-one/src/autogen_magentic_one/static/reactflow/",
        "cp /root/node_modules/@reactflow/core/dist/style.css /root/autogen/python/packages/autogen-magentic-one/src/autogen_magentic_one/static/reactflow/"
    )
    .env({
        "BING_API_KEY": os.environ.get("BING_API_KEY", ""),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "CHAT_COMPLETION_KWARGS_JSON": '{"model": "gpt-4"}',
        "PATH": "/root/autogen/python/.venv/bin:${PATH}"
    })
)

# Print environment variables for debugging
print("Environment variables:")
print(f"BING_API_KEY: {'Set' if os.environ.get('BING_API_KEY') else 'Not set'}")
print(f"OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
print(f"CHAT_COMPLETION_KWARGS_JSON: {os.environ.get('CHAT_COMPLETION_KWARGS_JSON', 'Not set')}")

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
def modal_fastapi_app():
    import sys
    import os
    import subprocess
    try:
        import autogen_magentic_one
        print(f"autogen_magentic_one path: {autogen_magentic_one.__file__}")
        from autogen_magentic_one.web_interface import app
        return app
    except ImportError as e:
        print(f"Error importing app: {e}")
        print("Detailed sys.path:")
        for i, path in enumerate(sys.path):
            print(f"  {i}: {path}")
            if os.path.exists(path):
                print(f"    Contents: {os.listdir(path)}")
            else:
                print("    Path does not exist")

        # Check if the autogen_magentic_one directory exists
        autogen_magentic_one_dir = os.path.join(current_dir, "packages", "autogen-magentic-one")
        if os.path.exists(autogen_magentic_one_dir):
            print(f"autogen_magentic_one directory exists: {autogen_magentic_one_dir}")
            print("Contents:")
            for item in os.listdir(autogen_magentic_one_dir):
                print(f"  {item}")

            # Try to install the package again
            print("Attempting to install autogen_magentic_one package...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", autogen_magentic_one_dir])
            print("autogen_magentic_one package installed successfully.")

            # Try importing again
            import autogen_magentic_one
            from autogen_magentic_one.web_interface import app
            return app
        else:
            print(f"autogen_magentic_one directory does not exist: {autogen_magentic_one_dir}")

        raise ImportError("Failed to import autogen_magentic_one after attempted installation")

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

    # Check if the autogen_magentic_one package is installed and print its location
    try:
        import autogen_magentic_one
        print(f"autogen_magentic_one is installed at: {autogen_magentic_one.__file__}")
        print(f"autogen_magentic_one version: {autogen_magentic_one.__version__}")
    except ImportError as e:
        print(f"Warning: autogen_magentic_one is not installed. Error: {e}")
    except AttributeError:
        print("Warning: autogen_magentic_one is installed but __version__ is not available")
# Docker-related function removed
