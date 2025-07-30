import sys
from typing import Optional

from .config import Config
from .git_utils import GitUtils
from .providers.factory import AIProviderFactory


class AutoCommitGenerator:
    """Automatic commit message generator using AI providers."""

    def __init__(self, config: Config):
        self.config = config
        self.git_utils = GitUtils()

    def generate_and_commit(
        self, provider_name: Optional[str] = None, include_all: bool = False
    ) -> None:
        """Generate a commit message using an AI provider and commit changes."""

        # Check if in a Git repository
        if not self.git_utils.is_git_repo():
            raise Exception("Not in a Git repository.")

        # Determine the provider to use
        provider_name = provider_name or self.config.default_provider

        # Create the AI provider instance
        try:
            ai_provider = AIProviderFactory.create_provider(provider_name, self.config)
        except Exception as e:
            raise Exception(f"Error configuring AI provider: {e}")

        # Check if there are changes to commit
        if include_all:
            if not (
                self.git_utils.has_staged_changes()
                or self.git_utils.has_unstaged_changes()
            ):
                print("No changes to commit.")
                return
            diff_content = self.git_utils.get_all_diff()
        else:
            if not self.git_utils.has_staged_changes():
                print(
                    "No staged changes found. Please stage your changes before committing or use the --all flag."
                )
                return
            diff_content = self.git_utils.get_staged_diff()

        if not diff_content.strip():
            print("No changes detected in files.")
            return

        # Generate the commit message
        print("Generating commit message...")
        try:
            commit_message = ai_provider.generate_commit_message(diff_content)
        except Exception as e:
            raise Exception(f"Error generating commit message: {e}")

        # Show the generated message to the user
        print(f"\n{'='*50}")
        print("GENERATED MESSAGE:")
        print(f"{'='*50}")
        print(f"Title: {commit_message["title"]}")
        print(f"Description: {commit_message['description']}")
        print(f"{'='*50}")

        # Request user confirmation
        while True:
            response = input("\nUse this commit message? (y/n): ").lower().strip()

            if response in ["y", "yes", "sí", "si"]:
                break
            elif response in ["n", "no"]:
                print("Commit cancelled.")
                return
            else:
                print("Reply with 'y' to confirm or 'n' to cancel.")

        # If the user wants to include all changes, stage them
        if include_all:
            print("Adding all changes to staging...")
            self.git_utils.stage_all_changes()

        # Create the commit with the generated message
        try:
            self.git_utils.commit_with_message(commit_message)
            print("✅ Commit successful!")
            while True:
                push_response = (
                    input("\nWould you like to push the changes? (y/n): ")
                    .lower()
                    .strip()
                )
                if push_response in ["y", "yes", "sí", "si"]:
                    try:
                        self.git_utils.push_changes()
                    except Exception as e:
                        print(
                            f"❌ Error pushing changes: {e}", file=sys.stderr
                        )  # Import sys for this
                    break  # Exit the push loop
                elif push_response in ["n", "no"]:
                    print("Push cancelled.")
                    break  # Exit the push loop
                else:
                    print("Reply with 'y' to push or 'n' to cancel.")
        except Exception as e:
            raise Exception(f"Error creating commit: {e}")
