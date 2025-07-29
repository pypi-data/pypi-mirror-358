""" Pratik is a library of various functions and classes helping to program more efficiently and more intuitively. """

import datetime
import functools
import inspect
import os
import pathlib
import warnings
from enum import Enum

from pratik.decorator import deprecated as deprecated_
from pratik.text import Color

@deprecated_
def deprecated(func):
    """ [DEPRECATED] Use `pratik.deprecated`. This function will be removed in 1.5.0.

    Decorator to mark functions as deprecated.

    This decorator issues a `DeprecationWarning` when the decorated function is called.
    It's useful for informing users that a function will be removed in a future version,
    and optionally guiding them to use an alternative.

    Args:
        func (Callable): The function to mark as deprecated.

    Returns:
        Callable: The wrapped function that issues a deprecation warning when called.

    Example:
        >>> @deprecated
        ... def old_function():
        ...     pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """ Wrapper function that emits a deprecation warning when the decorated function is called.

        Args:
            *args: Positional arguments passed to the original function.
            **kwargs: Keyword arguments passed to the original function.

        Returns:
            Any: The result of calling the original (deprecated) function.

        Raises:
            DeprecationWarning: Warns that the function is deprecated.
        """
        warnings.warn(
            f"{func.__name__}() is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        return func(*args, **kwargs)

    return wrapper


@deprecated_("Use `pratik.menu.Menu`. This function will be removed in 1.5.0")
class Menu:
    """ [DEPRECATED] Use `pratik.menu.Menu`. This function will be removed in 1.5.0.

    Class to manage an interactive menu.

    Attributes:
        title (str): The title of the menu.
        description (str): The description of the menu.
        description_center (bool): Whether to center the description text.
        choices (tuple): The available options in the menu.
        back_button (str): Text for the back button.
        colored (bool): Whether to color the selected choice.
        selected (int): Index of the currently selected option.
    """

    def __init__(self, *choices, title=..., description=..., back_button=..., description_center=False, colored=True):
        """ [DEPRECATED] Use `pratik.menu.Menu`. This function will be removed in 1.5.0.

        Initializes the menu with choices, title, description, and back button.

        Args:
            *choices: Variable length argument list of menu choices.
            title (str): The title of the menu.
            description (str): The description of the menu.
            back_button (str): The text of the back button.
            description_center (bool, optional): Center the description. Defaults to False.
            colored (bool, optional): Highlight selected choice. Defaults to True.
        """
        self.title = ... if title is ... or title == '' or title.isspace() else title
        self.description = ... if description is ... or description == '' or description.isspace() else description
        self.description_center = description_center
        self.choices = choices
        self.back_button = back_button
        self.colored = colored

        # Default selected option is the first one
        self.selected = 0

    def __len__(self):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Returns:
            int: Number of choices available in the menu.
        """
        return len(self.choices)

    def __str__(self):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Returns:
            str: A formatted string representation of the menu.
        """

        def get_title():
            """ Constructs the title section of the menu.

            Returns:
                str: Formatted title lines with borders.
            """
            if isinstance(self.title, str):
                line1 = f"  ╔═{'═' * len(self.title)}═╗  ".center(width) + "\n"
                line2 = "╔" + f"═╣ {self.title} ╠═".center(width - 2, '═') + "╗\n"
                line3 = "║" + f" ╚═{'═' * len(self.title)}═╝ ".center(width - 2) + "║\n"

                return line1 + line2 + line3
            else:
                return f"╔{'═' * (width - 2)}╗\n"

        def get_description(desc=...):
            """ Constructs the description section, wrapping text appropriately.

            Args:
                desc (list[str]): Pre-split description words. Defaults to self.description.split().

            Returns:
                str: Formatted description lines with alignment.
            """
            if desc is ...:
                if self.description is ...:
                    return ''
                desc: list[str] = self.description.split()

            result = ""

            while len(desc) != 0:
                word = desc.pop(0)
                if len(f"║{result} {word} ║") > width:
                    if self.description_center:
                        return "║" + result.center(width - 3) + " ║\n" + get_description([word] + desc)
                    else:
                        return "║" + result.ljust(width - 3) + " ║\n" + get_description([word] + desc)
                else:
                    result += f" {word}"

            if self.description_center:
                return "║" + result.center(width - 3) + " ║\n" + get_separator()
            else:
                return "║" + result.ljust(width - 3) + " ║\n" + get_separator()

        def get_choice_button(number, choice: str):
            """ Constructs the visual representation of a single choice.

            Args:
                number (int): The number/index of the choice.
                choice (str): The text of the choice.

            Returns:
                str: Formatted choice block with or without highlight.
            """
            if number == self.selected and self.colored:
                return (
                    f"║ {Color.RED}╔═{'═' * nb_width}═╗╔═{'═' * (width - nb_width - 12)}═╗{Color.STOP} ║\n"
                    f"║ {Color.RED}║ {str(number).zfill(nb_width)} ╠"
                    f"╣ {choice.ljust(width - nb_width - 12)} ║{Color.STOP} ║\n"
                    f"║ {Color.RED}╚═{'═' * nb_width}═╝╚═{'═' * (width - nb_width - 12)}═╝{Color.STOP} ║\n"
                )
            else:
                return (
                    f"║ ┌─{'─' * nb_width}─┐┌─{'─' * (width - nb_width - 12)}─┐ ║\n"
                    f"║ │ {str(number).zfill(nb_width)} ├┤ {choice.ljust(width - nb_width - 12)} │ ║\n"
                    f"║ └─{'─' * nb_width}─┘└─{'─' * (width - nb_width - 12)}─┘ ║\n"
                )

        def get_back_button():
            """ Returns the back button block if a back button is configured.

            Returns:
                str: Formatted back button string or empty string if not applicable.
            """
            if isinstance(self.back_button, str):
                return get_separator() + get_choice_button(0, self.back_button)
            else:
                return ''

        def get_separator():
            """ Creates a visual separator line.

            Returns:
                str: The separator string.
            """
            return f"╟{'─' * (width - 2)}╢\n"

        def get_footer():
            """ Returns the footer line of the menu.

            Returns:
                str: Footer string.
            """
            return f"╚{'═' * (width - 2)}╝"

        # If no choices are available, return a message indicating the menu is empty
        if len(self) == 0:
            return "The menu is empty."

        # Calculate width for formatting
        width = self._width
        nb_width = self._width_number

        # Construct the full menu string
        return (
                get_title() +
                get_description() +
                ''.join(get_choice_button(i + 1, self.choices[i]) for i in range(len(self.choices))) +
                get_back_button() +
                get_footer()
        )

    def __repr__(self):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Returns:
            str: Debug representation of the choices.
        """
        return repr(self.choices)

    def __iter__(self):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Returns:
            iterator: Iterator over menu choices.
        """
        return iter(self.choices)

    def __next__(self):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Move to the next option in the menu."""
        self.selected = (self.selected % len(self.choices)) + 1

    def _width(self):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Calculates the necessary width for the menu layout based on title, description, and choices.

        Returns:
            int: The required width for the menu layout.
            """
        if isinstance(self.title, str):
            title_size = len(f"╔═╣ {self.title} ╠═╗")
        else:
            title_size = 0

        if isinstance(self.description, str):
            desc_data = {
                len(word): word for word in self.description.split()
            }
            description_size = len(f"║ {desc_data[max(desc_data.keys())]} ║")
            del desc_data
        else:
            description_size = 0

        choice_data = {
            len(word): word for word in self.choices
        }
        choice_size = len(f"║ │ {len(self.choices)} ├┤ {choice_data[max(choice_data.keys())]} │ ║")
        del choice_data

        if isinstance(self.back_button, str):
            back_size = len(f"║ │ {len(self.choices)} ├┤ {self.back_button} │ ║")
        else:
            back_size = 0

        return max(title_size, description_size, choice_size, back_size)

    def _width_number(self):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Calculates the width needed to display the number of choices

        Returns:
            int: The width needed to display the number of choices.
        """
        return len(str(len(self.choices)))

    def select(self, *, printed=True):
        """ [DEPRECATED] Use `from pratik.menu import Menu`. This function will be removed in 1.5.0.

        Prompts the user to select an option from the menu.

        Args:
            printed (bool, optional): Whether to print the menu before input. Defaults to True.

        Returns:
            int: The selected option index.

        Raises:
            IndexError: If the input is outside the valid range.
        """
        if len(self.choices) == 0:
            if isinstance(self.back_button, str):
                chx = 0
            else:
                return None
        elif len(self.choices) == 1 and not isinstance(self.back_button, str):
            chx = 1
        else:
            if printed:
                print(self)
            was_chosen = False
            chx = None
            while not was_chosen:
                chx = enter(">> ")
                if not (chx not in range(0 if isinstance(self.back_button, str) else 1, len(self.choices) + 1)):
                    was_chosen = True
        self.selected = chx
        return chx


