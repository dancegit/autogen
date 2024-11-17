import modal

stub = modal.Stub("aider-agent")

def create_aider_image():
    return (
        modal.Image.debian_slim()
        .pip_install("aider-chat")
        .run_commands("mkdir -p /root/workspace")
    )

aider_image = create_aider_image()

@stub.function(
    image=aider_image,
    secret=modal.Secret.from_name("aider-secrets"),
    mounts=[modal.Mount.from_local_dir(".", remote_path="/root/workspace")]
)
def run_aider(message: str, config: dict) -> str:
    import os
    from aider import models, io, coder, prompts, repomap
    
    os.chdir("/root/workspace")
    
    aider_config = config
    model = models.Model(aider_config["model_name"])
    io_handler = io.InputOutput()
    coder_instance = coder.Coder(model, io_handler, git_enabled=aider_config.get("git_enabled", True))
    repo_map = repomap.RepoMap(aider_config.get("repo_path", "."))
    
    response = coder_instance.run(message)
    return response

if __name__ == "__main__":
    with stub.run():
        result = run_aider.remote("Hello, Aider!", {"model_name": "gpt-4"})
        print(result)
