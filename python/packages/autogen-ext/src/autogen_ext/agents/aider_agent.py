from typing import List, Optional, Sequence, Dict, Any
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import ChatMessage
from autogen_core.base import CancellationToken
from aider import models, io, coder, prompts, repomap
from .aider_config import AiderConfig, load_aider_config

class AiderAgent(BaseChatAgent):
    """An agent that uses Aider for code editing and generation tasks."""

    def __init__(self, name: str, description: str = "An AI agent that uses Aider for code-related tasks.", 
                 config: Dict[str, Any] = None):
        super().__init__(name, description)
        self.config = load_aider_config(config or {})
        self.model = models.Model(self.config.model_name)
        self.io = io.InputOutput()
        self.coder = coder.Coder(self.model, self.io, git_enabled=self.config.git_enabled)
        self.repo_path = self.config.repo_path
        self.repo_map = repomap.RepoMap(self.repo_path)

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        last_message = messages[-1]
        if last_message.role == "user":
            response = await self.process_user_message(last_message.content)
            return Response(content=response)
        return Response(content="I can only process user messages.")

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        self.coder.reset()
        self.repo_map.refresh()

    async def process_user_message(self, message: str) -> str:
        try:
            response = self.coder.run(message)
            return response
        except Exception as e:
            return f"Error processing message: {str(e)}"

    async def analyze_code(self, code: str) -> str:
        try:
            analysis_prompt = prompts.get_analysis_prompt(code)
            analysis = self.model.complete(analysis_prompt, max_tokens=self.config.max_tokens, temperature=self.config.temperature)
            return analysis
        except Exception as e:
            return f"Error analyzing code: {str(e)}"

    async def generate_code(self, prompt: str) -> str:
        try:
            generation_prompt = prompts.get_generation_prompt(prompt)
            generated_code = self.model.complete(generation_prompt, max_tokens=self.config.max_tokens, temperature=self.config.temperature)
            return generated_code
        except Exception as e:
            return f"Error generating code: {str(e)}"

    async def edit_code(self, code: str, instructions: str) -> str:
        try:
            edit_prompt = prompts.get_edit_prompt(code, instructions)
            edited_code = self.model.complete(edit_prompt, max_tokens=self.config.max_tokens, temperature=self.config.temperature)
            return edited_code
        except Exception as e:
            return f"Error editing code: {str(e)}"

    async def get_repo_map(self) -> Dict[str, Any]:
        try:
            return self.repo_map.get_map()
        except Exception as e:
            return {"error": f"Error getting repo map: {str(e)}"}

    async def update_file(self, file_path: str, new_content: str) -> None:
        try:
            self.coder.update_file(file_path, new_content)
        except Exception as e:
            raise ValueError(f"Error updating file: {str(e)}")

    async def commit_changes(self, commit_message: str) -> None:
        try:
            self.coder.commit(commit_message)
        except Exception as e:
            raise ValueError(f"Error committing changes: {str(e)}")
