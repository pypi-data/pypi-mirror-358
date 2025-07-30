# System prompts
OPENAI_SYSTEM_PROMPT = """You are an expert in Git who creates concise and descriptive commit titles and descriptions following best practices."""
GOOGLE_SYSTEM_PROMPT = """You are an expert in Git who creates concise and descriptive commit titles and descriptions following best practices."""

# Base prompt
BASE_COMMIT_PROMPT = """Based on the following code changes, generate a concise and descriptive commit title and description.
The message should follow conventional commit format. changes:

{diff_content}

Generate only the commit title and message, without additional explanations, and return them as a JSON object."""
