import inspect
import pathlib

from pratik import enter
from pratik.text import Color


class Menu:
    """ Class to manage an interactive menu.

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
        """ Initializes the menu with choices, title, description, and back button.

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
        """
        Returns:
            int: Number of choices available in the menu.
        """
        return len(self.choices)

    def __str__(self):
        """
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
        """
        Returns:
            str: Debug representation of the choices.
        """
        return repr(self.choices)

    def __iter__(self):
        """
        Returns:
            iterator: Iterator over menu choices.
        """
        return iter(self.choices)

    def __next__(self):
        """Move to the next option in the menu."""
        self.selected = (self.selected % len(self.choices)) + 1

    @property
    def _width(self):
        """ Calculates the necessary width for the menu layout based on title, description, and choices.

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

    @property
    def _width_number(self):
        """ Calculates the width needed to display the number of choices

        Returns:
            int: The width needed to display the number of choices.
        """
        return len(str(len(self.choices)))

    def select(self, *, printed=True):
        """
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


def choose_in_folder(path=...):
    path = path if path is not ... else pathlib.Path(inspect.stack()[1].filename).parent
    root_path = pathlib.Path(path)
    chooses = [choose for choose in root_path.iterdir()]
    print(root_path, chooses)
    return [None, *chooses][Menu(
        *[choose.name + ('\\' if choose.is_dir() else '') for choose in chooses],
        title=f"Choose in {root_path.name}",
        colored=False,
        back_button=f"Exit"
    ).select()]