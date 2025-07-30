from dict_fancy_printer.fancy_printer import FancyPrinter


def fancy_dict(d: dict) -> str():
    """Given a python dictionary, return a formatted string"""
    printer = FancyPrinter()
    return printer(d)


def print_fancy_dict(d: dict) -> None:
    """Given a python dictionary, it prints it in fancy way"""
    print(fancy_dict(d), end="")
