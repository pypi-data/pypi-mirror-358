""" ANSI color and style utilities for terminal output.

This module provides classes and utilities to format text with ANSI escape
sequences. It supports standard colors, RGB and hexadecimal values, background
highlighting, and text styling such as bold, italic, and underline.

Classes:
    - Color: For text color manipulation.
    - Highlight: For background color manipulation.
    - Style: For text style attributes (bold, italic, etc.)

Functions:
    - generate: Utility to combine ANSI codes into a single sequence.
    - information: Returns a formatted table of ANSI codes.

Note:
    This module depends on `pratik.color.Color` and uses a custom
    `@deprecated` decorator for legacy API maintenance.
"""

import pratik.color
from pratik.decorator import deprecated


def generate(*code):
    """ For concat too many codes.

    Arguments:
        code (str | int): An ANSI code or number code

    Returns:
        str: The ANSI escape sequence
    """

    def normalize(x):
        """ Normalize an ANSI code or numeric value into a clean string.

        Arguments:
            x (str | int):

        Returns:
            str:
        """
        if str(x).startswith('\033'):
            return x.removeprefix('\033[').removesuffix('m')
        else:
            return str(x)

    return "\033[{}m".format(';'.join(normalize(c) for c in code))


class Color:
    """ Class for control the color of the text."""

    @staticmethod
    @deprecated("Use `from_rgb`. This function will be removed in 1.6.0.")
    def get_rgb(red, green, blue):
        """ Get the ANSI escape sequence for an RGB color.

        Arguments:
            red (int) : The red color: 0 -> 255
            green (int) : The green color: 0 -> 255
            blue (int) : The blue color: 0 -> 255

        Returns:
            str : The ANSI escape sequence
        """
        return Color.from_rgb(red, green, blue)

    @staticmethod
    @deprecated("Use `from_hexadecimal`. This function will be removed in 1.6.0.")
    def get_hex(hexadecimal):
        """ Get the ANSI escape sequence for a Hex color.

        Arguments:
            hexadecimal (str) : The hexadecimal color: #000000 -> #FFFFFF

        Returns:
            str : The ANSI escape sequence
        """
        return Color.from_hexadecimal(hexadecimal)

    @classmethod
    def from_rgb(cls, red, green, blue):
        """ Get the ANSI escape sequence for an RGB color.

        Arguments:
            red (int): The red color: 0 -> 255
            green (int): The green color: 0 -> 255
            blue (int): The blue color: 0 -> 255

        Returns:
            str : The ANSI escape sequence
        """
        return "\033[38;2;{red};{green};{blue}m".format(red=red, green=green, blue=blue)

    @classmethod
    def apply_rgb(cls, red, green, blue, prompt):
        """ Apply the RGB color to text.

        Arguments:
            red (int): The red color: 0 -> 255
            green (int): The green color: 0 -> 255
            blue (int): The blue color: 0 -> 255
            prompt (str): The text prompt

        Returns:
            str : The prompt with the color.
        """
        return "\033[38;2;{red};{green};{blue}m{text}{stop}".format(
            red=red, green=green, blue=blue, text=prompt, stop=cls.STOP
        )

    @classmethod
    def from_hexadecimal(cls, hexadecimal):
        """ Get the ANSI escape sequence for a Hexadécimal color.

        WARN: Alpha in hexadecimal is ignored.

        Arguments:
            hexadecimal (str): The hexadecimal color: #000000 -> #FFFFFF

        Returns:
            str : The ANSI escape sequence
        """
        return cls.from_pratik_color(pratik.color.Color.by_hexadecimal(hexadecimal))

    @classmethod
    def apply_hexadecimal(cls, hexadecimal, prompt):
        """ Apply the Hexadécimal color to text.

        Arguments:
            hexadecimal (str): The hexadecimal color: #000000 -> #FFFFFF
            prompt (str): The text prompt

        Returns:
            str : The prompt with the color.
        """
        return "{ascii}{text}{stop}".format(
            ascii=cls.from_pratik_color(pratik.color.Color.by_hexadecimal(hexadecimal)), text=prompt, stop=cls.STOP
        )

    @classmethod
    def from_pratik_color(cls, color):
        """ Get the ANSI escape sequence for a Pratik color.

        WARN: Alpha is ignored.

        Arguments:
            color (pratik.color.Color): The Pratik's color

        Returns:
            str : The ANSI escape sequence
        """
        return cls.from_rgb(*color.rgb255)

    @classmethod
    def apply_pratik_color(cls, color, prompt):
        """ Apply the Pratik color to text.

        WARN: Alpha is ignored.

        Arguments:
            color (pratik.color.Color): The Pratik's color
            prompt (str): The text prompt

        Returns:
            str : The prompt with the color.
        """
        return "{ascii}{text}{stop}".format(
            ascii=cls.from_rgb(*color.rgb255), text=prompt, stop=cls.STOP
        )

    BLACK: str = '\033[30m'
    RED: str = '\033[31m'
    GREEN: str = '\033[32m'
    YELLOW: str = '\033[33m'
    BLUE: str = '\033[34m'
    PURPLE: str = '\033[35m'
    CYAN: str = '\033[36m'
    WHITE: str = '\033[37m'

    LIGHT_BLACK: str = '\033[90m'
    LIGHT_RED: str = '\033[91m'
    LIGHT_GREEN: str = '\033[92m'
    LIGHT_YELLOW: str = '\033[93m'
    LIGHT_BLUE: str = '\033[94m'
    LIGHT_PURPLE: str = '\033[95m'
    LIGHT_CYAN: str = '\033[96m'
    LIGHT_WHITE: str = '\033[97m'

    STOP: str = '\033[39m'

    @classmethod
    def black(cls, prompt):
        """ Apply black color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.BLACK, prompt, cls.STOP)

    @classmethod
    def red(cls, prompt):
        """ Apply red color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.RED, prompt, cls.STOP)

    @classmethod
    def green(cls, prompt):
        """ Apply green color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.GREEN, prompt, cls.STOP)

    @classmethod
    def yellow(cls, prompt):
        """ Apply yellow color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.YELLOW, prompt, cls.STOP)

    @classmethod
    def blue(cls, prompt):
        """ Apply blue color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.BLUE, prompt, cls.STOP)

    @classmethod
    def purple(cls, prompt):
        """ Apply purple color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.PURPLE, prompt, cls.STOP)

    @classmethod
    def cyan(cls, prompt):
        """ Apply cyan color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.CYAN, prompt, cls.STOP)

    @classmethod
    def white(cls, prompt):
        """ Apply white color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.WHITE, prompt, cls.STOP)

    @classmethod
    def light_black(cls, prompt):
        """ Apply light black color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_BLACK, prompt, cls.STOP)

    @classmethod
    def light_red(cls, prompt):
        """ Apply light red color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_RED, prompt, cls.STOP)

    @classmethod
    def light_green(cls, prompt):
        """ Apply light green color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_GREEN, prompt, cls.STOP)

    @classmethod
    def light_yellow(cls, prompt):
        """ Apply light yellow color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_YELLOW, prompt, cls.STOP)

    @classmethod
    def light_blue(cls, prompt):
        """ Apply light blue color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_BLUE, prompt, cls.STOP)

    @classmethod
    def light_purple(cls, prompt):
        """ Apply light purple color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_PURPLE, prompt, cls.STOP)

    @classmethod
    def light_cyan(cls, prompt):
        """ Apply light cyan color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_CYAN, prompt, cls.STOP)

    @classmethod
    def light_white(cls, prompt):
        """ Apply light white color to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the color.
        """
        return "{}{}{}".format(cls.LIGHT_WHITE, prompt, cls.STOP)

    def __init__(self, red=..., green=..., blue=..., *, hexadecimal=...):
        """ Use red, green, blue OR hexadecimal.

        **WARNING**: Hexadecimal overwrites red, green and blue.

        Arguments:
            red (int) : The red color: 0 -> 255
            green (int) : The green color: 0 -> 255
            blue (int) : The blue color: 0 -> 255
            hexadecimal (str) : The hexadecimal color: #000000 -> #FFFFFF
        """
        self.red = None
        self.green = None
        self.blue = None
        self.set(red, green, blue, hexadecimal=hexadecimal)

    def __str__(self):
        """Get the Hexadecimal value"""

        def make(x):
            """Convert an integer into a 2-digit hexadecimal string.

            Arguments:
                x (int): Integer value to convert (0 → 255)

            Returns:
                str: Hexadecimal string (e.g. 15 → "0F")
            """
            return hex(x).replace('0x', '').upper().rjust(2, '0')

        return "#{red}{green}{blue}".format(red=make(self.red), green=make(self.green), blue=make(self.blue))

    def __repr__(self):
        return "<ANSI Color:{red}, {green}, {blue}>".format(red=self.red, green=self.green, blue=self.blue)

    def __int__(self):
        return int(str(self)[1:], 16)

    def __next__(self):
        def make(x):
            """Convert an integer into a 2-digit hexadecimal string.

            Arguments:
                x (int): Integer value to convert (0 → 255)

            Returns:
                str: Hexadecimal string (e.g. 15 → "0F")
            """
            return hex(x).replace('0x', '').upper().rjust(6, '0')

        value = int(self) + 1
        if value > 16777215:
            raise StopIteration
        self.set(hexadecimal=make(value))
        return self

    @property
    def ansi_escape_sequence(self):
        """Return the ANSI escape sequence of this color.

        Returns:
            str: The escape sequence to apply this color to the foreground.
        """
        return self.from_hexadecimal(str(self))

    def set(self, red=..., green=..., blue=..., *, hexadecimal=...):
        """ Use red, green, blue OR hexadecimal.

        **WARNING**: Hexadecimal overwrites red, green and blue.

        Arguments:
            red (int) : The red color: 0 -> 255
            green (int) : The green color: 0 -> 255
            blue (int) : The blue color: 0 -> 255
            hexadecimal (str) : The hexadecimal color: #000000 -> #FFFFFF
        """
        if hexadecimal is not ...:
            if hexadecimal[0] == "#":
                hexadecimal = hexadecimal[1:]
            red = int(hexadecimal[:2], 16)
            green = int(hexadecimal[2:4], 16)
            blue = int(hexadecimal[4:], 16)
        self.red = red
        self.green = green
        self.blue = blue


class Highlight:
    """ Class for control the color of the highlight."""

    @staticmethod
    @deprecated("Use `from_rgb`. This function will be removed in 1.6.0.")
    def get_rgb(red=..., green=..., blue=...):
        """ [DEPRECATED] Use `from_rgb`. This function will be removed in 1.6.0.

        Get the ANSI escape sequence for an RGB color.

        Arguments:
            red (int) : The red color: 0 -> 255
            green (int) : The green color: 0 -> 255
            blue (int) : The blue color: 0 -> 255

        Returns:
            str : The ANSI escape sequence
        """
        return Highlight.from_rgb(red, green, blue)

    @staticmethod
    @deprecated("Use `from_hexadecimal`. This function will be removed in 1.6.0.")
    def get_hex(hexadecimal):
        """ [DEPRECATED] Use `from_hexadecimal`. This function will be removed in 1.6.0.

        Get the ANSI escape sequence for a Hex color.

        Arguments:
            hexadecimal (str) : The hexadecimal color: #000000 -> #FFFFFF

        Returns:
            str : The ANSI escape sequence
        """
        return Highlight.from_hexadecimal(hexadecimal)

    @classmethod
    def from_rgb(cls, red, green, blue):
        """ Get the ANSI escape sequence for an RGB color.

        Arguments:
            red (int): The red color: 0 -> 255
            green (int): The green color: 0 -> 255
            blue (int): The blue color: 0 -> 255

        Returns:
            str : The ANSI escape sequence
        """
        return "\033[48;2;{red};{green};{blue}m".format(red=red, green=green, blue=blue)

    @classmethod
    def apply_rgb(cls, red, green, blue, prompt):
        """ Apply the RGB highlight to text.

        Arguments:
            red (int): The red color: 0 -> 255
            green (int): The green color: 0 -> 255
            blue (int): The blue color: 0 -> 255
            prompt (str): The text prompt

        Returns:
            str : The prompt with the highlight.
        """
        return "\033[38;2;{red};{green};{blue}m{text}{stop}".format(
            red=red, green=green, blue=blue, text=prompt, stop=cls.STOP
        )

    @classmethod
    def from_hexadecimal(cls, hexadecimal):
        """ Get the ANSI escape sequence for a Hex color.

        WARN: Alpha in hexadecimal is ignored.

        Arguments:
            hexadecimal (str): The hexadecimal color: #000000 -> #FFFFFF

        Returns:
            str : The ANSI escape sequence
        """
        return cls.from_pratik_color(pratik.color.Color.by_hexadecimal(hexadecimal))

    @classmethod
    def apply_hexadecimal(cls, hexadecimal, prompt):
        """ Apply the Hexadécimal highlight to text.

        Arguments:
            hexadecimal (str): The hexadecimal color: #000000 -> #FFFFFF
            prompt (str): The text prompt

        Returns:
            str : The prompt with the highlight.
        """
        return "{ascii}{text}{stop}".format(
            ascii=cls.from_pratik_color(pratik.color.Color.by_hexadecimal(hexadecimal)), text=prompt, stop=cls.STOP
        )

    @classmethod
    def from_pratik_color(cls, color):
        """ Get the ANSI escape sequence for a Hex color.

        WARN: Alpha is ignored.

        Arguments:
            color (pratik.color.Color): The Pratik's color

        Returns:
            str : The ANSI escape sequence
        """
        return cls.from_rgb(*color.rgb255)

    @classmethod
    def apply_pratik_color(cls, color, prompt):
        """ Apply the Pratik highlight to text.

        WARN: Alpha is ignored.

        Arguments:
            color (pratik.color.Color): The Pratik's color
            prompt (str): The text prompt

        Returns:
            str : The prompt with the highlight.
        """
        return "{ascii}{text}{stop}".format(
            ascii=cls.from_rgb(*color.rgb255), text=prompt, stop=cls.STOP
        )

    BLACK: str = '\033[40m'
    RED: str = '\033[41m'
    GREEN: str = '\033[42m'
    YELLOW: str = '\033[43m'
    BLUE: str = '\033[44m'
    PURPLE: str = '\033[45m'
    CYAN: str = '\033[46m'
    WHITE: str = '\033[47m'

    LIGHT_BLACK: str = '\033[100m'
    LIGHT_RED: str = '\033[101m'
    LIGHT_GREEN: str = '\033[102m'
    LIGHT_YELLOW: str = '\033[103m'
    LIGHT_BLUE: str = '\033[104m'
    LIGHT_PURPLE: str = '\033[105m'
    LIGHT_CYAN: str = '\033[106m'
    LIGHT_WHITE: str = '\033[107m'

    STOP: str = '\033[49m'

    @classmethod
    def black(cls, prompt):
        """ Apply black in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.BLACK, prompt, cls.STOP)

    @classmethod
    def red(cls, prompt):
        """ Apply red in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.RED, prompt, cls.STOP)

    @classmethod
    def green(cls, prompt):
        """ Apply green in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.GREEN, prompt, cls.STOP)

    @classmethod
    def yellow(cls, prompt):
        """ Apply yellow in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.YELLOW, prompt, cls.STOP)

    @classmethod
    def blue(cls, prompt):
        """ Apply blue in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.BLUE, prompt, cls.STOP)

    @classmethod
    def purple(cls, prompt):
        """ Apply purple in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.PURPLE, prompt, cls.STOP)

    @classmethod
    def cyan(cls, prompt):
        """ Apply cyan in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.CYAN, prompt, cls.STOP)

    @classmethod
    def white(cls, prompt):
        """ Apply white in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.WHITE, prompt, cls.STOP)

    @classmethod
    def light_black(cls, prompt):
        """ Apply light black in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_BLACK, prompt, cls.STOP)

    @classmethod
    def light_red(cls, prompt):
        """ Apply light red in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_RED, prompt, cls.STOP)

    @classmethod
    def light_green(cls, prompt):
        """ Apply light green in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_GREEN, prompt, cls.STOP)

    @classmethod
    def light_yellow(cls, prompt):
        """ Apply light yellow in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_YELLOW, prompt, cls.STOP)

    @classmethod
    def light_blue(cls, prompt):
        """ Apply light blue in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_BLUE, prompt, cls.STOP)

    @classmethod
    def light_purple(cls, prompt):
        """ Apply light purple in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_PURPLE, prompt, cls.STOP)

    @classmethod
    def light_cyan(cls, prompt):
        """ Apply light cyan in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_CYAN, prompt, cls.STOP)

    @classmethod
    def light_white(cls, prompt):
        """ Apply light white in highlight to text

        Arguments:
             prompt (str): The text prompt

        Returns:
            str: The prompt with the highlight.
        """
        return "{}{}{}".format(cls.LIGHT_WHITE, prompt, cls.STOP)

    def __init__(self, red=..., green=..., blue=..., *, hexadecimal=...):
        """ Use red, green, blue OR hexadecimal.

        **WARNING**: Hexadecimal overwrites red, green and blue.

        Arguments:
            red (int) : The red color: 0 -> 255
            green (int) : The green color: 0 -> 255
            blue (int) : The blue color: 0 -> 255
            hexadecimal (str) : The hexadecimal color: #000000 -> #FFFFFF
        """
        self.red = None
        self.green = None
        self.blue = None
        self.set(red, green, blue, hexadecimal=hexadecimal)

    def __str__(self):
        """Get the Hexadecimal value"""

        def make(x):
            """Convert an integer into a 2-digit hexadecimal string.

            Arguments:
                x (int): Integer value to convert (0 → 255)

            Returns:
                str: Hexadecimal string (e.g. 15 → "0F")
            """
            return hex(x).replace('0x', '').upper().rjust(2, '0')

        return "#{red}{green}{blue}".format(red=make(self.red), green=make(self.green), blue=make(self.blue))

    def __repr__(self):
        return "<ANSI Highlight:{red}, {green}, {blue}>".format(red=self.red, green=self.green, blue=self.blue)

    def __int__(self):
        return int(str(self)[1:], 16)

    def __next__(self):
        def make(x):
            """Convert an integer into a 2-digit hexadecimal string.

            Arguments:
                x (int): Integer value to convert (0 → 255)

            Returns:
                str: Hexadecimal string (e.g. 15 → "0F")
            """
            return hex(x).replace('0x', '').upper().rjust(6, '0')

        value = int(self) + 1
        if value > 16777215:
            raise StopIteration
        self.set(hexadecimal=make(value))
        return self

    @property
    def ansi_escape_sequence(self):
        """Return the ANSI escape sequence of this highlight.

        Returns:
            str: The escape sequence to apply this color to the background.
        """
        return self.get_hex(str(self))

    def set(self, red=..., green=..., blue=..., *, hexadecimal=...):
        """ Use red, green, blue OR hexadecimal.

        **WARNING**: Hexadecimal overwrites red, green and blue.

        Arguments:
            red (int) : The red color: 0 -> 255
            green (int) : The green color: 0 -> 255
            blue (int) : The blue color: 0 -> 255
            hexadecimal (str) : The hexadecimal color: #000000 -> #FFFFFF
        """
        if hexadecimal is not ...:
            if hexadecimal[0] == "#":
                hexadecimal = hexadecimal[1:]
            red = int(hexadecimal[:2], 16)
            green = int(hexadecimal[2:4], 16)
            blue = int(hexadecimal[4:], 16)
        self.red = red
        self.green = green
        self.blue = blue


