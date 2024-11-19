import modal

app = modal.App("autogen-magentic-one")

image = modal.Image.debian_slim().pip_install([".", "playwright"])

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
