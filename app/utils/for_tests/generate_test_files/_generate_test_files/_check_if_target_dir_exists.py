from pathlib import Path


def check_if_target_dir_exists(target_dir: Path) -> None:
    """
    Validate the target directory and ensure it exists and is a directory.

    Args:
        target_dir (Path): The target directory to validate.

    Raises:
        FileNotFoundError: If the target directory does not exist.
        NotADirectoryError: If the target directory is not a directory.
    """

    if not target_dir.exists():
        raise FileNotFoundError(f"Target directory '{target_dir}' does not exist.")

    if not target_dir.is_dir():
        raise NotADirectoryError(f"'{target_dir}' is not a directory.")
