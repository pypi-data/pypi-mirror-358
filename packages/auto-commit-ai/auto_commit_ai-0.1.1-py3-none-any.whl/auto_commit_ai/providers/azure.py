import json
from typing import TYPE_CHECKING

from .base import AIProvider
from .prompts import BASE_COMMIT_PROMPT, OPENAI_SYSTEM_PROMPT

if TYPE_CHECKING:
    from ..config import Config


class AzureOpenAIProvider(AIProvider):
    """Azure OpenAI provider"""

    def __init__(self, config: "Config"):
        super().__init__(config)
        try:
            import openai

            self.client = openai.AzureOpenAI(
                api_key=config.azure_api_key,
                azure_endpoint=config.azure_endpoint,
                api_version=config.azure_api_version,
            )
        except ImportError:
            raise ImportError(
                "OpenAI library is not installed. Please install it with 'pip install openai'."
            )

    def is_configured(self) -> bool:
        """Check if the provider is configured."""
        return bool(self.config.azure_api_key and self.config.azure_endpoint)

    def generate_commit_message(self, diff_content: str) -> str:
        """Generate a commit message using Azure OpenAI."""
        prompt = self._create_base_prompt(diff_content)

        try:
            response = self.client.chat.completions.create(
                model=self.config.azure_model,
                messages=[
                    {
                        "role": "system",
                        "content": OPENAI_SYSTEM_PROMPT,
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
            raise Exception(
                f"Error generating commit message with Azure OpenAI: {str(e)}"
            )