@deprecated_("Use `pratik.logger.Logger`. This function will be removed in 1.5.0")
class Logger:
    """ [DEPRECATED] Use `pratik.logger.Logger`. This function will be removed in 1.5.0.

    A customizable file-based logging utility with color-coded terminal output.

    Supports four logging levels (DEBUG, INFO, WARNING, ERROR), file-based logging
    with automatic directory creation, and per-hour or per-day log file rotation.

    Attributes:
        _path (pathlib.Path): The base directory for storing log files.
        _per_hour (bool): Whether to split logs by hour instead of day.

    Args:
        log_path (str | pathlib.Path): Directory path where log files will be stored.
        per_hour (bool, optional): If True, create separate logs per hour. Defaults to False.
    """

    @deprecated_("Use `pratik.logger.Logger.Level`. This function will be removed in 1.5.0")
    class Level(Enum):
        """ [DEPRECATED] Use `pratik.logger.Logger.Level`. This function will be removed in 1.5.0.

        Enum representing the severity levels for logging.

        Members:
            DEBUG: Used for low-level debugging information.
            INFO: General informational messages.
            WARNING: Messages indicating a potential issue.
            ERROR: Messages reporting errors that occurred.
        """
        DEBUG = -1
        INFO = 0
        WARNING = 1
        ERROR = 2

        @property
        def color(self):
            """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

            Returns the ANSI color code associated with the logging level.

            Returns:
                str: The ANSI escape code for terminal color display.
            """
            if self == self.DEBUG:
                return Color.PURPLE
            elif self == self.INFO:
                return Color.GREEN
            elif self == self.WARNING:
                return Color.YELLOW
            elif self == self.ERROR:
                return Color.RED
            else:
                return ''

    def __init__(self, log_path, *, per_hour=False):
        """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

        Initializes the Logger instance with a path and file rotation policy.

        Args:
            log_path (str | pathlib.Path): Directory where log files will be stored.
            per_hour (bool, optional): If True, splits logs by hour. Defaults to False.
        """
        self._path = pathlib.Path(log_path) if isinstance(log_path, str) else log_path
        self._per_hour = per_hour
        if not self._path.exists():
            self._path.mkdir(parents=True, exist_ok=True)

    def __str__(self):
        """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

        Returns a string representation of the logger, as the full file path.

        Returns:
            str: The absolute path of the current log file.
        """
        return str(self.absolute())

    def __repr__(self):
        """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

        Returns a developer-readable representation of the logger.

        Returns:
            str: The current log file name.
        """
        return self.filename

    def filename(self):
        """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

        Computes the log file name based on the current date and optionally hour.

        Returns:
            str: The name of the log file.
        """
        now = datetime.datetime.now()
        if self._per_hour:
            return now.strftime("%Y-%m-%d-%H (%A %d %B %Y à %H heures)") + ".log"
        else:
            return now.strftime("%Y-%m-%d (%A %d %B %Y)") + ".log"

    def filepath(self):
        """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

        Constructs the full path to the current log file.

        Returns:
            pathlib.Path: Full path to the log file.
        """
        return self._path / self.filename

    def absolute(self):
        """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

        Returns the absolute path to the log file.

        Returns:
            pathlib.Path: Absolute path of the current log file.
        """
        return self.filepath.absolute()

    def log(self, *prompt, level=..., printed=True, colored=True, sep=' ', end='\n', file=...):
        """ [DEPRECATED] Use `from pratik.logger import Logger`. This function will be removed in 1.5.0.

        Logs a message to a file and optionally to the terminal.

        Args:
            *prompt: Message components to log.
            level (Logger.Level): The log level. Defaults to Logger.Level.INFO.
            printed (bool): If True, also prints the message to the terminal. Defaults to True.
            colored (bool): If True and printed is True, prints with color. Defaults to True.
            sep (str): Separator between message components. Defaults to ' '.
            end (str): End character(s) for the line. Defaults to newline.
            file (str | pathlib.Path): Path to the log file. Defaults to current file.

        Raises:
            TypeError: If the `file` argument is not a valid path type.
        """
        if level is ...:
            level = self.Level.INFO
        if file is ...:
            file = self.filepath
        if not isinstance(file, pathlib.Path):
            file = pathlib.Path(file)

        if not file.exists():
            file.parent.mkdir(parents=True, exist_ok=True)

        caller = inspect.stack()[-2]
        text = (
            f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}] '
            f'[{level.name.center(10)}] '
            f'({caller.filename} - {caller.function} : {caller.lineno}) '
            f'{sep.join([str(p) for p in prompt])}'
        )

        with open(file, 'a', encoding='UTF-8') as opened_file:
            opened_file.write(text + end)

        if printed:
            if colored:
                print(level.color if colored else '', end='')
            print(text, end=('\033[0m' + end) if colored else end)


