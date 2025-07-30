import builtins

_original_print = builtins.print
_original_input = builtins.input

_ansi_colour = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}

_reverse_ansi_colour = {v: k for k, v in _ansi_colour.items()}

_reset_code = "\x1b[0m"
_state = {"print_colour": "\x1b[33m", "input_colour": "\x1b[33m", "add_linebreak": True}


def set_linebreak(enabled: bool) -> None:
    """Enable or disable adding a linebreak before each print."""
    _state["add_linebreak"] = enabled


def _validate_colour(colour: str) -> None:
    """Validate that the given colour is known."""
    if colour.lower() not in _ansi_colour:
        raise ValueError(f"Unknown colour: {colour}")


def set_print_colour(colour: str) -> None:
    """Set the colour for printed text."""
    _validate_colour(colour)
    _state["print_colour"] = f"\x1b[{_ansi_colour[colour.lower()]}m"


def set_input_colour(colour: str) -> None:
    """Set the colour for input prompts."""
    _validate_colour(colour)
    _state["input_colour"] = f"\x1b[{_ansi_colour[colour.lower()]}m"


def get_print_colour() -> str:
    """Get the current print colour as a string."""
    return _reverse_ansi_colour.get(
        int(_state["print_colour"].strip("\x1b[m")), "Error: Unknown colour"
    )


def get_input_colour() -> str:
    """Get the current input colour as a string."""
    return _reverse_ansi_colour.get(
        int(_state["input_colour"].strip("\x1b[m")), "Error: Unknown colour"
    )


def colored_print(*args, **kwargs) -> None:
    """Print with the current print colour and optional linebreak."""
    lb = "\n" if _state["add_linebreak"] else ""
    _original_print(_state["print_colour"], end=lb)
    _original_print(*args, **kwargs)
    _original_print(_reset_code, end="")


def colored_input(prompt="") -> str:
    """Input with the current input colour."""
    _original_print(_state["input_colour"])
    user_input = _original_input(prompt + _reset_code)
    return user_input
