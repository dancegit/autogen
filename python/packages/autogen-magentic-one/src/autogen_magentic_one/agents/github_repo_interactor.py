import os
from typing import List, Tuple, Any
from github import Github, GithubException
from autogen_core.base import CancellationToken
from autogen_core.components import default_subscription
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage
from ..messages import UserContent
from .base_worker import BaseWorker

@default_subscription
class GitHubRepoInteractor(BaseWorker):
    """An agent that can interact with GitHub repositories."""

    DEFAULT_DESCRIPTION = "A GitHub repository interaction agent that can perform various operations on GitHub repositories."

    DEFAULT_SYSTEM_MESSAGES = [
        SystemMessage("""You are a helpful AI assistant specialized in GitHub repository operations.
You can perform various tasks related to GitHub repositories such as creating issues, commenting on pull requests, and fetching repository information.
When asked to perform a GitHub operation, use the appropriate function to execute the task.
Always provide clear and concise responses about the actions taken or information retrieved.""")
    ]

    def __init__(
        self,
        model_client: ChatCompletionClient,
        github_token: str,
        description: str = DEFAULT_DESCRIPTION,
        system_messages: List[SystemMessage] = DEFAULT_SYSTEM_MESSAGES,
    ) -> None:
        super().__init__(description)
        self._model_client = model_client
        self._system_messages = system_messages
        self._github = Github(github_token)

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """Respond to a reply request."""
        response = await self._model_client.create(
            self._system_messages + self._chat_history, cancellation_token=cancellation_token
        )
        assert isinstance(response.content, str)
        
        # Process the response and execute GitHub operations if needed
        result = self._process_and_execute_github_operations(response.content)
        
        return False, result

    def _process_and_execute_github_operations(self, content: str) -> str:
        # This method would parse the content and execute the appropriate GitHub operations
        # For demonstration, we'll implement a few example operations
        if "create_issue" in content.lower():
            return self._create_issue(content)
        elif "comment_on_pull_request" in content.lower():
            return self._comment_on_pull_request(content)
        elif "get_repo_info" in content.lower():
            return self._get_repo_info(content)
        else:
            return f"Processed content: {content}\nNo specific GitHub operation was executed."

    def _create_issue(self, content: str) -> str:
        # Extract repository name, issue title, and body from the content
        # This is a simplified example and would need more robust parsing in a real implementation
        repo_name = "owner/repo"  # Extract this from content
        issue_title = "New Issue"  # Extract this from content
        issue_body = "Issue description"  # Extract this from content
        
        try:
            repo = self._github.get_repo(repo_name)
            issue = repo.create_issue(title=issue_title, body=issue_body)
            return f"Created issue #{issue.number} in {repo_name}: {issue.html_url}"
        except GithubException as e:
            return f"Failed to create issue: {str(e)}"

    def _comment_on_pull_request(self, content: str) -> str:
        # Extract repository name, PR number, and comment from the content
        repo_name = "owner/repo"  # Extract this from content
        pr_number = 1  # Extract this from content
        comment = "PR comment"  # Extract this from content
        
        try:
            repo = self._github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            comment = pr.create_issue_comment(comment)
            return f"Commented on PR #{pr_number} in {repo_name}: {comment.html_url}"
        except GithubException as e:
            return f"Failed to comment on PR: {str(e)}"

    def _get_repo_info(self, content: str) -> str:
        # Extract repository name from the content
        repo_name = "owner/repo"  # Extract this from content
        
        try:
            repo = self._github.get_repo(repo_name)
            return f"Repository: {repo.full_name}\nDescription: {repo.description}\nStars: {repo.stargazers_count}\nForks: {repo.forks_count}"
        except GithubException as e:
            return f"Failed to get repository info: {str(e)}"
