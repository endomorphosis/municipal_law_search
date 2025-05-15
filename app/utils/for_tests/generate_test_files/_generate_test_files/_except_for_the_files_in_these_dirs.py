from pathlib import Path
from typing import Optional


def except_for_the_files_in_these_dirs(
        python_files_paths: list[Path], 
        ignore_dir_list: Optional[list[Path]] = []
        ) -> list[Path]:
    """
    Exclude files in the specified directories from the list of Python files.

    Args:
        python_files_paths (list[Path]): List of paths to Python files.
        ignore_dir_list (list[Path]): List of directories to ignore.

    Returns:
        list[Path]: Filtered list of Python file paths.
    """
    if not ignore_dir_list:
        return python_files_paths

    # Resolve all ignore directories to absolute paths
    resolved_ignore_dirs = [dir_path.resolve() for dir_path in ignore_dir_list]

    filtered_files = []
    for file_path in python_files_paths:
        resolved_path = file_path.resolve()
        # Check if this file is in any of the ignored directories
        if not any(str(resolved_path).startswith(str(ignore_dir)) for ignore_dir in resolved_ignore_dirs):
            filtered_files.append(file_path)

    return filtered_files
