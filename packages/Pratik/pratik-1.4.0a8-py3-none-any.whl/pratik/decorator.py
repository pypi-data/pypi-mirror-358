import functools
import warnings


def deprecated(reason=None):
    """ Decorator to mark functions as deprecated.

    This decorator can be used with or without a reason message. It issues a
    `DeprecationWarning` when the decorated function is called. If a reason
    is provided, it will be included in the warning message.

    Args:
        reason (str): Optional message explaining the deprecation or suggesting an alternative.

    Returns:
        Callable: The decorated function or a decorator wrapping the function, depending on usage.

    """

    def decorator(func):
        """Actual decorator that wraps the function and emits a warning.

        Args:
            func (Callable): The function to mark as deprecated.

        Returns:
            Callable: The wrapped function that issues a deprecation warning when called.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function that emits a deprecation warning when the function is called.

            Args:
                *args: Positional arguments passed to the original function.
                **kwargs: Keyword arguments passed to the original function.

            Returns:
                Any: The result of calling the original (deprecated) function.

            Raises:
                DeprecationWarning: Indicates that the function is deprecated.
            """
            msg = f"{func.__name__}() is deprecated"
            if reason:
                msg += f": {reason}"
            else:
                msg += " and will be removed in a future version."
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    if callable(reason):
        # The decorator is used without parentheses
        func = reason
        reason = None
        return decorator(func)

    return decorator