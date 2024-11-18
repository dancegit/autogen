import modal
from autogen_magentic_one import MagenticOneHelper

stub = modal.Stub("autogen-magentic-one")

@stub.function(
    image=modal.Image.debian_slim().pip_install(["autogen-magentic-one", "playwright"]),
    gpu="T4",
    timeout=600
)
def run_magentic_one(task: str):
    helper = MagenticOneHelper()
    result = helper.run(task)
    return result

@stub.local_entrypoint()
def main(task: str):
    result = run_magentic_one.remote(task)
    print(result)
