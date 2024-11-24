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

for path in [autogen_path, packages_path, autogen_magentic_one_path]:
    if path.exists():
        sys.path.insert(0, str(path))
        print(f"Added to sys.path: {path}")
    else:
        print(f"Warning: {path} does not exist")

# Print the updated sys.path
print("Updated sys.path:")
for path in sys.path:
    print(f"  {path}")

# Install autogen_magentic_one package
if autogen_magentic_one_path.exists():
    print("Installing autogen_magentic_one package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(autogen_magentic_one_path)])
    print("autogen_magentic_one package installed successfully.")
else:
    print("Warning: autogen_magentic_one directory not found.")

# Define the base image
base_image = (modal.Image
    .debian_slim()
    .apt_install(["docker.io", "docker-compose"])
    .copy_local_dir(".devcontainer", "/root/.devcontainer")
    .run_commands(
        "cd /root/.devcontainer && docker-compose up -d",
        "wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list",
        "apt-get update",
        "apt-get install -y google-chrome-stable"
    ))

app = modal.App("autogen-magentic-one")
__all__ = ['app', 'image']

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
    .copy_mount(autogen_mount, remote_path="/root/autogen")
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
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-magentic-one",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-agentchat",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-core",
        "/root/autogen/python/.venv/bin/pip install -e /root/autogen/python/packages/autogen-ext",
        "/root/autogen/python/.venv/bin/pip install playwright",
        "/root/autogen/python/.venv/bin/playwright install --with-deps chromium",
        "/root/autogen/python/.venv/bin/playwright install-deps",
        "/root/autogen/python/.venv/bin/playwright install chromium",
        "/root/autogen/python/.venv/bin/python -m playwright install",
        "/root/autogen/python/.venv/bin/python -m playwright install-deps",
        "/root/autogen/python/.venv/bin/python -m playwright install chromium"
    )
    .shell("/bin/bash")
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

    venv_path = "/root/autogen/python/.venv"
    activate_this = os.path.join(venv_path, "bin", "activate_this.py")

    if os.path.exists(activate_this):
        exec(open(activate_this).read(), {'__file__': activate_this})
        print(f"Activated virtual environment: {venv_path}")
    else:
        print(f"Warning: Virtual environment activation script not found at {activate_this}")

    print("Python sys.path:")
    for path in sys.path:
        print(f"  {path}")

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
