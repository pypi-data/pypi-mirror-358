import json
from typing import TYPE_CHECKING

from .base import AIProvider

if TYPE_CHECKING:
    from ..config import Config


class OpenAIProvider(AIProvider):
    """OpenAI provider"""

    def __init__(self, config: "Config"):
        super().__init__(config)
        try:
            import openai

            self.client = openai.OpenAI(
                api_key=config.openai_api_key, base_url=config.openai_base_url
            )
        except ImportError:
            raise ImportError(
                "Module 'openai' is not installed. Please install it with 'pip install openai'."
            )

    def is_configured(self) -> bool:
        """Check if the provider is configured."""
        return bool(self.config.openai_api_key)

    def generate_commit_message(self, diff_content: str) -> str:
        """Generate a commit message using OpenAI."""
        prompt = self._create_base_prompt(diff_content)

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompts.OPENAI_SYSTEM_PROMPT,
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            response_content = response.choices[0].message.content.strip()
            # Parse the response content as JSON
            return json.loads(self._clean_markdown_json_block(response_content))
        except Exception as e:
            raise Exception(f"Error generating commit message with OpenAI: {str(e)}")
