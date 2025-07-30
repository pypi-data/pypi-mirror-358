# ================================
# MAIN FUNCTION FOR CLI
# ================================

import argparse
import sys

from .core import AutoCommitGenerator, Config


def main():
    """Main function to handle command line arguments and execute the commit generation."""
    parser = argparse.ArgumentParser(
        description="Generate commit messages automatically using AI providers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s                    # Generate a commit message for staged changes
  %(prog)s --all              # Include all files (staged and unstaged) in the commit
  %(prog)s --provider google  # Use Google Gemini
  %(prog)s --provider azure   # Use Azure OpenAI

Required environment variables (.env):
  # OpenAI
  OPENAI_API_KEY=your_api_key
  OPENAI_MODEL=gpt-3.5-turbo
  
  # Google Gemini
  GOOGLE_API_KEY=your_api_key
  GOOGLE_MODEL=gemini-pro
  
  # Azure OpenAI
  AZURE_OPENAI_API_KEY=your_api_key
  AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
  AZURE_OPENAI_MODEL=gpt-35-turbo
  
  # General
  DEFAULT_AI_PROVIDER=openai  # openai, google, azure
  MAX_TOKENS=200 # Maximum tokens for the AI response
  TEMPERATURE=0.3 # Controls randomness in AI responses (0.1 = deterministic, 1.0 = more random)
        """,
    )

    parser.add_argument(
        "--provider",
        "-p",
        choices=["openai", "google", "azure"],
        help="AI provider to use for generating commit messages. Defaults to the provider set in the environment variable DEFAULT_AI_PROVIDER.",
    )

    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Add all files (staged and unstaged) to the commit. By default, only staged changes are included. All files will be added to the commit if this flag is set.",
    )

    parser.add_argument(
        "--version", "-v", action="version", version="Auto Commit Generator 0.1.0"
    )

    args = parser.parse_args()

    try:
        # Load configuration from environment variables
        config = Config.from_env()

        # Create and execute the AutoCommitGenerator
        generator = AutoCommitGenerator(config)
        generator.generate_and_commit(provider_name=args.provider, include_all=args.all)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