@deprecated_("Use the `__path__` variable instead. This function will be removed in 1.5.0")
def get_path(*path):
    """ [DEPRECATED] Use the `__path__` variable instead. This function will be removed in 1.5.0.

    Constructs a full file path, adapting to the current execution environment.

    Args:
        *path (str): Additional path components to join.

    Returns:
        str: The resolved file path.
    """

    # Get the filename of the caller
    caller_frame = inspect.stack()[1]
    caller_file = caller_frame.filename

    # Compute the absolute path relative to the caller's file location
    caller_path = pathlib.Path(caller_file).parent
    for part_path in path:
        if part_path == '..':
            caller_path = caller_path.parent
        else:
            caller_path = caller_path.joinpath(part_path)
    return str(caller_path.absolute()).replace('\\', '/')


@deprecated_("Use `pratik.get_root`. This function will be removed in 1.5.0")
def get_root(*, trigger='src'):
    """ [DEPRECATED] Use `pratik.get_root`. This function will be removed in 1.5.0.

    Gets the root path up to the given trigger directory.

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


@deprecated_("Use `pratik.enter`. This function will be removed in 1.5.0")
def enter(__prompt='', __type=int):
    """ [DEPRECATED] Use `pratik.enter`. This function will be removed in 1.5.0.

    Allows input of a specified type.

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


