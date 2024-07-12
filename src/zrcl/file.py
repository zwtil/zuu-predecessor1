from contextlib import contextmanager
from inspect import signature
import os
import tomllib
from zrcl.ext_hashlib import hash_file
from zrcl.ext_json import read_json
import pickle
import toml
import typing


class QuickFileError(Exception):
    pass


def load_toml(path: str):
    return tomllib.load(open(path, "rb"))


def save_toml(path: str, data: dict):
    with open(path, "w") as f:
        toml.dump(data, f)


def load_yaml(path: str):
    import yaml

    return yaml.load(open(path, "r"), Loader=yaml.SafeLoader)


def save_yaml(path: str, data: dict):
    import yaml

    with open(path, "w") as f:
        yaml.dump(data, f)


def load_pickle(path: str):
    return pickle.load(open(path, "rb"))


def save_pickle(path: str, data: dict):
    with open(path, "wb") as f:
        pickle.dump(data, f)


def _extension_read(path: str):
    if "." not in os.path.basename(path):
        raise QuickFileError("Unsupported file type")
    match path.split(".")[-1]:
        case "json":
            return read_json(path)
        case "toml":
            return load_toml(path)
        case "yaml":
            return load_yaml(path)
        case "pickle":
            return load_pickle(path)
        case _:
            raise QuickFileError("Unsupported file type")


def _signature_load(path: str):
    with open(path, "rb") as f:
        # Read the first few bytes to guess the file type
        fsignature = f.read(80)  # Read more bytes to better identify other formats

    # Identify JSON by the starting curly brace
    if fsignature.strip().startswith(b"{"):
        return read_json(path)

    # Identify TOML by the presence of a key=value pair typical in TOML files
    elif b"=" in fsignature and b"[" not in fsignature[: fsignature.find(b"=")].strip():
        return load_toml(path)

    # Identify YAML by typical starting indicators like "---"
    elif fsignature.strip().startswith(b"---"):
        return load_yaml(path)

    # Identify Pickle by checking the pickle magic number
    elif fsignature.startswith(pickle.dumps(pickle.MAGIC_NUMBER)):
        return load_pickle(path)

    else:
        raise QuickFileError("Unsupported file type or unknown signature")


def read_file(path: str, known_ext: str = None):
    """
    Reads a file from the given `path` and returns its contents. If `known_ext` is provided, it will try to read the file based on the extension. If the extension is not supported, a `QuickFileError` will be raised. If `known_ext` is not provided, it will try to guess the file type based on the file signature. If the file type is not supported, a `QuickFileError` will be raised.

    Args:
        path (str): The path to the file.
        known_ext (str, optional): The known extension of the file. Defaults to None.

    Returns:
        The contents of the file.

    Raises:
        QuickFileError: If the file type is not supported.
    """
    if known_ext:
        match known_ext:
            case "json":
                return read_json(path)
            case "toml":
                return load_toml(path)
            case "yaml":
                return load_yaml(path)
            case "pickle":
                return load_pickle(path)
            case _:
                raise QuickFileError("Unsupported file type")

    try:
        return _extension_read(path)
    except QuickFileError:
        return _signature_load(path)
    import os


class FilePropertyMeta:
    types = typing.Literal["mdate", "sha256", "size", "adate"]
    mapping: typing.Dict[types, typing.Callable[[str], typing.Any]] = {
        "mdate": os.path.getmtime,
        "sha256": lambda path: hash_file(path),
        "size": os.path.getsize,
        "adate": os.path.getatime,
    }

    callBackHooks: typing.Dict[str, typing.Callable] = {}

    @staticmethod
    def registerCallbackHook(
        *hooks: typing.Union[str, typing.Callable], callback: typing.Callable = None
    ):
        if callback is None and typing.callable(hooks[-1]):
            callback = hooks[-1]
            hooks = hooks[:-1]

        for hook in hooks:
            FilePropertyMeta.callBackHooks[hook] = callback


