import modal
from .agents.aider_agent import AiderAgent

app = modal.App()

# Create a custom Modal image for the AiderAgent
image = (
    modal.Image.debian_slim()
    .pip_install("aider-chat", "modal")
    .run_commands("mkdir -p /root/workspace")
)

@app.function(image=image)
def run_aider_agent(message: str):
    agent = AiderAgent("AiderAgent")
    return agent.process_message(message)

if __name__ == "__main__":
    with app.run():
        result = run_aider_agent.remote("Implement a simple Flask app")
        print(result)
