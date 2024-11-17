from typing import Dict, Any
from autogen_agentchat.base import Response
from autogen_core.base import CancellationToken
from ..agents.aider_agent import AiderAgent
from .github_aware_code_executor import GithubAwareCodeExecutor

class GithubAiderExecutor(GithubAwareCodeExecutor):
    def __init__(self, aider_config: Dict[str, Any], github_token: str):
        super().__init__(github_token)
        self.aider_agent = AiderAgent("AiderAgent", config=aider_config)

    async def execute(self, code: str, cancellation_token: CancellationToken) -> Response:
        # First, use Aider to analyze and potentially modify the code
        aider_response = await self.aider_agent.on_messages([{"role": "user", "content": f"Analyze and improve this code:\n{code}"}], cancellation_token)
        
        # If Aider made changes, use the improved code
        if aider_response.content != code:
            code = aider_response.content

        # Now execute the code using the parent class method
        return await super().execute(code, cancellation_token)

    async def commit_changes(self, message: str, cancellation_token: CancellationToken) -> Response:
        # Use Aider to commit changes
        return await self.aider_agent.commit_changes(message)

    async def get_repo_map(self, cancellation_token: CancellationToken) -> Dict[str, Any]:
        # Use Aider to get the repository map
        return await self.aider_agent.get_repo_map()
