from pathlib import Path
from typing import List, Union
from enum import Enum


ScanDepthEnum = Enum("ScanDepth", {
    "current": "current",
    "upto3": "upto3",
    "all": "all"
})


def scan_envyro_files(directory: Union[str, Path] = None, depth: ScanDepthEnum = ScanDepthEnum.current) -> List[Path]:
    """
    Scan for .envyro files based on folder traversal depth.

    Args:
        directory (str | Path, optional): Directory to scan. Defaults to current working directory.
        depth (ScanDepth): One of 'current', 'upto3', or 'all'.

    Returns:
        List[Path]: List of paths to .envyro files.
    """
    base_dir = Path(directory) if directory else Path.cwd()
    envyro_files = []

    if depth == ScanDepthEnum.upto3:
        # Collect only directory paths up to 3 levels deep (non-recursive beyond level 3)
        dirs_to_check = [base_dir]

        for level in range(3):
            new_dirs = []
            for d in dirs_to_check:
                subdirs = [p for p in d.iterdir() if p.is_dir()]
                new_dirs.extend(subdirs)
            dirs_to_check.extend(new_dirs)

        # Scan each of the collected directories
        for d in set(dirs_to_check):
            envyro_files.extend(d.glob("*.envyro"))

    elif depth == ScanDepthEnum.all:
        # Fully recursive through all directories
        for d in base_dir.rglob("*"):
            if d.is_dir():
                envyro_files.extend(d.glob("*.envyro"))

    else:
        # Only scan the current directory
        envyro_files = list(base_dir.glob("*.envyro"))

    return envyro_files
