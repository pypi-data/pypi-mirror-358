import datetime
import inspect
import pathlib
from enum import Enum

from pratik.text import Color


class Logger:
    """ A customizable file-based logging utility with color-coded terminal output.

    Supports four logging levels (DEBUG, INFO, WARNING, ERROR), file-based logging
    with automatic directory creation, and per-hour or per-day log file rotation.

    Attributes:
        _path (pathlib.Path): The base directory for storing log files.
        _per_hour (bool): Whether to split logs by hour instead of day.

    Args:
        log_path (str | pathlib.Path): Directory path where log files will be stored.
        per_hour (bool, optional): If True, create separate logs per hour. Defaults to False.
    """

    class Level(Enum):
        """ Enum representing the severity levels for logging.

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
            """ Returns the ANSI color code associated with the logging level.

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
        """ Initializes the Logger instance with a path and file rotation policy.

        Args:
            log_path (str | pathlib.Path): Directory where log files will be stored.
            per_hour (bool, optional): If True, splits logs by hour. Defaults to False.
        """
        self._path = pathlib.Path(log_path) if isinstance(log_path, str) else log_path
        self._per_hour = per_hour
        if not self._path.exists():
            self._path.mkdir(parents=True, exist_ok=True)

    def __str__(self):
        """ Returns a string representation of the logger, as the full file path.

        Returns:
            str: The absolute path of the current log file.
        """
        return str(self.absolute())

    def __repr__(self):
        """ Returns a developer-readable representation of the logger.

        Returns:
            str: The current log file name.
        """
        return self.filename

    @property
    def filename(self):
        """ Computes the log file name based on the current date and optionally hour.

        Returns:
            str: The name of the log file.
        """
        now = datetime.datetime.now()
        if self._per_hour:
            return now.strftime("%Y-%m-%d-%H (%A %d %B %Y à %H heures)") + ".log"
        else:
            return now.strftime("%Y-%m-%d (%A %d %B %Y)") + ".log"

    @property
    def filepath(self):
        """ Constructs the full path to the current log file.

        Returns:
            pathlib.Path: Full path to the log file.
        """
        return self._path / self.filename

    def absolute(self):
        """ Returns the absolute path to the log file.

        Returns:
            pathlib.Path: Absolute path of the current log file.
        """
        return self.filepath.absolute()

    def log(self, *prompt, level=..., printed=True, colored=True, sep=' ', end='\n', file=...):
        """ Logs a message to a file and optionally to the terminal.

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


def write_in_log(logger, *prompt, sep=' ', end='\n'):
    """ Add a message manually to the log.

    Arguments:
        logger (Logger): The logger to use
        *prompt: Message components to log.
        sep (str): Separator between message components. Defaults to ' '.
        end (str): End character(s) for the line. Defaults to newline.

    Returns:
        str: The message written in the log
    """
    message = sep.join(str(p) for p in prompt) + end
    with open(logger.filepath, 'a', encoding='UTF-8') as opened_file:
        opened_file.write(message)
    return message