from pathlib import Path


from configs import configs
from logger import utils_logger


def make_dir_if_it_doesnt_exist(dir_path: Path) -> None:
    """
    Creates a directory if it doesn't exist.

    This function checks if the specified directory path exists and creates it if it doesn't.
    It also validates that the directory is within the program's root directory for security.

    Args:
        dir_path (Path): The path of the directory to create.

    Raises:
        ValueError: If the directory path is not within the program's root directory
                    or is not the root directory itself.

    Returns:
        None

    Example:
        >>> make_dir_if_it_doesnt_exist(Path('/path/to/directory'))
        # Creates the directory if it doesn't exist
    """
    # Validate that the directory path is within program folder or is not the program folder itself
    if configs.paths.ROOT_DIR not in dir_path.parents and configs.paths.ROOT_DIR  != dir_path:
        raise ValueError(f"Can't make new folders that aren't in {configs.paths.ROOT_DIR}")
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
        utils_logger.info(f"Directory created: {dir_path}")
    else:
        utils_logger.info(f"Directory already exists: {dir_path}")


