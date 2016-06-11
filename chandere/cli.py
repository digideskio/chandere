"""Entry point for Chandere, parses command-line arguments and passes them to
the scraper as environment variables.
"""

from __future__ import print_function

import chandere.formatters
import chandere.core

import argparse
import os.path

__version__ = "0.1.1dev1"


class CustomHelp(argparse.HelpFormatter):
    """Small modifications argparse's default HelpFormatter."""

    def _fill_text(self, text, width, indent):
        return "".join(indent + line
                       for line in text.splitlines(keepends=True))

    def _split_lines(self, text, width):
        return text.splitlines()

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "Usage: "
        return super(CustomHelp, self).add_usage(usage, actions, groups,
                                                 prefix)


def parse_arguments():
    """Parses command-line arguments and returns the namespace."""
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=CustomHelp,
        usage="%(prog)s (BOARD)[/THREAD] [-c CHAN] [-o OUTPUT] [OPTIONS]",
        description="Generalized scraper for Futaba-styled imageboards, such "
        "as 4chan.\nCapable of downloading images and archiving entire boards.")
    docs = parser.add_argument_group("Documentation")
    docs.add_argument("-h",
                      "--help",
                      action="help",
                      help="Display this help page and exit.")
    docs.add_argument(
        "-v",
        "--version",
        action="version",
        version="  ###      ###\n  #\033[32;1m@@@\033[;m#  #\033[32;1m@@@"
        "\033[;m#\t\tChandere\n #\033[32;1m@@@@\033[;m#  #\033[32;1m@@@@"
        "\033[;m#\t\tVersion %s" % __version__ + "\n  ####    ####\t\tAn Image"
        "board Scraper\n\n\n    ##    ##\t\tDeveloped by Jakob\n   #\033[32;1m"
        "@@\033[;m#  #\033[32;1m@@\033[;m#\t\thttp://tsar-fox.com/\n  #"
        "\033[32;1m@\033[;m#\033[32;1m@\033[;m#  #\033[32;1m@\033[;m#"
        "\033[32;1m@\033[;m#\n   # #    # #\n",
        help="Display the currently installed version and exit.")
    docs.add_argument("-lc",
                      "--list-chans",
                      action="version",
                      version="Available Imageboard Aliases: "
                      "%s" % ", ".join(chandere.core.KNOWN_CHANS),
                      help="List known imageboard aliases and exit.")
    docs.add_argument("-lm",
                      "--list-modes",
                      action="version",
                      version="Available Modes of Operation: "
                      "%s" % ", ".join(chandere.core.AVAILABLE_MODES),
                      help="List available modes of operation and exit.")
    scraper_opts = parser.add_argument_group("Scraper Options")
    scraper_opts.add_argument(
        "board_thread",
        metavar="BOARD/THREAD",
        nargs="+",
        help="Combination of a board and optionally a thread to\nscrape from. "
        "(E.g.\"/g/51971506\"). If a thread is not\ngiven, Chandere will "
        "attempt to scrape the entire board.\nSeveral board/thread "
        "combinations can be given.")
    scraper_opts.add_argument(
        "-m",
        "--mode",
        default="tc",
        help="Designates the mode of operation for Chandere to operate\nin. "
        "Available modes of operation and their descriptions\ncan be listed "
        "with -lm. Default is \"tc,\"or \"Test\nConnection.\"")
    scraper_opts.add_argument(
        "-o",
        "--output",
        default=".",
        metavar="DIR",
        help="Indicates the path in which downloaded images or\narchives "
        "should be placed. Defaults to ./")
    scraper_opts.add_argument(
        "-df",
        "--dump-file",
        default=os.path.join(
            os.path.expanduser("~"), ".chandere"),
        metavar="DIR",
        help="Specifies a path at which the cache should be dumped, if\n"
        "cache dumping is enabled. Defaults to \".chandere\" in the\n"
        "running user's home directory.")
    scraper_opts.add_argument(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="Omits info-level log messages during runtime.")
    scraper_opts.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Omits the warning about network traffic typically\ngiven before "
        "operating in board mode.")
    scraper_opts.add_argument(
        "-bf",
        "--bottomfeed",
        action="store_true",
        help="Applicable only in board mode. Chanworks will load\nthe oldest "
        "posts first, and work its way back to the\nboard's newest posts "
        "before refreshing.")
    scraper_opts.add_argument(
        "-nd",
        "--no-dump",
        action="store_false",
        dest="dump",
        help="A cache of threads already seen will be used, but\nnot dumped "
        "to a file for future use.")
    scraper_opts.add_argument(
        "-nv",
        "--no-video",
        action="store_true",
        help="Applicable only in image downloader mode. Chandere\nwill ignore "
        ".webm files.")
    connection_opts = parser.add_argument_group("Connection Options")
    connection_opts.add_argument(
        "-c",
        "--chan",
        default="4chan",
        help="Used to designate the imageboard to be scraped from.\nAvailable "
        "aliases can be listed with -lc. Unlisted\nimageboards can be used as "
        "long as they are passed in\nthe form of an url (E.g. "
        "\"https://www.krautchan.net\")\nthough it is possible that the "
        "default offsets will not\nwork with the imageboard in question.")
    connection_opts.add_argument(
        "-r",
        "--refresh",
        default=300,
        type=int,
        metavar="XX",
        help="Specify the time in seconds Chandere should wait before\n"
        "refreshing a thread. This is ignored when scraping an\nentire "
        "board. Default is 300.")
    connection_opts.add_argument(
        "-fs",
        "--force-ssl",
        action="store_true",
        help="Forces connections to use https. Be warned that urllib\ndoes "
        "not attempt to verify the SSL certificate of the\nserver it is "
        "communicating with.")
    return parser.parse_args()


def main():
    """Entry point to the main module."""
    args = parse_arguments()
    combinations = chandere.formatters.separate_board_thread(args.board_thread)
    output, write_mode = chandere.formatters.parse_path(args.output, args.mode)
    refresh_rate = int(args.refresh)
    if len(combinations) < 1:
        exit(1)
    chandere.core.main(args.mode, args.chan, combinations, refresh_rate,
                       args.force_ssl, args.dump_file, args.no_video, output,
                       write_mode, args.bottomfeed, args.dump, args.force,
                       args.verbose)
