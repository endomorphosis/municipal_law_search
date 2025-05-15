from pathlib import Path

def get_all_python_files_in(target_dir: Path) -> list[Path]:
    """
    Get all Python files in the target directory and its subdirectories.

    Args:
        target_dir (Path): The target directory to search for Python files.

    Returns:
        list[Path]: A list of paths to all Python files found in the target directory.
    """
    python_files = []
    these_prefixes = ("test_", "__",)
    these_suffixes = ("_test.py", "test_.py", "__.py")

    for root, _, files in target_dir.walk():
        for file in files:
            if file.startswith(these_prefixes) or file.endswith(these_suffixes):
                continue
            if file.endswith(".py"):
                python_files.append(Path(root) / file)
    return python_files
