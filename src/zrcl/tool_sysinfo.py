import platform
import psutil


def run():
    # sysinfo
    # Operating System Information
    print("Operating System:", platform.system())
    print("OS Version:", platform.version())
    print("OS Release:", platform.release())

    # CPU Information
    print("CPU Cores:", psutil.cpu_count(logical=False))
    print("Total CPU Threads:", psutil.cpu_count(logical=True))

    # Memory Information
    memory = psutil.virtual_memory()
    print("Total Memory:", memory.total)
    print("Available Memory:", memory.available)
