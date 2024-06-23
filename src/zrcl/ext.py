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
