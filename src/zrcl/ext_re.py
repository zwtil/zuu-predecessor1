from functools import lru_cache
import re


@lru_cache()
def compile_pattern(pattern):
    if "*." in pattern:  # Pattern like '*.txt'
        ext = pattern.split("*.")[-1]
        return re.compile(r".*\." + re.escape(ext) + r"$")
    if "*" in pattern:  # Generic wildcard patterns like 'temp_*'
        return re.compile(re.escape(pattern).replace(r"\*", ".*"))
    return re.compile(
        re.escape(pattern) + r"$"
    )  # For exact filename or simple patterns


def should_include(file_name, include_file_masks=[], exclude_file_masks=[]):
    # Compile patterns only once
    includes = [compile_pattern(pattern) for pattern in include_file_masks]
    excludes = [compile_pattern(pattern) for pattern in exclude_file_masks]

    # Check excludes first
    for pattern in excludes:
        if pattern.match(file_name):
            return False

    # If includes is empty, return True unless excluded
    if not includes:
        return True

    # Check includes
    for pattern in includes:
        if pattern.match(file_name):
            return True

    return False
