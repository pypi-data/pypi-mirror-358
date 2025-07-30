import re
import typer
from pathlib import Path
from typing import List, Dict, Set, TypedDict
from dotenv import dotenv_values


class DictComparisonResult(TypedDict):
    """Type for dictionary comparison results"""
    present: Set[str]    # Keys present in both dictionaries
    missing: Set[str]    # Keys in dict2 that are missing from dict1
    extra: Set[str]      # Keys in dict1 that are not in dict2


def compare_env_dicts(dict1: Dict[str, str], dict2: Dict[str, str]) -> DictComparisonResult:
    """
    Compare two dictionaries and return the analysis of keys in context of the first dictionary.

    Args:
        dict1 (Dict[str, str]): The first dictionary (primary context)
        dict2 (Dict[str, str]): The second dictionary to compare against

    Returns:
        DictComparisonResult: A dictionary containing:
            - present: keys that exist in both dictionaries
            - missing: keys from dict2 that are missing in dict1
            - extra: keys in dict1 that don't exist in dict2
    """
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    return {
        "present": keys1 & keys2,          # Intersection - keys in both
        "missing": keys2 - keys1,          # Keys in dict2 but not in dict1
        "extra": keys1 - keys2             # Keys in dict1 but not in dict2
    }


def get_base_dir() -> Path:
    """
    Get the base directory of the project.

    Returns:
        Path: The absolute path to the project's root directory
    """
    current_file = Path(__file__).resolve()
    # Navigate up two levels from utils/get_files.py to reach the project root
    print(f"Current file path: {current_file}")
    print(f"Base directory path: {current_file.parent.parent.parent}")
    return current_file.parent.parent.parent


def get_env_files(directory: str = None) -> List[Path]:
    """
    Find all files containing '.env' in their name in the given directory and its subdirectories.

    Args:
        directory (str, optional): The directory to search in. Defaults to project's base directory if None.

    Returns:
        List[Path]: A list of Path objects for all found .env files
    """
    if directory is None:
        directory = get_base_dir()
    else:
        directory = Path(directory)

    env_files = []

    print(f"Searching for .env files in: {directory}")
    # Walk through all files in directory and subdirectories
    for file_path in directory.rglob("*"):
        if file_path.is_file() and ".env" in file_path.name:
            env_files.append(file_path)

    return env_files


def clean_env_content(content: str) -> str:
    """
    Remove comments and empty lines from environment file content.
    Preserves URLs containing # or // characters.

    Args:
        content (str): Raw content of the environment file

    Returns:
        str: Cleaned content with comments and empty lines removed
    """
    cleaned_lines = []
    for line in content.splitlines():
        # Remove leading/trailing whitespace
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip full-line comments
        if line.startswith('#') or (line.startswith('//') and not line.startswith('http://') and not line.startswith('https://')):
            continue

        # Handle inline comments while preserving URLs
        # First check for any URLs in the line
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, line)

        if urls:
            # Line contains URLs, need to be careful with comment detection
            comment_start = -1

            # Check for comment markers after the last URL
            last_url = urls[-1]
            last_url_end = line.find(last_url) + len(last_url)

            # Look for comments after the last URL
            possible_hash = line.find('#', last_url_end)
            possible_slashes = line.find('//', last_url_end)

            # Find the earliest comment marker that appears after the last URL
            if possible_hash != -1 and possible_slashes != -1:
                comment_start = min(possible_hash, possible_slashes)
            elif possible_hash != -1:
                comment_start = possible_hash
            elif possible_slashes != -1:
                comment_start = possible_slashes

            if comment_start != -1:
                line = line[:comment_start].strip()
        else:
            # No URLs, handle comments normally
            if '//' in line:
                line = line[:line.index('//')].strip()
            if '#' in line:
                line = line[:line.index('#')].strip()

        # Add non-empty lines
        if line:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def get_env_dict(file_path: str) -> dict:
    """
    Loads environment variables from a file using python-dotenv.
    Handles quotes, comments, and escaped characters correctly.
    """
    path = Path(file_path).resolve()

    if not path.exists():
        raise typer.BadParameter(f"File '{file_path}' does not exist")
    if not path.is_file():
        raise typer.BadParameter(f"'{file_path}' is not a file")

    try:
        env_dict = dotenv_values(path)
        return {k: v for k, v in env_dict.items() if v is not None}
    except Exception as e:
        raise typer.BadParameter(f"Failed to parse '{file_path}': {e}")


def get_file_content(file_path: str) -> str:
    """
    Check if a file exists and return its contents if valid.

    Args:
        file_path (str): The path to the file (can be absolute or relative)

    Returns:
        str: The contents of the file if it exists and is readable

    Raises:
        typer.BadParameter: If the file doesn't exist, isn't a file, isn't readable,
                          or isn't a valid text file
    """
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(file_path).resolve()

        # Check if the file exists and is a file (not a directory)
        if not path.exists():
            raise typer.BadParameter(f"File '{file_path}' does not exist")
        if not path.is_file():
            raise typer.BadParameter(f"'{file_path}' is not a file")

        # Try to read the file contents
        try:
            # with path.open('r') as f:
            # content = f.read()
            return get_env_dict(path)
        except UnicodeDecodeError:
            raise typer.BadParameter(f"File '{file_path}' is not a text file")
        except PermissionError:
            raise typer.BadParameter(
                f"Permission denied reading '{file_path}'")

    except Exception as e:
        if isinstance(e, typer.BadParameter):
            raise
        raise typer.BadParameter(
            f"Error processing file '{file_path}': {str(e)}")