class Style:
    """ Class for control the style of the text."""

    BOLD = "\033[1m"
    NO_BOLD = "\033[21m"

    @classmethod
    def bold(cls, prompt):
        """ Apply bold to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.BOLD, prompt, cls.NO_BOLD)

    LOW_INTENSITY = "\033[2m"
    NO_LOW_INTENSITY = "\033[22m"

    @classmethod
    def low_intensity(cls, prompt):
        """ Apply low intensity to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.LOW_INTENSITY, prompt, cls.NO_LOW_INTENSITY)

    ITALIC = "\033[3m"
    NO_ITALIC = "\033[23m"

    @classmethod
    def italic(cls, prompt):
        """ Apply italic to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.ITALIC, prompt, cls.NO_ITALIC)

    UNDERLINE = "\033[4m"
    NO_UNDERLINE = "\033[24m"

    @classmethod
    def underline(cls, prompt):
        """ Apply underline to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.UNDERLINE, prompt, cls.NO_UNDERLINE)

    SLOWLY_FLASHING = "\033[5m"
    NO_SLOWLY_FLASHING = "\033[25m"

    @classmethod
    def slowly_flashing(cls, prompt):
        """ Apply slowly flashing to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.SLOWLY_FLASHING, prompt, cls.NO_SLOWLY_FLASHING)

    RAPIDLY_FLASHING = "\033[6m"
    NO_RAPIDLY_FLASHING = "\033[26m"

    @classmethod
    def rapidly_flashing(cls, prompt):
        """ Apply rapidly flashing to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.RAPIDLY_FLASHING, prompt, cls.NO_RAPIDLY_FLASHING)

    NEGATIVE = "\033[7m"
    NO_NEGATIVE = "\033[27m"

    @classmethod
    def negative(cls, prompt):
        """ Apply negative to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.NEGATIVE, prompt, cls.NO_NEGATIVE)

    HIDDEN = "\033[8m"
    NO_HIDDEN = "\033[28m"

    @classmethod
    def hidden(cls, prompt):
        """ Apply hidden to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.HIDDEN, prompt, cls.NO_HIDDEN)

    STRIKETHROUGH = "\033[9m"
    NO_STRIKETHROUGH = "\033[29m"

    @classmethod
    def strikethrough(cls, prompt):
        """ Apply strikethrough to text.

        Arguments:
            prompt (str) : The text prompt

        Returns:
            str: The text prompt with effect.
        """
        return "{}{}{}".format(cls.STRIKETHROUGH, prompt, cls.NO_STRIKETHROUGH)

    STOP_ALL = generate(*range(21, 30))
    """str: Combined ANSI codes to reset most styles (bold, italic, underline, etc.)."""


