import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Loaded configuration for the application."""

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    openai_base_url: Optional[str] = None

    # Google (Gemini)
    google_api_key: Optional[str] = None
    google_model: Optional[str] = None

    # Azure OpenAI
    azure_api_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_model: Optional[str] = None
    azure_api_version: Optional[str] = None

    # General
    default_provider: str = "openai"
    max_tokens: int = 150
    temperature: float = 0.3

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        current_dir_dotenv = os.path.join(os.getcwd(), ".auto_commit_ai.env")
        home_dir_dotenv = os.path.join(os.path.expanduser("~"), ".auto_commit_ai.env")

        if os.path.exists(current_dir_dotenv):
            load_dotenv(dotenv_path=current_dir_dotenv)

        elif os.path.exists(home_dir_dotenv):
            load_dotenv(dotenv_path=home_dir_dotenv, override=True)
        else:
            print(
                "No .env file found in the current directory or home directory. "
                "Please, create a .auto_commit_ai.env file with the necessary configuration variables."
            )
            pass

        return cls(
            # OpenAI
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL"),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            # Google
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            google_model=os.getenv("GOOGLE_MODEL"),
            # Azure OpenAI
            azure_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_model=os.getenv("AZURE_OPENAI_MODEL"),
            azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            # General
            default_provider=os.getenv("DEFAULT_AI_PROVIDER", "openai"),
            max_tokens=int(os.getenv("MAX_TOKENS", "200")),
            temperature=float(os.getenv("TEMPERATURE", "0.3")),
        )
