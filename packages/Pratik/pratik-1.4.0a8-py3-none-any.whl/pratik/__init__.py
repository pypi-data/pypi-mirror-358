""" Pratik is a library of various functions and classes helping to program more efficiently and more intuitively. """

import inspect
import json
import os
import pathlib

from pratik.text import Color

path = pathlib.Path(__file__).parent / 'metadata.json'
if path.exists():
    __DEBUG__ = False
else:
    path = pathlib.Path(__file__).parent.parent / 'metadata.json'
    __DEBUG__ = True
with open(path) as f:
    _METADATA = json.load(f)
    __author__ = _METADATA['authors']
    __version__ = _METADATA['version']
    __description__ = _METADATA['description']

def clear(*, return_line=False):
    """ Clears the console screen.

    This function clears the console by using the `cls` command on Windows
    and `clear` on other operating systems.

    Args:
        return_line (bool, optional): If True, prints a blank line after clearing. Defaults to False.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    if return_line:
        print()


def enter(__prompt='', __type=int):
    """ Allows input of a specified type.

    Types:
    ------
    - bool
    - complex
    - float
    - int
    - list
    - set
    - slice
    - str

    Args:
        __prompt (str, optional): Prompt text. Defaults to ''.
        __type (type, optional): The desired type. Must be in allowed types. Defaults to int.

    Returns:
        Union[bool, complex, float, int, list, set, slice, str]: The typed input.

    Raises:
        TypeError: If an unsupported type is provided.
    """
    if __type not in [
        bool, complex, float, int, list, set, slice, str
    ]:
        raise TypeError(f'{__type} is not a possible type.')
    var: str = input(__prompt)
    while True:
        try:
            '''  '''
            if __type == bool:
                if var.lower() in [
                    "yes", "是的", "हां", "sí", "si", "نعم", "হ্যাঁ", "oui", "да", "sim", "جی ہاں",
                    "y", "1", "true"
                ]:
                    return True
                elif var.lower() in [
                    "no", "不", "नहीं", "no", "لا", "না", "non", "нет", "não", "nao", "نہیں",
                    "n", "0", "false"
                ]:
                    return False
                else:
                    raise ValueError(f"could not convert string to bool: '{var}'")
            elif __type == slice:
                return slice(*var.split(':'))
            elif __type == list:
                return var.split()
            return __type(var)
        except ValueError:
            print(Color.RED + f"\"{var}\" is not of type {__type.__name__}" + Color.STOP)
            var: str = input(__prompt)


def gcd(a, b):
    """
    Computes the greatest common divisor of two numbers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: The greatest common divisor.
    """

    if b == 0:
        return a
    else:
        return gcd(b, a % b)


def get_root(*, trigger='src'):
    """ Gets the root path up to the given trigger directory.

    Args:
        trigger (str, optional): The folder name that marks the root. Defaults to 'src'.

    Returns:
        str: The computed root path.
    """
    caller_frame = inspect.stack()[1]
    root = ''
    index, can_continue = 0, True
    path_parts = caller_frame.filename.split('\\')
    while index < (len(path_parts) - 1) and can_continue:
        part = path_parts[index]
        if part == trigger:
            can_continue = False
        else:
            root += part + '/'
            index += 1
    return root


def humanize_number(__number, __fill_char='.'):
    """
    Formats a number with separators to enhance readability.

    Args:
        __number (int): The number to format.
        __fill_char (str, optional): Separator character. Defaults to '.'.

    Returns:
        str: The formatted number.
    """

    number = list(reversed(str(__number)))
    return ''.join(reversed(__fill_char.join(''.join(number[x:x + 3]) for x in range(0, len(number), 3))))


def is_prime(x):
    """ Checks if a number is a prime number.

    Arguments:
        x (int): The number to check.

    Returns:
        bool: True if the number is prime, False otherwise.
    """
    if abs(x) == 1:
        return False
    else:
        for i in range(2, int(x ** 0.5) + 1):
            if x % i == 0:
                return False
        return True


def progress_bar(x, n, *, width=100):
    """ Displays a progress bar in the console.
    Use '\\\\r' to overwrite the line.

    Args:
        x (int): Current progress.
        n (int): Total count.
        width (int, optional): Width of the bar. Defaults to 100.
    """
    if n > 0:
        pourcent = x / n
        size = round(pourcent * width)
        print(f"\r{x:0{len(str(n))}}/{n} | {'█' * size}{'░' * (width - size)} {round(pourcent * 100):3}%", end='')
    else:
        print(f"\r{x:0{len(str(n))}}/{n} | {'-' * width} NaN%", end='')