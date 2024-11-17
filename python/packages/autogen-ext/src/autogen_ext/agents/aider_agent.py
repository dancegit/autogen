from typing import List, Optional, Sequence, Dict, Any
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import ChatMessage
from autogen_core.base import CancellationToken
from .aider_config import AiderConfig, load_aider_config
from .aider_modal import run_aider, stub

class AiderAgent(BaseChatAgent):
    """An agent that uses Aider for code editing and generation tasks."""

    def __init__(self, name: str, description: str = "An AI agent that uses Aider for code-related tasks.", 
                 config: Dict[str, Any] = None):
        super().__init__(name, description)
        self.config = load_aider_config(config or {})

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        last_message = messages[-1]
        if last_message.role == "user":
            try:
                response = await run_aider.remote(last_message.content, self.config)
                return Response(content=response)
            except Exception as e:
                return Response(content=f"Error processing message: {str(e)}")
        return Response(content="I can only process user messages.")

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        # Reset functionality is handled within the Docker container
        pass

    async def analyze_code(self, code: str) -> str:
        try:
            response = await run_aider.remote(f"Analyze the following code:\n{code}", self.config)
            return response
        except Exception as e:
            return f"Error analyzing code: {str(e)}"

    async def generate_code(self, prompt: str) -> str:
        try:
            response = await run_aider.remote(f"Generate code for the following prompt:\n{prompt}", self.config)
            return response
        except Exception as e:
            return f"Error generating code: {str(e)}"

    async def edit_code(self, code: str, instructions: str) -> str:
        try:
            response = await run_aider.remote(f"Edit the following code:\n{code}\nInstructions:\n{instructions}", self.config)
            return response
        except Exception as e:
            return f"Error editing code: {str(e)}"

    async def get_repo_map(self) -> Dict[str, Any]:
        try:
            response = await run_aider.remote("Get repository map", self.config)
            return eval(response)  # Convert string representation of dict to actual dict
        except Exception as e:
            return {"error": f"Error getting repo map: {str(e)}"}

    async def update_file(self, file_path: str, new_content: str) -> None:
        try:
            await run_aider.remote(f"Update file {file_path} with the following content:\n{new_content}", self.config)
        except Exception as e:
            raise ValueError(f"Error updating file: {str(e)}")

    async def commit_changes(self, commit_message: str) -> None:
        try:
            await run_aider.remote(f"Commit changes with message: {commit_message}", self.config)
        except Exception as e:
            raise ValueError(f"Error committing changes: {str(e)}")
