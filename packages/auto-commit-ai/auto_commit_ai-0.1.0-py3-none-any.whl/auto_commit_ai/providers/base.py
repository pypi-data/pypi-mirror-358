import json
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from . import prompts

if TYPE_CHECKING:
    from ..config import Config


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: "Config"):
        self.config = config
        self.prompts = prompts

    @abstractmethod
    def generate_commit_message(self, diff_content: str) -> json:
        """Generate a commit message based on the provided diff content."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is configured."""
        pass

    def _create_base_prompt(self, diff_content: str) -> str:
        """Create the base prompt for generating commit messages."""
        return prompts.BASE_COMMIT_PROMPT.format(diff_content=diff_content)

    def _clean_markdown_json_block(self, content: str) -> str:
        """Rremove markdown code blocks and extract JSON content."""
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            return match.group(1)
        return content.strip()
