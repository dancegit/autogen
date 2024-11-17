import re
from typing import List, Tuple, Dict, Any
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
        operations = {
            "create_issue": self._create_issue,
            "comment_on_pull_request": self._comment_on_pull_request,
            "get_repo_info": self._get_repo_info,
            "list_issues": self._list_issues,
            "create_pull_request": self._create_pull_request,
            "list_pull_requests": self._list_pull_requests,
            "get_commit_info": self._get_commit_info,
        }

        for operation, func in operations.items():
            if operation in content.lower():
                return func(content)

        return f"Processed content: {content}\nNo specific GitHub operation was executed."

    def _extract_params(self, content: str, params: List[str]) -> Dict[str, str]:
        extracted = {}
        for param in params:
            match = re.search(rf"{param}:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
            if match:
                extracted[param] = match.group(1).strip()
        return extracted

    def _create_issue(self, content: str) -> str:
        params = self._extract_params(content, ["repo_name", "issue_title", "issue_body"])
        try:
            repo = self._github.get_repo(params["repo_name"])
            issue = repo.create_issue(title=params["issue_title"], body=params["issue_body"])
            return f"Created issue #{issue.number} in {params['repo_name']}: {issue.html_url}"
        except GithubException as e:
            return f"Failed to create issue: {str(e)}"

    def _comment_on_pull_request(self, content: str) -> str:
        params = self._extract_params(content, ["repo_name", "pr_number", "comment"])
        try:
            repo = self._github.get_repo(params["repo_name"])
            pr = repo.get_pull(int(params["pr_number"]))
            comment = pr.create_issue_comment(params["comment"])
            return f"Commented on PR #{params['pr_number']} in {params['repo_name']}: {comment.html_url}"
        except GithubException as e:
            return f"Failed to comment on PR: {str(e)}"

    def _get_repo_info(self, content: str) -> str:
        params = self._extract_params(content, ["repo_name"])
        try:
            repo = self._github.get_repo(params["repo_name"])
            return f"Repository: {repo.full_name}\nDescription: {repo.description}\nStars: {repo.stargazers_count}\nForks: {repo.forks_count}"
        except GithubException as e:
            return f"Failed to get repository info: {str(e)}"

    def _list_issues(self, content: str) -> str:
        params = self._extract_params(content, ["repo_name", "state"])
        try:
            repo = self._github.get_repo(params["repo_name"])
            state = params.get("state", "open")
            issues = repo.get_issues(state=state)
            return "\n".join([f"#{issue.number}: {issue.title}" for issue in issues[:10]])
        except GithubException as e:
            return f"Failed to list issues: {str(e)}"

    def _create_pull_request(self, content: str) -> str:
        params = self._extract_params(content, ["repo_name", "title", "body", "head", "base"])
        try:
            repo = self._github.get_repo(params["repo_name"])
            pr = repo.create_pull(title=params["title"], body=params["body"], head=params["head"], base=params["base"])
            return f"Created PR #{pr.number} in {params['repo_name']}: {pr.html_url}"
        except GithubException as e:
            return f"Failed to create pull request: {str(e)}"

    def _list_pull_requests(self, content: str) -> str:
        params = self._extract_params(content, ["repo_name", "state"])
        try:
            repo = self._github.get_repo(params["repo_name"])
            state = params.get("state", "open")
            prs = repo.get_pulls(state=state)
            return "\n".join([f"#{pr.number}: {pr.title}" for pr in prs[:10]])
        except GithubException as e:
            return f"Failed to list pull requests: {str(e)}"

    def _get_commit_info(self, content: str) -> str:
        params = self._extract_params(content, ["repo_name", "commit_sha"])
        try:
            repo = self._github.get_repo(params["repo_name"])
            commit = repo.get_commit(params["commit_sha"])
            return f"Commit: {commit.sha}\nAuthor: {commit.commit.author.name}\nMessage: {commit.commit.message}"
        except GithubException as e:
            return f"Failed to get commit info: {str(e)}"
