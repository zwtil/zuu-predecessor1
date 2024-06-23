class SingletonClssed(type):
    """
    A metaclass that ensures only one instance of a class is created.

    This metaclass is used to create singleton classes. Only one instance of
    a class created with this metaclass will be created.

    Example:
        >>> class MyClass(metaclass=SingletonClssed):
        ...     pass
        >>> my_instance = MyClass()
        >>> my_instance2 = MyClass()
        >>> my_instance is my_instance2
        True
    """

    _cls = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._cls:
            cls._cls[cls] = super(SingletonClssed, cls).__call__(*args, **kwargs)
        return cls._cls[cls]


class SingletonOne(type):
    """
    A metaclass that ensures only one instance of a class is created.

    This metaclass is used to create singleton classes. Only one instance of
    a class created with this metaclass will be created.

    Example:
        >>> class MyClass(metaclass=SingletonOne):
        ...     pass
        >>> my_instance = MyClass()
        >>> my_instance2 = MyClass()
        >>> my_instance is my_instance2
        True
    """

    _ins = None

    def __call__(cls, *args, **kwargs):
        if cls._ins is None:
            cls._ins = super(SingletonOne, cls).__call__(*args, **kwargs)
        return cls._ins
