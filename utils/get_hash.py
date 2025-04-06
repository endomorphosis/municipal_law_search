from functools import partial
import hashlib
from pathlib import Path
from typing import Any, BinaryIO, overload


def get_hash(string: str) -> str:
    """
    Generate a SHA-256 hash for a given string.
    
    Args:
        string (str): The string to hash
        
    Returns:
        str: The hexadecimal digest of the SHA-256 hash
    """
    return hashlib.sha256(string.encode()).hexdigest()

def hash_string(hashable: str) -> str:
    """
    Generate a SHA-256 hash for a string.
    
    Args:
        hashable (str): The string to hash
        
    Returns:
        str: The hexadecimal digest of the SHA-256 hash
        
    Note:
        This is a convenience wrapper around get_hash
    """
    return get_hash(hashable)

def hash_set(hashable: set, hash_elements = True) -> str|set[str]:
    """
    Generate a hash for a set.
    
    Args:
        hashable (set): The set to hash
        hash_elements (bool, optional): If True, hash each element of the set.
            If False, hash the string representation of the entire set. Defaults to True.
            
    Returns:
        str|set[str]: If hash_elements is True, returns a set of hashes for each element.
            Otherwise, returns a single hash for the entire set.
    """
    return hash_list(list(hashable), hash_elements)

def hash_list(hashable: list, hash_elements = True) -> str|list[str]:
    """
    Generate a hash for a list.
    
    Args:
        hashable (list): The list to hash
        hash_elements (bool, optional): If True, hash each element of the list.
            If False, hash the string representation of the entire list. Defaults to True.
            
    Returns:
        str|list[str]: If hash_elements is True, returns a list of hashes for each element.
            Otherwise, returns a single hash for the entire list.
    """
    if hash_elements:
        return [GetHash.make_hash(element) for element in hashable]
    else:
        return get_hash(str(hashable))

def hash_file_path(hashable: Path) -> str:
    """
    Generate a hash for a file path.
    
    Args:
        hashable (Path): The file path to hash
        
    Returns:
        str: A hash of the string representation of the path
    """
    return get_hash(str(hashable))

