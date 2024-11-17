from typing import Dict, Any
from pydantic import BaseModel, Field

class AiderConfig(BaseModel):
    model_name: str = Field(default="gpt-4", description="The name of the LLM model to use")
    repo_path: str = Field(default=".", description="The path to the repository")
    git_enabled: bool = Field(default=True, description="Whether to use Git integration")
    max_tokens: int = Field(default=2000, description="Maximum number of tokens for LLM responses")
    temperature: float = Field(default=0.7, description="Temperature for LLM responses")

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'AiderConfig':
        return cls(**config)

def load_aider_config(config: Dict[str, Any]) -> AiderConfig:
    return AiderConfig.from_dict(config)
