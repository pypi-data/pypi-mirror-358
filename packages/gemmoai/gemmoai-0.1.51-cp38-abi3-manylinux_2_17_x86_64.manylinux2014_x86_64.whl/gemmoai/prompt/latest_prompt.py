import importlib
import os
from typing import Tuple


def get_latest_prompt_version(
    prompt_type: str, prompt_directory: str = "prompts"
) -> Tuple[str, str]:
    """Get the latest version of user and system prompts for a given prompt type.

    Args:
        prompt_type (str): The type of prompt to load (e.g. 'classification', 'extraction')
        prompt_directory (str, optional): Directory containing prompt version folders. Defaults to "prompts".

    Returns:
        Tuple[str, str]: A tuple containing (user_prompt, system_prompt). Either value may be None if not defined.

    The prompt directory should contain version folders named with numbers (e.g. "1", "2").
    Each version folder should contain prompt modules named after the prompt_type.
    The prompts are expected to define 'user' and/or 'system' variables containing the prompt text.
    """

    # Get all version folders and select the latest one based on numeric sorting
    prompt_versions = os.listdir(prompt_directory)
    prompt_version = sorted(prompt_versions, key=lambda x: float(x))[-1]

    # Import the prompt module for the specified type from the latest version
    prompt = importlib.import_module(f"{prompt_directory}.{prompt_version}.{prompt_type}")

    # Extract user and system prompts if defined, otherwise return None
    user_prompt = getattr(prompt, "user", None)
    system_prompt = getattr(prompt, "system", None)

    return user_prompt, system_prompt
