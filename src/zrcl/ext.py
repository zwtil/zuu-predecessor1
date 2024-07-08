import copy
import json
import typing


class classProperty(object):
    """
    A class that provides a descriptor for defining class-level properties.
    """

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def get_deep(obj: typing.Union[dict, list, set, tuple], *keys):
    """
    Get a value from a nested object using a sequence of keys.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to retrieve the value from.
        *keys: The sequence of keys to access the desired value.

    Returns:
        typing.Any: The value retrieved from the nested object.

    Raises:
        KeyError: If a key is not found in a dictionary.
        IndexError: If an index is out of range in a list, set, or tuple.
        AttributeError: If an attribute is not found in an object.

    Example:
        >>> obj = {'a': {'b': {'c': 42}}}
        >>> get_deep(obj, 'a', 'b', 'c')
        42
    """
    curr = obj
    for key in keys:
        if isinstance(curr, dict):
            curr = curr.get(key)
        elif isinstance(curr, (list, set, tuple)):
            curr = curr[int(key)]
        else:
            curr = getattr(curr, key)

    return curr


def set_deep(obj: typing.Union[dict, list, set, tuple], *keys, value):
    """
    Set a value in a nested object using a sequence of keys.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to set the value in.
        *keys: The sequence of keys to access the desired location for setting the value.
        value: The value to be set in the nested object.

    Raises:
        None

    Returns:
        None
    """
    curr = obj
    for key in keys[:-1]:
        if isinstance(curr, dict):
            curr = curr.get(key)
        elif isinstance(curr, (list, set, tuple)):
            curr = curr[int(key)]
        else:
            curr = getattr(curr, key)

    if isinstance(curr, dict):
        curr[keys[-1]] = value
    elif isinstance(curr, (list, set, tuple)):
        curr[int(keys[-1])] = value
    else:
        setattr(curr, keys[-1], value)


def del_deep(obj: typing.Union[dict, list, set, tuple], *keys):
    """
    A function to delete a value in a nested object using a sequence of keys.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to delete the value from.
        *keys: The sequence of keys to access the desired location for deleting the value.

    Returns:
        None
    """
    curr = obj
    for key in keys[:-1]:
        if isinstance(curr, dict):
            curr = curr.get(key)
        elif isinstance(curr, (list, set, tuple)):
            curr = curr[int(key)]
        else:
            curr = getattr(curr, key)

    if isinstance(curr, dict):
        del curr[keys[-1]]
    elif isinstance(curr, (list, set, tuple)):
        del curr[int(keys[-1])]
    else:
        delattr(curr, keys[-1])


def set_default_deep(
    obj: typing.Union[dict, list, set, tuple], *keys, value, fillpadding=False
):
    """
    Set a value in a nested object using a sequence of keys. If the keys do not exist, they are created.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to set the value in.
        *keys: The sequence of keys to access the desired location for setting the value.
        value: The value to be set in the nested object.
        fillpadding (bool, optional): If True, and the last key is an index that is beyond the length of the current list,
            the list is padded with None values to make space for the new value. Defaults to False.

    Raises:
        IndexError: If the last key is an index that is beyond the length of the current list and fillpadding is False.
        IndexError: If the last key is an index that is beyond the length of the current set or tuple.
        AttributeError: If the last key is an attribute that does not exist in the current object.
        IndexError: If the current object is a set and the last key is not in the set.

    Returns:
        None
    """

    curr = obj
    for key in keys[:-1]:
        if isinstance(curr, dict):
            curr = curr.get(key)
        elif isinstance(curr, (list, set, tuple)):
            curr = curr[int(key)]
        else:
            curr = getattr(curr, key)

    if isinstance(curr, set):
        raise IndexError("set does not support default value")

    # check has attr
    if (
        (isinstance(curr, dict) and keys[-1] in curr)
        or (isinstance(curr, (list, set, tuple)) and int(keys[-1]) < len(curr))
        or (not isinstance(curr, (dict, list, set, tuple)) and hasattr(curr, keys[-1]))
    ):
        return

    if isinstance(curr, dict):
        curr[keys[-1]] = value
    elif isinstance(curr, (list, tuple)):
        if len(curr) + 1 < int(keys[-1]) and not fillpadding:
            raise IndexError

        while len(curr) < int(keys[-1]):
            curr.append(None)

        curr[int(keys[-1])] = value
    else:
        setattr(curr, keys[-1], value)


def rreplace(s: str, old: str, new: str, occurrence):
    """
    Replaces the last occurrence of a substring in a string with a new substring.

    Args:
        s (str): The input string.
        old (str): The substring to be replaced.
        new (str): The new substring to replace the old substring.
        occurrence (int): The number of occurrences of the old substring to replace.

    Returns:
        str: The modified string with the last occurrence of the old substring replaced by the new substring.

    Raises:
        None

    Example:
        >>> rreplace("Hello, world!", "world", "codeium", 1)
        'Hello, codeium!'
    """
    if occurrence <= 0:
        return s

    parts = s.rsplit(old, occurrence)
    return new.join(parts)