def information():
    """ All ANSI code in table

    Returns:
        str: A table of information
    """
    return """\
╔═════════╦══════════════════════════════╦════════════════════════════════════════════════════════════════════════╗
║   Code  ║            Effect            ║                                  Note                                  ║
╠═════════╬══════════════════════════════╬════════════════════════════════════════════════════════════════════════║
║    0    ║        Reset / Normal        ║                      all attributes off (default)                      ║
║    1    ║  Bold or increased intensity ║                                                                        ║
║    2    ║   Dim (decreased intensity)  ║                          Not widely supported.                         ║
║    3    ║            Italic            ║           Not widely supported. Sometimes treated as inverse.          ║
║    4    ║           Underline          ║                                                                        ║
║    5    ║          Slow blink          ║                        less than 150 per minute                        ║
║    6    ║          Rapid blink         ║         MS-DOS ANSI.SYS; 150+ per minute; not widely supported         ║
║    7    ║       [[Inverse video]]      ║                  swap foreground and background colors                 ║
║    8    ║            Conceal           ║                          Not widely supported.                         ║
║    9    ║            Crossed           ║   Characters legible, but marked for deletion. Not widely supported.   ║
║    10   ║    Primary (default) font    ║                                                                        ║
║  11–19  ║        Alternate font        ║                      Select alternate font `n-10`                      ║
║    20   ║            Fraktur           ║                          hardly ever supported                         ║
║    21   ║ Bold off or double underline ║ Bold off not widely supported; double underline hardly ever supported. ║
║    22   ║  Normal color or intensity   ║                         Neither bold nor faint                         ║
║    23   ║    Not italic, not Fraktur   ║                                                                        ║
║    24   ║         Underline off        ║                     Not singly or doubly underlined                    ║
║    25   ║           Blink off          ║                                                                        ║
║    27   ║          Inverse off         ║                                                                        ║
║    28   ║            Reveal            ║                               conceal off                              ║
║    29   ║          Not crossed         ║                                                                        ║
║  30–37  ║     Set foreground color     ║                          See color table below                         ║
║    38   ║     Set foreground color     ║            next arguments are `5;n` or `2;r;g;b`, see below            ║
║    39   ║   Default foreground color   ║             implementation defined (according to standard)             ║
║  40–47  ║     Set background color     ║                          See color table below                         ║
║    48   ║     Set background color     ║            next arguments are `5;n` or `2;r;g;b`, see below            ║
║    49   ║   Default background color   ║             implementation defined (according to standard)             ║
║    51   ║            Framed            ║                                                                        ║
║    52   ║           Encircled          ║                                                                        ║
║    53   ║           Overlined          ║                                                                        ║
║    54   ║    Not framed or encircled   ║                                                                        ║
║    55   ║         Not overlined        ║                                                                        ║
║    60   ║      Ideogram underline      ║                          hardly ever supported                         ║
║    61   ║  Ideogram double underline   ║                          hardly ever supported                         ║
║    62   ║       Ideogram overline      ║                          hardly ever supported                         ║
║    63   ║   Ideogram double overline   ║                          hardly ever supported                         ║
║    64   ║     Ideogram stress mark     ║                          hardly ever supported                         ║
║    65   ║    Ideogram attributes off   ║                     reset the effects of all 60-64                     ║
║  90–97  ║  Set bright foreground color ║                        aixterm (not in standard)                       ║
║ 100–107 ║  Set bright background color ║                        aixterm (not in standard)                       ║
╚═════════╩══════════════════════════════╩════════════════════════════════════════════════════════════════════════╝
"""


STOP = "\033[0m"