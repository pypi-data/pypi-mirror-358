import json
import subprocess


class GitUtils:
    """Utilities for interacting with Git repositories."""

    @staticmethod
    def is_git_repo() -> bool:
        """Checks if the current directory is a Git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"], capture_output=True, check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_staged_diff() -> str:
        """Gets the diff of staged files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error getting staged diff: {e}")

    @staticmethod
    def get_all_diff() -> str:
        """Gets the diff of all changes (staged and unstaged)."""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error getting all diff: {e}")

    @staticmethod
    def has_staged_changes() -> bool:
        """Checks if there are staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"], capture_output=True
            )
            return result.returncode != 0
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def has_unstaged_changes() -> bool:
        """Checks if there are unstaged changes."""
        try:
            result = subprocess.run(["git", "diff", "--quiet"], capture_output=True)
            return result.returncode != 0
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def stage_all_changes():
        """Adds all changes to the staging area."""
        try:
            subprocess.run(["git", "add", "-A"], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error staging changes: {e}")

    @staticmethod
    def commit_with_message(message: json):
        """Commits changes with the given message."""
        try:
            subprocess.run(
                ["git", "commit", "-m", message["title"], "-m", message["description"]],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error committing changes: {e}")

    @staticmethod
    def push_changes():
        """Pushes the committed changes to the remote repository."""
        try:
            print("Attempting to push changes...")
            # Detect the current branch to push
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = branch_result.stdout.strip()

            # Detect the remote to push to (e.g., origin)
            remote_result = subprocess.run(
                ["git", "remote"],
                capture_output=True,
                text=True,
                check=True,
            )
            remote = (
                remote_result.stdout.splitlines()[0].strip()
                if remote_result.stdout.strip()
                else "origin"
            )  # Default to 'origin' if no remotes found

            subprocess.run(["git", "push", remote, current_branch], check=True)
            print("✅ Push successful!")
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Error pushing changes: {e}\nPlease check your remote configuration and permissions."
            )
        except Exception as e:
            raise Exception(f"An unexpected error occurred during push: {e}")
