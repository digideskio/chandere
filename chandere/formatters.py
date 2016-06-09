"""Formatters for Chandere, meant to be called by cli.py to put input into a
form usable by the core module."""

import re
import os

def separate_board_thread(arguments):
    """Parses the positional argument for specifying the board and thread to
    scrape from.
    """
    combinations = []
    for argument in arguments:
        try:
            board = "/" + re.search(r'[\d\w]+(?=\/)?', argument).group() + "/"
        except AttributeError:
            print("error: Invalid board given.")
            exit(1)
        try:
            thread = re.search(r'(?<=(\/|\s))\d+(?!\/)', argument).group()
        except AttributeError:
            thread = None
        combinations.append((board, thread))
    return combinations


def parse_path(string, mode):
    """Validates a specific output location."""
    is_potential_file = bool(re.search(r'\S\.\w+(?!(\\|\/))', string))
    parent_dir = os.path.dirname(os.path.abspath(string))
    write_mode = None
    if mode == "id":
        if is_potential_file:
            exit("error: \"id\" mode cannot output to a file.")
        elif os.path.exists(string) and os.path.isdir(string):
            path = string
        elif os.path.exists(parent_dir) and not os.path.exists(string):
            os.mkdir(string)
            path = string
        else:
            exit("error: Invalid output path.")
    elif mode == "ar":
        if os.path.exists(string) and os.path.isfile(string):
            path = string
            write_mode = "a"
        elif os.path.exists(string) and os.path.isdir(string):
            path = os.path.join(string, "archive.txt")
            write_mode = "a+"
        elif os.path.exists(parent_dir) and not os.path.exists(string):
            path = string
            write_mode = "a+"
        else:
            exit("error: Invalid output path.")
    else:
        path = None
    return (path, write_mode)
