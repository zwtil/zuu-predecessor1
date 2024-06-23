import typing
import py7zr


def crack_password(
    path: str,
    passwordStream: typing.Generator[str, None, None],
    maxAttempts: int = 1000,
    dedup: typing.Callable[[str], bool] = None,
):
    """
    Cracks the password of a given zip file using a generator of passwords.

    Args:
        path (str): The path to the zip file.
        passwordStream (typing.Generator[str, None, None]): A generator of passwords to try.
        maxAttempts (int, optional): The maximum number of password attempts to make. Defaults to 1000.
        dedup (typing.Callable[[str], bool], optional): A function to deduplicate passwords. Defaults to None.

    Returns:
        str: The correct password if found, otherwise None.

    Raises:
        Any exception that is not related to LZMA errors.

    This function attempts to open the zip file with each password in the passwordStream. If no exception is raised,
    it means that the password is correct and the function returns it. If the file is bad or the password is incorrect,
    the function continues with the next password. If the number of attempts exceeds maxAttempts, the function stops.
    If dedup is not None, it is used to deduplicate passwords. If dedup is None, a set of passwords is used to deduplicate.
    """
    if dedup is None:
        dedupset = set()

    for i, password in enumerate(passwordStream):
        if i > maxAttempts:
            break
        try:
            # Attempt to open the archive with the current password
            with py7zr.SevenZipFile(path, mode="r", password=password) as archive:
                archive.files
                return password  # Password is correct if no exception was raised
        except py7zr.Bad7zFile:
            # Continue with the next password if the file is bad or wrong password
            pass
        except Exception as e:
            # Raise exception if it's not related to LZMA errors
            if "_lzma.LZMAError" not in str(type(e)):
                raise e

        if dedup is not None and dedup(password):
            continue
        elif dedup is None and password in dedupset:
            continue
        if not dedup:
            dedupset.add(password)
