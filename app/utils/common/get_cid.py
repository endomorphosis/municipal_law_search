import hashlib
import os
from pathlib import Path
import tempfile


from multiformats import CID, multihash


class IpfsMultiformats:
    """
    A class to manage Content Identifiers (CIDs) using multihash and IPFS standards.
    
    This class provides methods to generate CIDs for files and content using the
    IPFS multiformats specification. It implements a three-step process:
    1. Hash the content using SHA-256
    2. Wrap the hash in Multihash format
    3. Generate a CIDv1 using the raw codec and base32 encoding
    """

    def __init__(self):
        """Initialize a new IpfsMultiformats instance."""
        return None

    def get_file_sha256(self, file_path: str) -> bytes:
        """
        Calculate the SHA-256 hash of a file. 
        
        This method reads the file in 8192-byte chunks to handle large files
        without loading everything into memory all at once.

        Args:
            file_path (str): The path to the file to be hashed.

        Returns:
            bytes: The SHA-256 hash of the file content.
        """
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.digest()

    def get_multihash_sha256(self, file_content_hash: bytes) -> bytes:
        """
        Wrap the given SHA-256 hash in Multihash format.
        
        This method uses the 'sha2-256' algorithm identifier for the Multihash format.

        Args:
            file_content_hash (bytes): The SHA-256 hash of the file content.

        Returns:
            bytes: The Multihash-formatted hash.
        """
        return multihash.wrap(file_content_hash, 'sha2-256')

    def get_cid(self, file_data: str | bytes) -> str:
        """
        Generate a Content Identifier (CID) for the given file path or raw data.

        For file paths, it directly calculates the CID. For raw data, it creates a temporary file,
        writes the data to it, calculates the CID, and then removes the temporary file.

        Args:
            file_data (str | bytes): The file path or raw data to generate a CID for.

        Returns:
            str: The generated CID as a string.
            
        Note:
            - For existing files, the CID is calculated directly from the file
            - For string or bytes data, a temporary file is created to calculate the CID
            - The temporary file is always removed after processing
            - CIDs are generated using CIDv1 with base32 encoding and the 'raw' codec
        """
        # If file_data is a valid file path that exists
        if isinstance(file_data, str) and os.path.isfile(file_data):
            print("Making file hash...")
            if os.path.getsize(file_data) > 0:
                file_content_hash = self.get_file_sha256(file_data)
                mh = self.get_multihash_sha256(file_content_hash)
                cid = CID('base32', 1, 'raw', mh)
                return str(cid)
            else:
                print("Empty file. Defaulting to temp file method.")

        # If file_data is raw data or an empty file, use a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            filename = f.name
            with open(filename, 'w') as f_new:
                f_new.write(file_data)

            file_content_hash = self.get_file_sha256(filename)
            mh = self.get_multihash_sha256(file_content_hash)
            cid = CID('base32', 1, 'raw', mh)
        
        # Always clean up the temporary file
        os.remove(filename)

        return str(cid)


# Generate CID for arbitrary string
def _get_cid_for_string(string: str) -> str:
    """
    Generate a Content Identifier (CID) for a given string using SHA-256 hashing and multihash encoding.

    Args:
        string (str): The input string for which the CID is to be generated.

    Returns:
        str: The generated CID in base32 format.

    Note:
        - This function uses the SHA-256 hashing algorithm to hash the input string.
        - The resulting hash is wrapped using the multihash library with the 'sha2-256' code.
        - The CID is constructed using the base32 encoding, version 1, and the 'raw' codec.
    """
    hash = hashlib.sha256(string).digest()
    mh = multihash.wrap(hash, 'sha2-256')
    cid = CID('base32', 1, 'raw', mh)
    return str(cid)


def get_cid(file_data: str | Path | bytes, for_string: bool = False) -> str:
    """
    Generate a Content Identifier (CID) for the given file or string.

    For file paths, it directly calculates the CID. For strings, calculates the CID from a temporary file.

    Args:
        file_data (str | Path | bytes): The file path or string data to generate a CID for.
        for_string (bool): Flag to indicate if the input is an arbitrary string 
            (as opposed to a Path or the string of a path). Defaults to False.

    Returns:
        str: The generated CID as a string.
    """
    if for_string:
        return _get_cid_for_string(file_data)

    if isinstance(file_data, Path):
       file_data = str(file_data)

    ipfs_multiformats = IpfsMultiformats()
    return ipfs_multiformats.get_cid(file_data)