class FrozenDict(dict):
    """
    A dictionary that cannot be modified after it is created.

    This class is similar to the built-in `frozenset` data structure, but
    for dictionaries instead of sets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def __copy__(self):
        return FrozenDict(self)

    def __deepcopy__(self, memo):
        return FrozenDict(copy.deepcopy(dict(self), memo))

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __setattr__(self, key, value):
        raise AttributeError

    def __delattr__(self, key):
        raise AttributeError

    def __str__(self):
        return str(sorted(dict(self)))

    def __repr__(self):
        return repr(dict(self))

    @classmethod
    def fromString(cls, string):
        if "{" not in string:
            return cls({"string": string})
        try:
            resolved = json.loads(string)
        except json.decoder.JSONDecodeError:
            resolved = {"string": string}
        return cls(resolved)

    def toJSON(self):
        return json.dumps(dict(self))

    def fromJSON(json_str):
        return FrozenDict(json.loads(json_str))

    @classmethod
    def toString(cls, key):
        if isinstance(key, FrozenDict) and len(key) == 1 and "string" in key:
            # if the key is string
            return key["string"]
        else:
            return json.dumps(dict(key))


class DictKeysDict(dict):
    """
    A dictionary where all keys are enforced to be FrozenDict instances. Any dictionary
    values are converted recursively to DictKeysDict, ensuring that all nested keys within
    these dictionary values are also FrozenDict instances.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        if isinstance(key, str):
            key = FrozenDict.fromString(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        key = self._ensure_frozendict(key)
        value = self._convert_value(value)
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            k = self._ensure_frozendict(k)
            v = self._convert_value(v)
            super().__setitem__(k, v)

    def setdefault(self, key, default=None):
        key = self._ensure_frozendict(key)
        default = self._convert_value(default)
        return super().setdefault(key, default)

    def _ensure_frozendict(self, key):
        """
        Ensures that the given key is a valid FrozenDict or a convertible string.

        Parameters:
            key (Union[str, dict]): The key to be ensured.

        Returns:
            Union[FrozenDict, DictKeysDict]: The ensured key.

        Raises:
            KeyError: If the key is not a valid FrozenDict or a convertible string.
        """
        if isinstance(key, str):
            return FrozenDict.fromString(key)
        elif isinstance(key, dict) and not isinstance(key, FrozenDict):
            return DictKeysDict(key)  # Convert nested dicts on keys to DictKeysDict
        elif not isinstance(key, FrozenDict):
            raise KeyError(
                "Keys must be instances of FrozenDict or convertible strings"
            )
        return key

    def _convert_value(self, value):
        """
        Recursively convert dictionary values to DictKeysDict. If the value is a list or
        another iterable containing dictionaries, those dictionaries are also converted.
        """
        if isinstance(value, dict) and not isinstance(value, DictKeysDict):
            return DictKeysDict(
                {
                    self._ensure_frozendict(k): self._convert_value(v)
                    for k, v in value.items()
                }
            )
        elif isinstance(value, list):
            return [self._convert_value(item) for item in value]
        return value

    @classmethod
    def dumpJson(cls, obj):
        """
        Serializes an object to a JSON string.

        Args:
            obj (Any): The object to be serialized.

        Returns:
            str: The serialized JSON string.

        This class method recursively converts the object to a JSON-serializable format. If the object is a `DictKeysDict`, it converts the keys to strings using `FrozenDict.toString()`. If the object is a list, it recursively converts each item in the list. If the object is a `FrozenDict`, it converts it to a string using `FrozenDict.toString()`. For any other object, it returns the object as is. The resulting object is then serialized using `json.dumps()`.

        Example:
            >>> class DictKeysDict(dict):
            ...     pass
            >>> class FrozenDict(dict):
            ...     @classmethod
            ...     def toString(cls, key):
            ...         return str(key)
            >>> obj = DictKeysDict({FrozenDict({'a': 1}): [FrozenDict({'b': 2}), {'c': 3}]})
            >>> DictKeysDict.dumpJson(obj)
            '{"{a: 1}": ["{b: 2}", {"c": 3}]}'
        """

        def parse(x):
            if isinstance(x, DictKeysDict):
                return {FrozenDict.toString(k): parse(v) for k, v in x.items()}
            elif isinstance(x, list):
                return [parse(item) for item in x]
            elif isinstance(x, FrozenDict):
                return FrozenDict.toString(x)  # Special handling for simple FrozenDict
            else:
                return x

        return json.dumps(parse(obj))

    @classmethod
    def loadJson(cls, jsonStr):
        """
        A method to load JSON from a string, recursively converting nested objects into DictKeysDict.
        Args:
            cls: The class method.
            jsonStr: The JSON string to be loaded.
        Returns:
            The loaded JSON object represented as a DictKeysDict.
        """

        def convert(obj):
            if isinstance(obj, dict):
                return DictKeysDict(
                    {FrozenDict.fromString(k): convert(v) for k, v in obj.items()}
                )
            elif isinstance(obj, list):
                return [convert(item) for item in obj]
            else:
                return obj

        return convert(json.loads(jsonStr))
