import modal
import os
from modal_sandbox.images.base_image import base_image

app = modal.App("autogen-magentic-one")

# Install autogen-magentic-one from the local directory, playwright, and necessary browser dependencies
image = (
    base_image
    .pip_install(".")  # Install the current directory (autogen-magentic-one)
    .pip_install("playwright")
    .run_commands("playwright install --with-deps chromium")
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

@app.local_entrypoint()
def main(task: str):
    result = run_magentic_one.remote(task)
    print(result)

if __name__ == "__main__":
    modal.runner.deploy_app(app)
