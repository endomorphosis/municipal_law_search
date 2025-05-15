from pathlib import Path

def make_init_file(output_dir: Path) -> None:
    """Create __init__.py to make it a proper Python package"""

    init_file_path = output_dir / "__init__.py"

    if not init_file_path.exists():
        init_file_path.touch()
