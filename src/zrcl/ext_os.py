import os
import stat


def has_hidden_attribute(filepath):
    """
    Check if a file has the hidden attribute.

    Parameters:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file has the hidden attribute, False otherwise.
    """
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
