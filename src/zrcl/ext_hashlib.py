import hashlib
import os
from zrcl.ext_re import should_include


def hash_file(path: str, algorithm: str = "sha256", chunk_size: int = 65536, normalize_newline: bool = True) -> str:
    """
    Computes the hash value of a file.

    Args:
        path (str): The path to the file.
        algorithm (str): The hashing algorithm to use. Defaults to "sha256".
        chunk_size (int): The size of the chunks used to read the file. Defaults to 65536.

    Returns:
        str: The computed hash value of the file.
    """
    hasher = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            if normalize_newline:
                chunk = chunk.replace(b"\r\n", b"\n")
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_bytes(data: bytes, algorithm: str = "sha256", normalize_newline: bool = True) -> str:
    """
    Computes the hash value of a given byte string using the specified algorithm.

    Args:
        data (bytes): The byte string to be hashed.
        algorithm (str, optional): The hashing algorithm to use. Defaults to "sha256".

    Returns:
        str: The computed hash value of the byte string in hexadecimal format.
    """
    if normalize_newline:
        data = data.replace(b"\r\n", b"\n")
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def hash_folder(
    path: str,
    algorithm: str = "sha256",
    chunk_size: int = 65536,
    include_file_masks: list = [],
    exclude_file_masks: list = [],
    normalize_newline: bool = True,
) -> str:
    """
    Computes the hash value of all the files in a folder using the specified algorithm.

    Args:
        path (str): The path to the folder.
        algorithm (str): The hashing algorithm to use. Defaults to "sha256".
        chunk_size (int): The size of the chunks used to read the files. Defaults to 65536.
        include_file_masks (list): A list of file masks to include. Defaults to an empty list.
        exclude_file_masks (list): A list of file masks to exclude. Defaults to an empty list.
        normalize_newline (bool): Whether to normalize newline characters. Defaults to True.
    Returns:
        str: The computed hash value of all the files in the folder.
    """
    hasher = hashlib.new(algorithm)
    for root, dirs, files in os.walk(path):
        for file in files:
            if not should_include(file, include_file_masks, exclude_file_masks):
                continue
            with open(os.path.join(root, file), "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    if normalize_newline:
                        chunk = chunk.replace(b"\r\n", b"\n")
                    hasher.update(chunk)
    return hasher.hexdigest()


def hash_python_directory(
    directory: str, algorithm: str = "sha256", chunk_size: int = 65536, normalize_newline: bool = True
) -> str:
    """
    Computes the hash value of all files in a given directory, skipping '__pycache__'
    directories and non-Python files.

    Args:
        directory (str): The directory to be hashed.
        algorithm (str, optional): The hashing algorithm to use. Defaults to 'sha256'.
        chunk_size (int): The size of the chunks used to read the files. Defaults to 65536.

    Returns:
        str: The computed hash value of the directory contents in hexadecimal format.
    """
    hasher = hashlib.new(algorithm)
    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs if d != "__pycache__"
        ]  # Skip '__pycache__' directories
        for file in files:
            if not file.endswith(".py"):
                continue  # Only hash Python files
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    if normalize_newline:
                        chunk = chunk.replace(b"\r\n", b"\n")
                    hasher.update(chunk)
    return hasher.hexdigest()
