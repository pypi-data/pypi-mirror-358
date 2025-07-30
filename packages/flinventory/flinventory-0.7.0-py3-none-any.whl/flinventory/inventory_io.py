"""Utilities to read and write files for things, locations and signs.

todo: consistency check for Inventory: schema and options all the same and things consistent?
"""

import random

import argparse
import logging
import os
from typing import Callable, Sequence, Iterable, Optional, Self, Iterator, cast

from . import constant
from .box import BoxedThing
from .location import Schema


class Inventory(list[BoxedThing]):
    """A list of things with some metadata.

    An inventory can be list as list[Thing] but also stores
    the location schema as the attribute inventory.schema
    (None if none given) and options.
    """

    def __init__(
        self,
        things: Iterable[BoxedThing],
        directory: str = ".",
        options: Optional[constant.Options] = None,
        schema: Optional[Schema] = None,
    ):
        """Create an inventory from a list of things.

        Args:
            directory: where all options and data is stored
            things: list of things in the inventory
            options: inventory-wide options. Taken from first thing if not given
            schema: inventory-wide location schema. Taken from first if not given
        """
        super().__init__(things)
        self._directory = directory
        os.makedirs(directory, exist_ok=True)
        if schema is None:
            if len(self) == 0:
                self.schema = Schema({})
            else:
                self.schema = self[0].location.schema
        else:
            self.schema = schema

        if options is None:
            if len(self) == 0:
                self.options = constant.Options({})
            else:
                self.options = self[0].options
        else:
            self.options = options

    @classmethod
    def from_json_files(cls, directory: str = ".") -> Self:
        """Create an inventory from a directory with the structure described in the README.

        Args:
            directory: directory with options, schema and data
        Returns:
            an inventory of things including location and sign as members
        """
        options = constant.Options.from_file(directory)
        schema = Schema.from_file(directory)
        try:
            thing_directories = os.listdir(
                os.path.join(directory, constant.THING_DIRECTORY)
            )
        except (FileNotFoundError, NotADirectoryError):
            boxed_things = []
        else:
            boxed_things = [
                BoxedThing.from_files(
                    directory=os.path.join(
                        directory, constant.THING_DIRECTORY, thing_directory
                    ),
                    options=options,
                    schema=schema,
                )
                for thing_directory in thing_directories
            ]
        return cls(
            things=boxed_things, directory=directory, options=options, schema=schema
        )

    @property
    def directory(self):
        """The directory containing all options and data."""
        return self._directory

    def add_thing(self) -> BoxedThing:
        """Add an empty thing.

        Returns:
            the newly created thing.
        """
        things_directory = os.path.join(self._directory, constant.THING_DIRECTORY)
        os.makedirs(things_directory, exist_ok=True)
        while (
            thing_id := "".join(
                random.choices(population="abcdefghijklmnopqrstuvwxyz0123456789", k=5)
            )
        ) in os.listdir(things_directory):
            pass
        thing_directory = os.path.join(things_directory, thing_id)
        new_thing = BoxedThing.from_files(thing_directory, self.options, self.schema)
        self.append(new_thing)
        return new_thing

    def save(self) -> None:
        """Save inventory files.

        todo: save schema. Schema changes are not implemented in schema yet.
        Saving schema would be possible with schema.json attribute.
        todo: maybe save options
        """
        for thing in self:
            thing.save()

    def get_id(self, thing: BoxedThing) -> str:
        """Return the id (which is its directory with the thing directory) of a thing.

        Needs to be in the inventory because the things know where they are saved
        but not how much of it is their id and how much is the general thing directory.
        """
        return os.path.relpath(
            thing.directory, os.path.join(self._directory, constant.THING_DIRECTORY)
        )

    def get_by_id(self, thing_id: str) -> BoxedThing:
        """Return thing by its id which is its directory name.

        Todo: maybe make more efficient by caching the result in a dict
        or making the inventory a dict [id: thing]

        Raises:
            KeyError: if no such thing exists
        """
        for thing in self:
            if self.get_id(thing) == thing_id:
                return thing
        raise KeyError(thing_id)

    def get_by_key(self, key, value) -> Iterable[BoxedThing]:
        """Return all boxed things that have this value for this key.

        For example useful for looking up thing by name: get_by_key(('name', 0), 'Nice thing')

        If value is None, return all things without this value (or actually having
        this value as None). (If this is trouble because you actually want to search
        for None, the implementation could change but would be more verbose.)

        Todo: maybe make more efficient by caching the result in a dict
        """
        return (box for box in self if box.thing.get(key, None) == value)

    def get_by_best(self, key, value) -> Iterator[BoxedThing]:
        """Return all boxed things that have this value as the 'best' option for this key.

        Where 'best' is meant in the sense of DefaultedDict.best.

        If value is None, return all things without this value (or actually having
        this value as None). (If this is trouble because you actually want to search
        for None, the implementation could change but would be more verbose.)

        Todo: maybe make more efficient by caching the result in a dict
        """
        return (box for box in self if box.thing.best(key, backup=None) == value)

    def direct_ancestors(self, thing: BoxedThing, key: str) -> set[BoxedThing]:
        """Convert key (assuming list of ids) into set of things.

        Intended for key = subclass_of and part_of.
        """
        generalisations = set()
        for thing_id in cast(tuple, thing.get(key, tuple())):
            try:
                generalisations.add(self.get_by_id(thing_id))
            except KeyError:
                logging.getLogger("inventory.direct_generalisations").warning(
                    f"id {thing_id} in {self.get_id(thing)} ({thing.best('name', backup="?")}) "
                    "subclass_of is not a valid id. Ignore it."
                )
        return generalisations

    def ancestors(self, thing: BoxedThing, key: str) -> set[BoxedThing]:
        """Get all direct and indirect key of elements as things.

        Intended for key = subclass_of and part_of.
        """
        generalisations = set()
        unchecked = {thing}
        while unchecked:
            current = unchecked.pop()
            generalisations.add(current)
            unchecked.update(self.direct_ancestors(current, key))
            # to avoid checking something again, avoiding infinite loops:
            unchecked.difference_update(generalisations)
        return generalisations.difference({thing})

    def super_things(self, thing: BoxedThing) -> set[BoxedThing]:
        """Get all things this thing is a part of. Directly or indirectly.

        That is: a part_of b & b part_of c ⇒ a part_of c
        and a subclass_of b not⇒ a part_of b but
        a subclass_of b & b part_of c ⇒ a part_of c

        Infinite loops must be avoided, so simple recursive call might be problematic.

        Not implemented but maybe necessary: caching result in the thing.
        Cache must be invalidated whenever part_of or subclass_of of any
        included thing changes. Difficult. Better would be cache on the
        direct level.
        """
        supers = set()
        unchecked = {thing}
        generalisations = {thing}  # only saved to avoid recursion loop
        unchecked_generalisations = set()
        while unchecked or unchecked_generalisations:
            if unchecked:
                current = unchecked.pop()
                supers.add(current)
            else:
                current = unchecked_generalisations.pop()
                generalisations.add(current)
            unchecked.update(self.direct_ancestors(current, "part_of"))
            unchecked_generalisations.update(
                self.direct_ancestors(current, "subclass_of")
            )
            unchecked.difference_update(supers)
            unchecked_generalisations.difference_update(generalisations)

        return supers.difference({thing})


