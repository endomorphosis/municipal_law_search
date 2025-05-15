from pathlib import Path


from logger import logger


def write_test_file(test_file_path: Path, content: str) -> bool:
    """
    Write the test content to the test file.

    Args:
        test_file_path (Path): Path to the test file.
        content (str): Content to write to the file.

    Returns:
        bool: True if the file was written successfully, False otherwise.
    """
    try:
        # Ensure the directory exists
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the content to the file
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        logger.error(f"Failed to write test file: {e}")
        return False
