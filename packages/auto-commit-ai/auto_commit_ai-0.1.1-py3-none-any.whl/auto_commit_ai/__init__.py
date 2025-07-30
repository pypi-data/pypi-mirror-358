"""Commitly - Auto Commit Generator - Generate commit messages automatically using AI providers."""

__version__ = "0.1.0"
__author__ = "Toni Miquel Llull"

from .config import Config
from .core import AutoCommitGenerator
from .providers.factory import AIProviderFactory

__all__ = ["AutoCommitGenerator", "AIProviderFactory", "Config"]