class FileProperty:
    """
    Class for handling file properties.

    Example:
        class Config:
            file_path = FileProperty("config.json", customLoad=read_json)

        config = Config()
        print(config.file_path)

    """

    _properties = {}
    _cachedContent = {}

    def __init__(
        self,
        path: typing.Union[property, str],
        watching: typing.List[
            typing.Union[typing.List[FilePropertyMeta.types], FilePropertyMeta.types]
        ] = ["size", ["mdate", "sha256"]],
        customLoad: typing.Callable[[str], typing.Any] = None,
        customWatch: typing.Callable[[str], typing.Any] = None,
        fileCreate: typing.Callable[[str], typing.Any] = lambda path: open(
            path, "w"
        ).close(),
        callbacks: typing.List[typing.Union[str, typing.Callable]] = [],
    ):
        self.watching = watching
        self.path = path
        self.customLoad = customLoad
        self.customWatch = customWatch
        self.callbacks = callbacks

        if fileCreate and not os.path.exists(path):
            fileCreate(path)

    def _needToRefetch(
        self,
        watch: typing.Union[
            typing.List[FilePropertyMeta.types], FilePropertyMeta.types
        ],
        record: typing.Dict,
    ):
        if isinstance(watch, list):
            return any(self._needToRefetch(w, record) for w in watch)

        old_value = record.get(watch)
        new_value = (
            self.customWatch(self.path)
            if watch == "custom"
            else FilePropertyMeta.mapping[watch](self.path)
        )
        if new_value != old_value:
            record[watch] = new_value
            return True
        return False

    def __get__(self, instance, owner):
        path = self.path(instance) if isinstance(self.path, property) else self.path

        if not os.path.exists(path):
            return None

        if path not in self._properties:
            self._properties[path] = {}

        if not self._needToRefetch(self.watching, self._properties[path]):
            return self._cachedContent.get(path)

        content = self.customLoad(path) if self.customLoad else read_file(path)
        self._cachedContent[path] = content

        for callback in self.callbacks:
            resolved_callback = FilePropertyMeta.callBackHooks.get(callback, callback)
            resolved_callback(path, content, self._properties[path])

        return content


# ANCHOR change monitor
class FolderWatcher:
    """
    A class for watching a folder and its subfolders for changes.

    This class allows you to watch a folder and its subfolders for changes to files.
    It provides a mechanism to detect when a file has been created, modified, or deleted.
    """

    def __init__(self, path: str, deep: bool = False, detailed: bool = False):
        self.path = path
        self.deep = deep
        self.detailed = detailed
        self.watched = {}
        self.changed = {}
        self.snapshot()

    def snapshot(self):
        """
        Snapshot the directory and its subdirectories to keep track of file changes.

        This method takes a snapshot of the directory and its subdirectories, storing
        information about each file's modification date, size, and whether it is a directory.
        It uses the `os.walk` function to recursively traverse the directory tree.

        Parameters:
            None

        Returns:
            None

        Raises:
            OSError: If an error occurs while accessing the file system.

        """
        self.watched = {}
        try:
            if self.deep:
                for root, dirs, files in os.walk(self.path):
                    for name in files + dirs:
                        full_path = os.path.join(root, name)
                        is_dir = os.path.isdir(full_path)
                        try:
                            stats = {
                                "mdate": os.path.getmtime(full_path),
                                "size": os.path.getsize(full_path),
                                "isdir": is_dir,
                            }
                            if self.detailed:
                                # Add detailed stats if required
                                pass
                            self.watched[full_path] = stats
                        except OSError:
                            continue
            else:
                for name in os.listdir(self.path):
                    full_path = os.path.join(self.path, name)
                    is_dir = os.path.isdir(full_path)
                    try:
                        stats = {
                            "mdate": os.path.getmtime(full_path),
                            "size": os.path.getsize(full_path),
                            "isdir": is_dir,
                        }
                        if self.detailed:
                            # Add detailed stats if required
                            pass
                        self.watched[full_path] = stats
                    except OSError:
                        continue

        except Exception as e:
            print(f"Failed to snapshot directory {self.path}: {str(e)}")

    def track_changes(self):
        """
        Tracks changes between the current state of the watched files and the previous state.

        This method clears the `changed` dictionary and creates a copy of the `watched` dictionary.
        It then takes a snapshot of the current state of the files being watched.

        For each file in the `old_watched` dictionary, it checks if the file still exists.
        If the file does not exist, it adds the file path to the `changed` dictionary with the value "deleted".
        If the file exists, it checks if the modification time or size of the file has changed compared to the previous state.
        If either the modification time or size has changed, it adds the file path to the `changed` dictionary with the value "modified".

        After checking all the files in `old_watched`, it finds the files that were created by comparing the set of files in `watched` with the set of files in `old_watched`.
        For each newly created file, it adds the file path to the `changed` dictionary with the value "created".

        This method does not return anything.
        """
        self.changed.clear()
        old_watched = self.watched.copy()

        self.snapshot()
        for k, v in old_watched.items():
            if not os.path.exists(k):
                self.changed[k] = "deleted"
            elif v and (
                os.path.getmtime(k) != v["mdate"] or os.path.getsize(k) != v["size"]
            ):
                self.changed[k] = "modified"

        newlycreated = set(self.watched) - set(old_watched)
        for k in newlycreated:
            self.changed[k] = "created"

    @contextmanager
    def watch(self):
        """
        A context manager that watches for changes and tracks them.
        """
        try:
            yield
        finally:
            self.track_changes()

    @property
    def created(self):
        """
        Returns the list of created files.
        """
        created = []
        for k, v in self.changed.items():
            if v == "created":
                created.append(k)
        return created

    @property
    def deleted(self):
        """
        Returns the list of deleted files.
        """
        deleted = []
        for k, v in self.changed.items():
            if v == "deleted":
                deleted.append(k)
        return deleted

    @property
    def modified(self):
        """
        Returns the list of modified files.
        """
        modified = []
        for k, v in self.changed.items():
            if v == "modified":
                modified.append(k)
        return modified