def check_filename_types(filetypes: Sequence[str]) -> Callable[[str], str]:
    """Create function that checks for being a simple file.

    If it isn't of one of the specified file types, add the fileending."""

    def check_file_type(path: str):
        """Throw an error if path is not a simple file name."""
        # basedir, _ = os.path.split(path)
        # if len(basedir) > 0:
        #     raise argparse.ArgumentTypeError("Only simple file name, not path allowed.")
        _, ext = os.path.splitext(path)
        if ext not in filetypes:
            path += filetypes[0]
        return path

    return check_file_type


def add_file_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments for file names for argument parser."""
    parser.add_argument(
        "dataDirectory",
        default=".",
        help="Directory with all the data. Structure of this directory is not changable.",
    )
    parser.add_argument(
        "--output-dir",
        "-d",
        default="out",
        help=(
            "Directory where to put the output "
            "files like pdf list, sign html pages, LaTeX sign file"
        ),
    )
    parser.add_argument(
        "--output-mdlist",
        "-md",
        default="things.md",
        help=(
            "File where to write the list of things"
            " as a markdown file. Relative to out "
            "directory."
        ),
        type=check_filename_types([".md"]),
    )
    parser.add_argument(
        "--output-tree",
        "-tree",
        default="things-tree.txt",
        help=(
            "File where to write the list of things"
            " as a tree in a text file. Relative "
            "to out directory."
        ),
        type=check_filename_types([".txt"]),
    )
    parser.add_argument(
        "--output-pdflist",
        "-pdf",
        default="things.pdf",
        help=(
            "File where to write the list of things"
            " as a pdf file. Relative to out "
            "directory."
        ),
        type=check_filename_types([".pdf"]),
    )
    parser.add_argument(
        "--output-signs",
        "-s",
        default="signs.html",
        help=(
            "File where to write the html page"
            " with big signs,"
            " relative to out directory."
        ),
        type=check_filename_types([".html", ".htm"]),
    )
    parser.add_argument(
        "--output-signs-latex",
        default="signs.tex",
        help=(
            "File where to write the LaTeX file"
            " with big signs,"
            " relative to out directory."
        ),
        type=check_filename_types([".tex"]),
    )
    parser.add_argument(
        "--logfile",
        "-lf",
        default="things.log",
        help="Where to write the log file. Relative to the out directory.",
        type=check_filename_types([".log"]),
    )


def dict_warn_on_duplicates(ordered_pairs):
    """Log warning for duplicate keys.

    Args:
        ordered_pairs: list of key value pairs found in json
    Returns:
        dictionary with the given keys and values,
        in case of duplicate keys, take the first
    """
    result_dict = {}
    logger = logging.getLogger(__name__ + ".jsonImport")
    for key, value in ordered_pairs:
        if key in result_dict:
            logger.warning(
                f"duplicate key: {key} "
                f"(first value (used): {result_dict[key]}, "
                f"new value: {value})"
            )
        else:
            result_dict[key] = value
    return result_dict
