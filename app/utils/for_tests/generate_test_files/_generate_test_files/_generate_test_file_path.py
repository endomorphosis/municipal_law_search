from pathlib import Path


def generate_test_file_path(source_file_path: Path, output_dir: Path) -> Path:
    """
    Generate the path for the test file based on the source file path.

    Args:
        source_file_path (Path): Path to the source Python file.
        output_dir (Path): Directory where the test file should be created.

    Returns:
        Path: Path to the test file.
    """
    # Get the relative directory structure from the source file
    relative_dir = source_file_path.parent.name

    # Construct the output subdirectory path
    test_subdir = output_dir / relative_dir if relative_dir != "." else output_dir

    # Create subdirectories in the output directory to mirror the structure of the target directory
    if not test_subdir.exists():
        test_subdir.mkdir(parents=True, exist_ok=True)

    # Construct the full test file path using the output directory
    # Create test filename by prepending "test_" to the original filename
    test_file_path = test_subdir / f"test_{source_file_path.name}"

    return test_file_path.resolve()
