from pathlib import Path


def get_hashes_from_hashes_csv(dir: Path) -> list[str]:
    """
    Reads hashes from a CSV file in the specified directory.

    This function reads a file named 'hashes.csv' from the given directory,
    extracts each line, and returns a list of hashes with whitespace stripped.

    Args:
        dir (Path): The directory containing the 'hashes.csv' file.

    Returns:
        list[str]: A list of hash strings with whitespace stripped.

    Example:
        >>> get_hashes_from_hashes_csv(Path("/path/to/directory"))
        ['hash1', 'hash2', 'hash3']
    """
    dir = dir / "hashes.csv"
    with open(dir, "r") as f:
        hashes = f.readlines()
    return [hash.strip() for hash in hashes]