@deprecated_("Use `pratik.humanize_number`. This function will be removed in 1.5.0")
def humanize_number(__number, __fill_char='.'):
    """ [DEPRECATED] Use `pratik.humanize_number`. This function will be removed in 1.5.0.

    Formats a number with separators to enhance readability.

    Args:
        __number (int): The number to format.
        __fill_char (str, optional): Separator character. Defaults to '.'.

    Returns:
        str: The formatted number.
    """

    number = list(reversed(str(__number)))
    return ''.join(reversed(__fill_char.join(''.join(number[x:x + 3]) for x in range(0, len(number), 3))))


@deprecated_("Use `pratik.gcd`. This function will be removed in 1.5.0")
def gcd(a, b):
    """ [DEPRECATED] Use `pratik.gcd`. This function will be removed in 1.5.0.

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


@deprecated_("Use `pratik.progress_bar`. This function will be removed in 1.5.0")
def progress_bar(x, n, *, width=100):
    """ [DEPRECATED] Use `pratik.progress_bar`. This function will be removed in 1.5.0.

    Displays a progress bar in the console.
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


@deprecated_("Use `pratik.clear`. This function will be removed in 1.5.0")
def clear(*, return_line=False):
    """ [DEPRECATED] Use `pratik.clear`. This function will be removed in 1.5.0.

    Clears the console screen.

    This function clears the console by using the `cls` command on Windows
    and `clear` on other operating systems.

    Args:
        return_line (bool, optional): If True, prints a blank line after clearing. Defaults to False.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    if return_line:
        print()
