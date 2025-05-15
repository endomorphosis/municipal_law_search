from pathlib import Path

def make_output_dir(output_dir: Path) -> None:
    """
    Initialize the output directory for test files.

    Args:
        output_dir (Path): The output directory path to initialize.

    This function:
    1. Creates the output directory if it doesn't exist
    2. Creates an empty __init__.py file to make it a proper Python package
    """
    # Create output directory if it doesn't exist
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
