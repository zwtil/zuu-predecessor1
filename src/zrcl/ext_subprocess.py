import subprocess
from typing import TypedDict
import typing
import platform


def open_detached(path: str, *args) -> None:
    """
    Opens a new process in a detached state.

    Args:
        path (str): The path to the executable file.
        *args: Additional arguments to be passed to the executable.

    Returns:
        None: This function does not return anything.

    Description:
        This function uses the `subprocess.Popen` method to create a new process
        and execute the specified executable file with the given arguments. The
        process is created in a detached state, meaning it runs independently
        of the parent process. The standard input, output, and error streams of
        the process are set to be pipes. The `creationflags` parameter is used
        to specify the creation flags for the process, including `DETACHED_PROCESS`,
        `CREATE_NEW_PROCESS_GROUP`, and `CREATE_BREAKAWAY_FROM_JOB`.

    Example:
        ```python
        open_detached("path/to/executable", "arg1", "arg2")
        ```
    """
    subprocess.Popen(
        [path, *(str(arg) for arg in args)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=(
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_BREAKAWAY_FROM_JOB
        ),
    )


class queryCtx(TypedDict):
    """
    A dictionary containing additional context for processing the subprocess output.

    Attributes:
        decode (str, optional): The name of the encoding used to decode the output of the subprocess.
        decodeOrder (List[str], optional): A list of encodings to try when decoding the output of the subprocess.
        toList (bool, optional): Whether to split the output of the subprocess into a list of lines.
        stripNull (bool, optional): Whether to remove null characters from the output of the subprocess.
        stripEmpty (bool, optional): Whether to remove empty lines from the output of the subprocess.
    """

    decode: typing.NotRequired[str]
    decodeOrder: typing.NotRequired[typing.List[str]]
    toList: typing.NotRequired[bool]
    stripNull: typing.NotRequired[bool]
    stripEmpty: typing.NotRequired[bool]


def query(path: str, *args, timeout: int = 5, ctx: queryCtx = None) -> bytes:
    """
    Runs a subprocess with the given path and arguments, captures its output, and returns it as a byte string.

    Args:
        path (str): The path to the executable file.
        *args: Additional arguments to be passed to the executable.
        timeout (int, optional): The maximum amount of time to wait for the subprocess to complete. Defaults to 5.
        ctx (queryCtx, optional): Additional context for processing the subprocess output. Defaults to None.

    Returns:
        bytes: The output of the subprocess as a byte string.

    Raises:
        subprocess.TimeoutExpired: If the subprocess takes longer than the specified timeout to complete.
        subprocess.CalledProcessError: If the subprocess returns a non-zero exit status.

    Example:
        >>> query("path/to/executable", "arg1", "arg2")
        b'output of the subprocess'
    """

    try:
        command = [path, *(str(arg) for arg in args)]
        proc = subprocess.run(command, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise e
    except subprocess.CalledProcessError as e:
        raise e

    if ctx is None:
        return proc.stdout

    if "decode" in ctx:
        decoded = proc.stdout.decode(ctx["decode"])
    elif "decodeOrder" in ctx:
        for decode in ctx["decodeOrder"]:
            try:
                decoded = proc.stdout.decode(decode)
                break
            except UnicodeDecodeError:
                pass

    if "toList" in ctx and ctx["toList"]:
        decodedList = decoded.split("\n")
    else:
        return decoded

    if "stripNull" in ctx and ctx["stripNull"]:
        decodedList = list(filter(lambda x: x != "", decodedList))

    if "stripEmpty" in ctx and ctx["stripEmpty"]:
        blist = decodedList
        decodedList = []
        for b in blist:
            if b not in [" ", "\t", "\n", "\r", "\x00", "\r\n", ""]:
                decodedList.append(b.strip())

    return decodedList


def check_is_installed(app_name: str) -> bool:
    """
    Check if an application is installed on the operating system.

    Args:
        app_name (str): The name of the application to check.

    Returns:
        bool: True if the application is installed, False otherwise.

    This function checks if an application is installed on the operating system by using the appropriate command for the operating system.

    On Windows, it uses the 'where' command to check for the app existence.

    On macOS, it uses the 'type' command or 'which' command to check for the app existence.

    On Linux, it uses the 'which' command to check for the app existence.

    If the command succeeds, the application is considered installed and the function returns True.

    If the command fails, the application is considered not installed and the function returns False.

    If the operating system is not Windows, macOS, or Linux, the function returns False.
    """

    os_type = platform.system()

    try:
        if os_type == "Windows":
            # On Windows, use 'where' command to check for the app existence
            subprocess.check_call(
                ["where", app_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif os_type == "Darwin":
            # On macOS, use 'type' command or 'which'
            subprocess.check_call(
                ["type", app_name],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif os_type == "Linux":
            # On Linux, use 'which' command
            subprocess.check_call(
                ["which", app_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            return False
    except subprocess.CalledProcessError:
        # The command failed, the application is not installed
        return False

    # The command succeeded, the application is installed
    return True
