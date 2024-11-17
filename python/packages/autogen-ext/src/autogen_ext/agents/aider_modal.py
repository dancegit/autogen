import modal

stub = modal.Stub("aider-agent")

def create_aider_image():
    return (
        modal.Image.from_registry("ghcr.io/paul-gauthier/aider:latest")
        .pip_install("modal")
    )

aider_image = create_aider_image()

@stub.function(
    image=aider_image,
    secret=modal.Secret.from_name("aider-secrets"),
    mounts=[modal.Mount.from_local_dir(".", remote_path="/workspace")]
)
def run_aider(message: str, config: dict) -> str:
    import os
    import subprocess
    
    os.chdir("/workspace")
    
    cmd = [
        "aider",
        "--model", config.get("model_name", "gpt-4"),
        "--no-git",
        "--input-history-file", "/dev/null",
        "--chat-history-file", "/dev/null",
        "--message", message
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

if __name__ == "__main__":
    with stub.run():
        result = run_aider.remote("Hello, Aider!", {"model_name": "gpt-4"})
        print(result)
