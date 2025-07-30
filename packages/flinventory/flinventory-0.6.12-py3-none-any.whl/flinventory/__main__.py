"""Entrypoint to the package if called for running without import.

Command-line interface with the different housekeeping tasks.
"""

import argparse

from . import generate_labels, inventory_io
from . import datacleanup


def parse_args():
    """Parse the command-line arguments.

    Supply information from command-line arguments.

    Add various subparsers that have each a func
    default that tells the main program which
    function should be called if this subcommand
    is issued.

    Returns:
        Options as a dict-like object.

    """
    parser = argparse.ArgumentParser(
        description="""Collection of various data cleaning tasks and label making.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers()
    inventory_io.add_file_args(parser)
    datacleanup.add_arg_parsers(subparsers)
    generate_labels.add_arg_parsers(subparsers)
    return parser.parse_args()


def main():
    """Run the command-line interface."""
    arguments = parse_args()
    datacleanup.logging_config(arguments)
    try:
        function = arguments.func
    except AttributeError:
        print("No command given. See -h for help information.")
    else:
        function(arguments)


if __name__ == "__main__":
    main()
