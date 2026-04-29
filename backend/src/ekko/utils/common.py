"""Shared utility functions.

This module provides framework-independent helpers. It MUST NOT import from
any other Ekko layer (core, application, infrastructure, presentation, config).
"""

from pathlib import Path


def _validate_file_path(dir_path: Path, filename: str, suffix: str) -> Path:
    """Validate and return a path to a file.

    Args:
        dir_path: Directory to look in.
        filename: Name of the file.
        suffix: Required file extension (e.g. ".txt").

    Returns:
        Resolved path to the validated file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension does not match *suffix*.
    """
    path = dir_path / filename
    if not path.is_file():
        raise FileNotFoundError(f"File '{filename}' not found in '{dir_path!s}'.")
    if path.suffix != suffix:
        raise ValueError(f"File '{filename}' must have a '{suffix}' extension.")
    return path


def load_prompt(filename: str, *, prompt_dir: Path) -> str:
    """Load a prompt text file from the given prompts directory.

    Args:
        filename: Name of the prompt file (must end in .txt).
        prompt_dir: Directory containing prompt files.

    Returns:
        Contents of the prompt file as a string.

    Raises:
        FileNotFoundError: If the file does not exist in *prompt_dir*.
        ValueError: If the file does not have a .txt extension.
    """
    prompt_path = _validate_file_path(prompt_dir, filename, ".txt")
    return prompt_path.read_text(encoding="utf8")
