from contextlib import contextmanager
import logging
from zrcl.beta_desktop_automation.feature_cropper import FeatureCropper
import time


def waitFor(token: FeatureCropper, timeout: float = 10.0, interval: float = 1.1):
    """
    Wait for a given token function to return a truthy value or until the specified timeout is reached.

    Args:
        token (FeatureCropper): The token function to be called.
        timeout (float, optional): The maximum amount of time to wait for the token function to return a truthy value. Defaults to 10.0.
        interval (float, optional): The time interval between each call to the token function. Defaults to 1.1.

    Returns:
        The last result of calling the token function.

    Raises:
        TimeoutError: If the token function does not return a truthy value within the specified timeout.

    Note:
        The token function should return a truthy value to indicate success or a falsy value to indicate failure.
        If the token function raises an exception, it will be logged and the function will continue to wait.
    """
    currentTime = time.time()
    while time.time() - currentTime < timeout:
        try:
            if token():
                break
        except Exception as e:
            logging.error(e)

        time.sleep(interval)

    if not token._lastResult:
        raise TimeoutError("Timed out")
    return token._lastResult


@contextmanager
def repeatWith(token: FeatureCropper, times: int = 1):
    """
    A context manager that repeatedly yields the result of calling the given token function.

    Args:
        token (FeatureCropper): The token function to be called.
        times (int, optional): The number of times the token function should be called. Defaults to 1.

    Yields:
        The result of calling the token function.

    Returns:
        The last result of calling the token function.
    """
    for _ in range(times):
        yield token()
    return token._lastResult
