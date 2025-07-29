class Singleton:
    """A class implementing the Singleton design pattern.

    This class ensures that only one instance of the class exists at any time.
    """

    _instance = None  # The single instance of the class

    def __new__(cls, *args, **kwargs):
        """Creates a new instance of the class, if one does not exist.

        If an instance already exists, it returns the existing instance.
        If arguments are provided and an instance exists, it reinitialized the instance.

        Arguments:
            *args: Positional arguments passed to singleton_init.
            **kwargs: Keyword arguments passed to singleton_init.

        Returns:
            Singleton: The single instance of the Singleton class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.singleton_init(*args, **kwargs)
        elif args or kwargs:
            cls._instance.singleton_init(*args, **kwargs)
        return cls._instance

    def singleton_init(self, *args, **kwargs):
        """Initializes the singleton instance.

        This method is intended to be overridden or extended in subclasses.

        Arguments:
            *args: Positional arguments passed to initialization.
            **kwargs: Keyword arguments passed to initialization.
        """
        pass


class KeySingleton:
    """A class implementing the Singleton design pattern.

    This class ensures that only one instance of the class exists at any time.
    """

    _instance = {}  # The single instance of the class

    def __new__(cls, key, *args, **kwargs):
        """Creates a new instance of the class, if one does not exist.

        If an instance already exists, it returns the existing instance.
        If arguments are provided and an instance exists, it reinitialized the instance.

        Arguments:
            *args: Positional arguments passed to singleton_init.
            **kwargs: Keyword arguments passed to singleton_init.

        Returns:
            Singleton: The single instance of the Singleton class.
        """
        if key not in cls._instance:
            cls._instance[key] = super().__new__(cls)
            cls._instance[key].singleton_init(*args, **kwargs)
        elif args or kwargs:
            cls._instance[key].singleton_init(*args, **kwargs)
        return cls._instance[key]

    def singleton_init(self, *args, **kwargs):
        """Initializes the singleton instance.

        This method is intended to be overridden or extended in subclasses.

        Arguments:
            *args: Positional arguments passed to initialization.
            **kwargs: Keyword arguments passed to initialization.
        """
        pass
