from pathlib import Path


from logger import utils_logger


def clear_hashes_csv(dir: Path) -> None:
    """
    Clear the contents of the 'hashes.csv' file in the specified directory.
    If the file doesn't exist, it creates a new empty file.

    Args:
        dir (Path): The directory path where the 'hashes.csv' file is located.

    Raises:
        No exceptions are raised directly, but any exceptions during file operations
        are caught and logged.
    """
    file_path = dir / "hashes.csv"

    if not file_path.exists():
        utils_logger.debug(f"File {file_path} does not exist, creating a new empty file.")
    try:
        with open(file_path, "w") as f:
            f.write("")
        utils_logger.debug(f"Cleared {file_path}")
    except Exception as e:
        utils_logger.debug(f"Error clearing {file_path}: {e}")

