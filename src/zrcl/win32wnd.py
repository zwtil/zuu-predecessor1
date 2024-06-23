import pygetwindow as gw
import win32process


def get_pid_from_hwnd(hwnd):
    """Get the process ID given the handle of a window."""
    if not isinstance(hwnd, int):
        assert isinstance(hwnd, gw.Win32Window)
        hwnd = hwnd._hWnd

    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception as e:
        print(f"Error: {e}")
        return None
