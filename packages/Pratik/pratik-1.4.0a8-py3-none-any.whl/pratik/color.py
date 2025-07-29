class Color:
    @staticmethod
    def by_hsv(h, s, v, alpha=1.0):
        """ To convert from HSV to RGB

        Arguments:
            h (float): Hue H ∈ [0, 1]
            s (float): Saturation S ∈ [0, 1]
            v (float): Value V ∈ [0, 1]
            alpha (float): Alpha ∈ [0, 1]

        Returns:
            (Color): Color of HSV values.

        Raises:
            ValueError: If the values are not between 0 and 1.
        """
        if h < 0 or 1 < h:
            raise ValueError("Hue must be between 0 and 1 (include)")
        if s < 0 or 1 < s:
            raise ValueError("Saturation must be between 0 and 1 (include)")
        if v < 0 or 1 < v:
            raise ValueError("Value must be between 0 and 1 (include)")
        if alpha < 0 or 1 < alpha:
            raise ValueError("Alpa must be between 0 and 1 (include)")

        def f(n):
            k = (n + h * 6) % 6
            return v - (v * s * max(0, min(k, 4 - k, 1)))

        return Color(f(5), f(3), f(1))

    @staticmethod
    def by_hsl(h, s, l, alpha=1.0):
        """ To convert from HSL to RGB

        Arguments:
            h (float): Hue H ∈ [0, 1]
            s (float): Saturation S ∈ [0, 1]
            l (float): Lightness L ∈ [0, 1]
            alpha (float): Alpha ∈ [0, 1]

        Returns:
            (Color): Color of HSL values.

        Raises:
            ValueError: If the values are not between 0 and 1.
        """

        def hue(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        if h < 0 or 1 < h:
            raise ValueError("Hue must be between 0 and 1 (include)")
        if s < 0 or 1 < s:
            raise ValueError("Saturation must be between 0 and 1 (include)")
        if l < 0 or 1 < l:
            raise ValueError("Light must be between 0 and 1 (include)")
        if alpha < 0 or 1 < alpha:
            raise ValueError("Alpa must be between 0 and 1 (include)")

        if s == 0:
            r = g = b = l
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue(p, q, h + 1 / 3)
            g = hue(p, q, h)
            b = hue(p, q, h - 1 / 3)

        return Color(r, g, b)

    @staticmethod
    def by_rgb255(r, g, b, alpha=255):
        """ To convert from RGB ∈ [0, 255] to RGB ∈ [0, 1]

        Arguments:
            r (int): Red ∈ [0, 255]
            g (int): Green ∈ [0, 255]
            b (int): Blue ∈ [0, 255]
            alpha (int): Alpha ∈ [0, 255]

        Returns:
            Color: Color of RGB values.

        Raises:
            ValueError: If the values are not between 0 and 255.
        """
        if r < 0 or 255 < r:
            raise ValueError("Red must be between 0 and 255 (include)")
        if g < 0 or 255 < g:
            raise ValueError("Green must be between 0 and 255 (include)")
        if b < 0 or 255 < b:
            raise ValueError("Blue must be between 0 and 255 (include)")
        if alpha < 0 or 255 < alpha:
            raise ValueError("Alpa must be between 0 and 255 (include)")
        return Color(r / 255.0, g / 255.0, b / 255.0)

    @staticmethod
    def by_hexadecimal(hexadecimal):
        """ To convert from hexadecimal

        Arguments:
            hexadecimal (str): The hexadecimal value to convert.

        Returns:
            (Color): Color of hexadecimal values.
        """
        hexadecimal = hexadecimal.removeprefix('#')
        if len(hexadecimal) == 6:
            return Color.by_rgb255(
                int(hexadecimal[:2], 16),
                int(hexadecimal[2:4], 16),
                int(hexadecimal[4:], 16)
            )
        else:
            return Color.by_rgb255(
                int(hexadecimal[2:4], 16),
                int(hexadecimal[4:6], 16),
                int(hexadecimal[6:], 16),
                int(hexadecimal[:2], 16)
            )

    @staticmethod
    def by_binary(binary):
        """ To convert from binary

        Arguments:
            binary (str): The binary value to convert.

        Returns:
            (Color): Color of binary values.
        """
        binary = binary.removeprefix('0b')
        if len(binary) == 24:
            return Color.by_rgb255(
                int(binary[:8], 2),
                int(binary[8:16], 2),
                int(binary[16:], 2)
            )
        else:
            return Color.by_rgb255(
                int(binary[8:16], 2),
                int(binary[16:24], 2),
                int(binary[24:], 2),
                int(binary[:8], 2)
            )

    # =-= =-= =-= =< Constructor >= =-= =-= =-= #

    def __init__(self, r, g, b, alpha=1.0):
        """ Color Constructor

        Arguments:
            r (float): Red ∈ [0, 1]
            g (float): Green ∈ [0, 1]
            b (float): Blue ∈ [0, 1]
            alpha (float): Alpha ∈ [0, 1]

        Raises:
            ValueError: If the values are not between 0 and 1.
        """
        if r < 0 or 1 < r:
            raise ValueError("Red must be between 0 and 1 (include)")
        if g < 0 or 1 < g:
            raise ValueError("Green must be between 0 and 1 (include)")
        if b < 0 or 1 < b:
            raise ValueError("Blue must be between 0 and 1 (include)")
        if alpha < 0 or 1 < alpha:
            raise ValueError("Alpa must be between 0 and 1 (include)")

        self.red: float = r
        self.green: float = g
        self.blue: float = b
        self.alpha: float = alpha

    # =-= =-= =-= =< --- >= =-= =-= =-= #

    def __repr__(self):
        return f"<red:{self.red255}, green:{self.green255}, blue:{self.blue255}" + (
            f", alpha:{self.alpha255}>" if self.alpha != 1.0 else ">")

    def __index__(self):
        return int(self)

    def __abs__(self):
        copy = self.copy()
        copy.alpha = 1.0
        return copy

    def __neg__(self):
        copy = self.copy()
        copy.red = 1.0 - copy.red
        copy.green = 1.0 - copy.green
        copy.blue = 1.0 - copy.blue
        copy.alpha = 1.0 - copy.alpha
        return copy

    def __pos__(self):
        return self.copy()

    # =-= =-= =-= =< Concatenating Operators >= =-= =-= =-= #

    def __str__(self):
        return f"({self.red255}, {self.green255}, {self.blue255})"

    def __int__(self):
        return int(self.binary, 2)

    # =-= =-= =-= =< Comparison Operator Methods >= =-= =-= =-= #

    def __lt__(self, other):
        return self.hue < other

    def __le__(self, other):
        return self.hue <= other

    def __eq__(self, other):
        if isinstance(other, Color):
            return (
                    self.red == other.red and
                    self.green == other.green and
                    self.blue == other.blue and
                    self.alpha == other.alpha
            )
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, Color):
            return (
                    self.red != other.red or
                    self.green != other.green or
                    self.blue != other.blue or
                    self.alpha != other.alpha
            )
        else:
            return True

    def __ge__(self, other):
        return self.hue >= other

    def __gt__(self, other):
        return self.hue > other

    # =-= =-= =-= =< Arithmetic Operators >= =-= =-= =-= #

    def __add__(self, other):
        if isinstance(other, Color):
            return Color(
                min(1.0, self.red + other.red),
                min(1.0, self.green + other.green),
                min(1.0, self.blue + other.blue),
                self.alpha
            )
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                return Color(
                    min(1.0, self.red + other),
                    min(1.0, self.green + other),
                    min(1.0, self.blue + other),
                    self.alpha
                )
            else:
                return Color.by_rgb255(
                    min(255, round(self.red255 + other)),
                    min(255, round(self.green255 + other)),
                    min(255, round(self.blue255 + other)),
                    self.alpha255
                )
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __sub__(self, other):
        if isinstance(other, Color):
            return Color(
                max(0.0, self.red - other.red),
                max(0.0, self.green - other.green),
                max(0.0, self.blue - other.blue),
                self.alpha
            )
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                return Color(
                    max(0.0, self.red - other),
                    max(0.0, self.green - other),
                    max(0.0, self.blue - other),
                    self.alpha
                )
            else:
                return Color.by_rgb255(
                    max(0, round(self.red255 - other)),
                    max(0, round(self.green255 - other)),
                    max(0, round(self.blue255 - other)),
                    self.alpha255
                )
        else:
            raise TypeError(f"unsupported operand type(s) for -: '{type(self)}' and '{type(other)}'")

    def __mul__(self, other):
        if isinstance(other, Color):
            return Color(
                min(1.0, abs(self.red * other.red)),
                min(1.0, abs(self.green * other.green)),
                min(1.0, abs(self.blue * other.blue)),
                self.alpha
            )
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                return Color(
                    min(1.0, abs(self.red * other)),
                    min(1.0, abs(self.green * other)),
                    min(1.0, abs(self.blue * other)),
                    self.alpha
                )
            else:
                return Color.by_rgb255(
                    min(255, abs(round(self.red255 * other))),
                    min(255, abs(round(self.green255 * other))),
                    min(255, abs(round(self.blue255 * other))),
                    self.alpha255
                )
        else:
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'")

    def __truediv__(self, other):
        if isinstance(other, Color):
            return Color(
                abs(self.red / other.red),
                abs(self.green / other.green),
                abs(self.blue / other.blue),
                self.alpha
            )
        elif isinstance(other, (int, float)):
            return Color(
                abs(self.red / other),
                abs(self.green / other),
                abs(self.blue / other),
                self.alpha
            )
        else:
            raise TypeError(f"unsupported operand type(s) for /: '{type(self)}' and '{type(other)}'")

    def __floordiv__(self, other):
        if isinstance(other, Color):
            return Color(
                abs((self.red255 // other.red) / 255),
                abs((self.green255 // other.green) / 255),
                abs((self.blue255 // other.blue) / 255),
                self.alpha
            )
        elif isinstance(other, (int, float)):
            return Color(
                abs((self.red255 // other) / 255),
                abs((self.green255 // other) / 255),
                abs((self.blue255 // other) / 255),
                self.alpha
            )
        else:
            raise TypeError(f"unsupported operand type(s) for //: '{type(self)}' and '{type(other)}'")

    def __mod__(self, other):
        if isinstance(other, Color):
            return Color(
                abs((self.red255 % other.red) / 255),
                abs((self.green255 % other.green) / 255),
                abs((self.blue255 % other.blue) / 255),
                self.alpha
            )
        elif isinstance(other, (int, float)):
            return Color(
                abs((self.red255 % other) / 255),
                abs((self.green255 % other) / 255),
                abs((self.blue255 % other) / 255),
                self.alpha
            )
        else:
            raise TypeError(f"unsupported operand type(s) for %: '{type(self)}' and '{type(other)}'")

    def __pow__(self, other):
        if isinstance(other, Color):
            return Color(
                min(1.0, abs(self.red ** other.red)),
                min(1.0, abs(self.green ** other.green)),
                min(1.0, abs(self.blue ** other.blue)),
                self.alpha
            )
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                return Color(
                    min(1.0, abs(self.red ** other)),
                    min(1.0, abs(self.green ** other)),
                    min(1.0, abs(self.blue ** other)),
                    self.alpha
                )
            else:
                return Color.by_rgb255(
                    min(255, abs(round(self.red255 ** other))),
                    min(255, abs(round(self.green255 ** other))),
                    min(255, abs(round(self.blue255 ** other))),
                    self.alpha255
                )
        else:
            raise TypeError(f"unsupported operand type(s) for **: '{type(self)}' and '{type(other)}'")

    # =-= =< Right-Hand Method >= =-= #

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __rmod__(self, other):
        return self.__mod__(other)

    def __rpow__(self, other):
        return self.__pow__(other)

    # =-= =< Augmented Assignments >= =-= #

    def __iadd__(self, other):
        if isinstance(other, Color):
            self.red = min(1.0, self.red + other.red)
            self.green = min(1.0, self.green + other.green)
            self.blue = min(1.0, self.blue + other.blue)
            return self
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                self.red = min(1.0, self.red + other)
                self.green = min(1.0, self.green + other)
                self.blue = min(1.0, self.blue + other)
                return self
            else:
                self.red255 = min(255, self.red + other)
                self.green255 = min(255, self.green + other)
                self.blue255 = min(255, self.blue + other)
                return self
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __isub__(self, other):
        if isinstance(other, Color):
            self.red = max(0.0, self.red - other.red)
            self.green = max(0.0, self.green - other.green)
            self.blue = max(0.0, self.blue - other.blue)
            return self
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                self.red = max(0.0, self.red - other)
                self.green = max(0.0, self.green - other)
                self.blue = max(0.0, self.blue - other)
                return self
            else:
                self.red255 = max(0, self.red255 - other)
                self.green255 = max(0, self.green255 - other)
                self.blue255 = max(0, self.blue255 - other)
                return self
        else:
            raise TypeError(f"unsupported operand type(s) for -: '{type(self)}' and '{type(other)}'")

    def __imul__(self, other):
        if isinstance(other, Color):
            self.red = min(1.0, abs(self.red * other.red))
            self.green = min(1.0, abs(self.green * other.green))
            self.blue = min(1.0, abs(self.blue * other.blue))
            return self
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                self.red = min(1.0, abs(self.red * other))
                self.green = min(1.0, abs(self.green * other))
                self.blue = min(1.0, abs(self.blue * other))
                return self
            else:
                self.red255 = min(1.0, abs(self.red255 * other))
                self.green255 = min(1.0, abs(self.green255 * other))
                self.blue255 = min(1.0, abs(self.blue255 * other))
                return self
        else:
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'")

    def __itruediv__(self, other):
        if isinstance(other, Color):
            self.red = abs(self.red / other.red)
            self.green = abs(self.green / other.green)
            self.blue = abs(self.blue / other.blue)
            return self
        elif isinstance(other, (int, float)):
            self.red = abs(self.red / other)
            self.green = abs(self.green / other)
            self.blue = abs(self.blue / other)
            return self
        else:
            raise TypeError(f"unsupported operand type(s) for /: '{type(self)}' and '{type(other)}'")

    def __ifloordiv__(self, other):
        if isinstance(other, Color):
            self.red255 = abs(self.red255 // other.red255)
            self.green255 = abs(self.green255 // other.green255)
            self.blue255 = abs(self.blue255 // other.blue255)
            return self
        elif isinstance(other, (int, float)):
            self.red255 = abs(self.red255 // other)
            self.green255 = abs(self.green255 // other)
            self.blue255 = abs(self.blue255 // other)
            return self
        else:
            raise TypeError(f"unsupported operand type(s) for //: '{type(self)}' and '{type(other)}'")

    def __imod__(self, other):
        if isinstance(other, Color):
            self.red255 = abs(self.red255 % other.red255)
            self.green255 = abs(self.green255 % other.green255)
            self.blue255 = abs(self.blue255 % other.blue255)
            return self
        elif isinstance(other, (int, float)):
            self.red255 = abs(self.red255 % other)
            self.green255 = abs(self.green255 % other)
            self.blue255 = abs(self.blue255 % other)
            return self
        else:
            raise TypeError(f"unsupported operand type(s) for %: '{type(self)}' and '{type(other)}'")

    def __ipow__(self, other):
        if isinstance(other, Color):
            self.red = min(1.0, abs(self.red ** other.red))
            self.green = min(1.0, abs(self.green ** other.green))
            self.blue = min(1.0, abs(self.blue ** other.blue))
            return self
        elif isinstance(other, (int, float)):
            if isinstance(other, float) and other < 1:
                self.red = min(1.0, abs(self.red ** other))
                self.green = min(1.0, abs(self.green ** other))
                self.blue = min(1.0, abs(self.blue ** other))
                return self
            else:
                self.red255 = min(255, abs(self.red255 ** other))
                self.green255 = min(255, abs(self.green255 ** other))
                self.blue255 = min(255, abs(self.blue255 ** other))
                return self
        else:
            raise TypeError(f"unsupported operand type(s) for **: '{type(self)}' and '{type(other)}'")

    # =-= =-= =-= =< Bitwise Operators >= =-= =-= =-= #

    def __and__(self, other):
        return self.by_binary(bin(int(self) & int(other))[2:].rjust(32, '0'))

    def __or__(self, other):
        return self.by_binary(bin(int(self) | int(other))[2:].rjust(32, '0'))

    def __xor__(self, other):
        return self.by_binary(bin(int(self) ^ int(other))[2:].rjust(32, '0'))

    def __invert__(self):
        return self.by_binary(
            (f'{bin(self.alpha255)[2:]:08}' if self.alpha != 1.0 else '') +
            bin(
                ~int(f"0b{bin(self.red255)[2:]:08}{bin(self.green255)[2:]:08}{bin(self.blue255)[2:]:08}", 2)
            )[2:].rjust(32, '0')
        )

    def __lshift__(self, places):
        return self.by_binary(bin(int(self) << places)[2:].rjust(32, '0'))

    def __rshift__(self, places):
        return self.by_binary(bin(int(self) >> places)[2:].rjust(32, '0'))

    # =-= =< Augmented Assignments >= =-= #

    def __iand__(self, other):
        return self.set(self.__and__(other))

    def __ior__(self, other):
        return self.set(self.__or__(other))

    def __ixor__(self, other):
        return self.set(self.__xor__(other))

    def __ilshift__(self, places):
        return self.set(self.__lshift__(places))

    def __irshift__(self, places):
        return self.set(self.__rshift__(places))

    # =-= =-= =-= =< Creating Iterators >= =-= =-= =-= #

    def __iter__(self):
        c = self.copy()
        c.hue = 0
        return self.copy()

    def __next__(self):
        if self.hue < 359:
            self.hue += 1
            return self
        else:
            raise StopIteration

    @property
    def binary(self):
        return (f"0b"
                f"{f'{bin(self.alpha255)[2:]:08}' if self.alpha != 1.0 else ''}"
                f"{bin(self.red255)[2:]:08}"
                f"{bin(self.green255)[2:]:08}"
                f"{bin(self.blue255)[2:]:08}")

    @binary.setter
    def binary(self, value):
        self.set(self.by_binary(value))

    @property
    def hexadecimal(self):
        return (f"#"
                f"{f'{hex(self.alpha255)[2:]:02}' if self.alpha != 1.0 else ''}"
                f"{hex(self.red255)[2:]:02}"
                f"{hex(self.green255)[2:]:02}"
                f"{hex(self.blue255)[2:]:02}").upper()

    @hexadecimal.setter
    def hexadecimal(self, value):
        self.set(self.by_hexadecimal(value))

    @property
    def rgb255(self):
        return self.red255, self.green255, self.blue255

    @rgb255.setter
    def rgb255(self, value):
        self.red255, self.green255, self.blue255 = value

    @property
    def red255(self):
        return round(self.red * 255)

    @red255.setter
    def red255(self, value):
        self.red = value / 255

    @property
    def green255(self):
        return round(self.green * 255)

    @green255.setter
    def green255(self, value):
        self.green = value / 255

    @property
    def blue255(self):
        return round(self.blue * 255)

    @blue255.setter
    def blue255(self, value):
        self.blue = value / 255

    @property
    def alpha255(self):
        return round(self.alpha * 255)

    @alpha255.setter
    def alpha255(self, value):
        self.alpha = value / 255

    @property
    def max(self):
        return max(self.red, self.green, self.blue)

    @property
    def min(self):
        return min(self.red, self.green, self.blue)

    @property
    def range(self):
        return self.max - self.min

    @property
    def chroma(self):
        return self.range

    @property
    def hsv(self):
        return self.hue, self.saturation_value, self.value

    @hsv.setter
    def hsv(self, value):
        self.set(self.by_hsv(*value))

    @property
    def hsl(self):
        return self.hue, self.saturation_lightness, self.lightness

    @hsl.setter
    def hsl(self, value):
        self.set(self.by_hsl(*value))

    @property
    def hue(self):
        v_max = self.max
        v_min = self.min
        if v_max == v_min:
            return 0
        else:
            d = v_max - v_min

            if v_max == self.red:
                hue = (self.green - self.blue) / d + (6 if self.green < self.blue else 0)
            elif v_max == self.green:
                hue = (self.blue - self.red) / d + 2
            else:
                hue = (self.red - self.green) / d + 4

            hue /= 6

            return round(hue, 2)

    @hue.setter
    def hue(self, value):
        self.set(self.by_hsv(value, self.saturation_value, self.value))

    @property
    def saturation_value(self):
        return 0 if self.value == 0 else self.chroma / self.value

    @saturation_value.setter
    def saturation_value(self, value):
        self.set(self.by_hsv(self.hue, value, self.value))

    @property
    def value(self):
        return self.max

    @value.setter
    def value(self, value):
        self.set(self.by_hsv(self.hue, self.saturation_value, value))

    @property
    def saturation_lightness(self):
        v_max = self.max
        v_min = self.min
        return round(
            0
            if v_max == v_min else
            (
                (v_max - v_min) / (2 - v_max - v_min)
                if ((v_max + v_min) / 2) > 0.5 else
                (v_max - v_min) / (v_max + v_min)
            ), 2
        )

    @saturation_lightness.setter
    def saturation_lightness(self, value):
        self.set(self.by_hsl(self.hue, value, self.lightness))

    @property
    def lightness(self):
        return round((self.max + self.min) / 2, 2)

    @lightness.setter
    def lightness(self, value):
        self.set(self.by_hsl(self.hue, self.saturation_lightness, value))

    @property
    def ascii(self):
        return f"\033[38;2;{self.red255};{self.green255};{self.blue255}m"

    def copy(self):
        return Color(self.red, self.green, self.blue, self.alpha)

    def set(self, other):
        self.red = other.red
        self.green = other.green
        self.blue = other.blue
        self.alpha = other.alpha
        return self