def hash_file(hashable: Path, chunk_size = 8192) -> str:
    """
    Generate a hash for a file's contents by reading it in chunks.
    
    Args:
        hashable (Path): The path to the file to hash
        chunk_size (int, optional): The size of chunks to read the file in. Defaults to 8192.
        
    Returns:
        str: The hexadecimal digest of the SHA-256 hash of the file's contents
    """
    sha256 = hashlib.sha256()
    with hashable.open("rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def hash_file_name(hashable: Path, hash_extension_too: bool = False) -> str:
    """
    Generate a hash for a file name.
    
    Args:
        hashable (Path): The path containing the filename to hash
        hash_extension_too (bool, optional): If True, include the file extension in the hash.
            If False, only hash the stem of the filename. Defaults to False.
            
    Returns:
        str: A hash of the filename
    """
    of_file_name = hashable.name if hash_extension_too else hashable.stem
    return get_hash(of_file_name)

def hash_file_directory(
        hashable: Path, 
        recursive: bool = False, 
        hash: str = "files_names_and_directories"
    ) -> str:
    """
    Generate a hash for the contents of a directory.
    
    Args:
        hashable (Path): The directory path to hash
        recursive (bool, optional): If True, include subdirectories recursively.
            If False, only include top-level files and directories. Defaults to False.
        hash (str, optional): What to include in the hash. Options are:
            - "files_names_and_directories": Hash both files and directory names (default)
            - "file_names": Hash only file names
            - "directories": Hash only directory names
            
    Returns:
        str: A hash or list of hashes depending on the content
        
    Raises:
        ValueError: If hash is not one of the allowed values
    """

    if hash not in ["directories", "file_names", "files_names_and_directories"]:
        raise ValueError("hash must be 'directories', 'files', or 'files_and_directories'")

    file_finder = partial(hashable.rglob, "*") if recursive else hashable.iterdir

    match hash:
        case "file_names":
            things_to_hash = [file for file in file_finder() if file.is_file()]
        case "files_names_and_directories":
            things_to_hash = [file for file in file_finder()]
        case "directories":
            things_to_hash = [file for file in file_finder() if file.is_dir()]
        case _:
            raise ValueError("hash must be one of 'whole_directory', 'files', or 'files_and_directories'")
    return hash_list(things_to_hash)

def hash_dict(hashable: dict, hash_keys: bool = True, hash_values: bool = True) -> str|dict[str, str]:
    """
    Generate hashes for a dictionary, either for its keys, values, or both.
    
    Args:
        hashable (dict): The dictionary to hash
        hash_keys (bool, optional): Whether to hash the keys. Defaults to True.
        hash_values (bool, optional): Whether to hash the values. Defaults to True.
        
    Returns:
        str|dict[str, str]: A dictionary with hashed keys, values, or both, depending on
            the hash_keys and hash_values parameters.
            
    Raises:
        ValueError: If both hash_keys and hash_values are False
    """
    if hash_keys and hash_values:
        return {GetHash.make_hash(key): GetHash.make_hash(value) for key, value in hashable.items()}
    elif hash_keys:
        return {GetHash.make_hash(key): value for key, value in hashable.items()}
    elif hash_values:
        return {key: GetHash.make_hash(value) for key, value in hashable.items()}
    else:
        raise ValueError("hash_keys and hash_values cannot both be False")

def hash_bytes(hashable: bytes) -> str:
    """
    Generate a SHA-256 hash for a bytes object.
    
    Args:
        hashable (bytes): The bytes object to hash
        
    Returns:
        str: The hexadecimal digest of the SHA-256 hash
    """
    return hashlib.sha256(hashable).hexdigest()

def hash_tuple(hashable: tuple) -> str:
    """
    Generate a hash for a tuple by hashing each element.
    
    Args:
        hashable (tuple): The tuple to hash
        
    Returns:
        str: A list of hashes, one for each element in the tuple
    """
    return hash_list(list(hashable), hash_elements=True)

_HASH_FUNCTION_DICT = {
    str: hash_string,
    Path: {
        "hash_file_name": hash_file_name,
        "hash_file_path": hash_file_path,
        "hash_file": hash_file,
        "hash_file_directory": hash_file_directory,
    },
    bytes: hash_bytes,
    dict: hash_dict,
    list: hash_list,
    set: hash_set,
    frozenset: hash_set,
    tuple: hash_tuple,
    'np.ndarray': lambda x: get_hash(x.tobytes()),
    'pd.DataFrame': lambda x: get_hash(x.to_csv()),
}


class GetHash:
    """
    Make a Sha256 hash of something
    """
    try: # See if we got numpy and pandas
        import numpy as np
        import pandas as pd
    except ImportError:
        # If numpy and pandas aren't installed, 
        # the user probably wasn't going to hash things from them anyway.
        pass

    @overload
    @staticmethod # Hash a string
    def hash(hashable: str) -> str:...

    @overload
    @staticmethod # Hash a file path
    def hash(hashable: Path) -> str:...

    @overload
    @staticmethod # Hash a filename
    def hash(hashable: Path, hash_extension_too: bool = False) -> str:...

    @overload
    @staticmethod # Hash a file
    def hash(hashable: Path, chunk_size: int = 8192) -> str:...

    @overload
    @staticmethod # Hash a file directory
    def hash(hashable: Path, recursive: bool = False, hash: str = "file_names_and_directories") -> str:...

    @overload
    @staticmethod # Hash a binary string
    def hash(hashable: bytes) -> str:...

    @overload
    @staticmethod # Hash a dictionary
    def hash(hashable: dict, hash_keys: bool = False, hash_values: bool = True) -> str:...

    @overload
    @staticmethod # Hash a list of hashables
    def hash(hashable: list, hash_elements: bool = True) -> str|list[str]:...

    @overload
    @staticmethod # Hash a set of hashables
    def hash(hashable: set, hash_elements: bool = True) -> str|list[str]:...

    @overload
    @staticmethod # Hash a binary stream
    def hash(hashable: BinaryIO) -> str:...

    @overload
    @staticmethod # Hash a set
    def hash(hashable: BinaryIO) -> str:...

    @overload
    @staticmethod # Hash a tuple
    def hash(hashable: tuple, hash_elements: bool = True) -> str|list[str]:...

    @overload
    @staticmethod # Hash a dataframe
    def hash(hashable: pd.DataFrame) -> str:...

    @overload
    @staticmethod # Hash a numpy array
    def hash(hashable: np.ndarray) -> str:...

    @staticmethod
    def make_hash(hashable, **kwargs) -> str:
        """
        Hash a hashable object.
        """
        hash_func = None
        if hashable is None:
            print("hashable is None and thus cannot be hashed. Returning None.")
            return None

        # Coerce input to string if it is an int, float, or bool
        if isinstance(hashable, (int, float, bool)):
            hashable = str(hashable)

        try:
            hash_func = _HASH_FUNCTION_DICT.get(type(hashable))
        except KeyError:
            print(f"No hash function found for type: {type(hashable)}. Returning None.")
            return None

        if isinstance(hash_func, dict): # Multiple hash functions for the same type
            if isinstance(hashable, Path):
                if "hash_extension_too" in kwargs:
                    hash_func = _HASH_FUNCTION_DICT.get(type(hashable))["hash_file_name"]
                elif "chunk_size" in kwargs:
                    hash_func = _HASH_FUNCTION_DICT.get(type(hashable))["hash_file"]
                elif "recursive" in kwargs:
                    hash_func = _HASH_FUNCTION_DICT.get(type(hashable))["hash_file_directory"]
                else:
                    hash_func = _HASH_FUNCTION_DICT.get(type(hashable))["hash_file_path"]
        try:
             # Execute the hash function
            return hash_func(hashable, **kwargs)
        except Exception as e:
            print(f"Error hashing {hashable}: {e}")
            return None
