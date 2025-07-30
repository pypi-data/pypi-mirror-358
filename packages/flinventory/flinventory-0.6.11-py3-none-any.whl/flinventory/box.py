#!/usr/bin/env python3
"""Class representing a thing in an inventory for a specific workshop with location and sign."""
import itertools
import os.path

import collections.abc
from typing import Any, Optional, Self, Union, cast

from . import constant
from . import defaulted_data

from .location import Location, Schema
from .sign import Sign
from .thing import Thing


class BoxedThing:
    """Represents one thing in the workshop inventory.

    That is: a thing, a location, a sign, an image.

    Dictionary-like functions are forwarded to the underlying thing.

    Location and sign are special members, given by the respective files.

    Properties:
        location: Location   Where this thing is stored.
        sign: Sign           Parameters for the sign for this thing.
        options: Options     Global options.
        directory: str      Where information about this thing is stored.
                             Accessible only via property directory.
    """

    def __init__(
        self,
        options: constant.Options,
        schema: Schema,
        directory: str,
        thing: Optional[Thing] = None,
        location: Optional[Location] = None,
        sign: Optional[Sign] = None,
    ):
        """Create a thing from the given data.

        If created empty, adding a name afterward is heavily encouraged.
        If thing and sign are given, sign.default must be thing.
        The directory for thing, sign and location must be the same.
        Args:
            directory: directory where the thing data should be saved (later).
            options: global options
            schema: location schema for the location
            thing: the thing to be stored. If None, replaced with empty thing.
            location: where the thing is stored. If none, empty location is created.
            sign: how the sign for this thing looks like. If none, empty sign information is used.
        """
        self._thing = (
            Thing(data={}, default={}, options=options, directory=directory)
            if thing is None
            else thing
        )
        self._location = (
            Location(schema=schema, data={}, directory=directory, options=options)
            if location is None
            else location
        )
        self._sign = (
            Sign(
                data={},
                thing=self._thing,
                options=options,
                directory=directory,
            )
            if sign is None
            else sign
        )
        self._directory = directory
        self.options = options
        assert (error := self.consistent()) == "", error

    @property
    def thing(self):
        """The underlying thing."""
        return self._thing

    @property
    def location(self):
        """The location of the box."""
        return self._location

    @property
    def sign(self):
        """The sign information for this box."""
        return self._sign

    def consistent(self):
        """Checks if the data in all sub elements (thing, sign, location) are consistent.

        - .directory is the same
        - thing is default of sign
        - todo: options are the same for all

        Usable in assert statement:
        assert (error := self.consistent) == "", error

        Returns:
            "" if fine, error message str if not consistent
        """
        if self._sign.default != self._thing:
            return (
                "When creating a boxed thing, the default for sign data must the thing."
            )
        if self._sign.directory != self.directory:
            return (
                f"When creating a boxed thing, the directory for the sign must "
                f"be same as for the box, not {self._sign.directory=} != {self.directory=}."
            )
        if self._location.directory != self.directory:
            return (
                f"When creating a boxed thing, the directory for the sign must "
                f"be same as for the box, not {self._location.directory=} != {self.directory=}."
            )
        if self._thing.directory != self.directory:
            return (
                f"When creating a boxed thing, the directory for the thing must "
                f"be same as for the box, not {self._thing.directory=} != {self.directory=}."
            )
        return ""

    @classmethod
    def from_files(
        cls, directory: str, options: constant.Options, schema: Schema
    ) -> Self:
        """Create a new boxed thing based on yaml files in directory.

        Arguments:
            directory: directory which includes a THING_FILE file and maybe
                a SIGN_FILE and LOCATION_FILE (a missing THING_FILE raises no error
                but is a bit useless)
            options: global options
            schema: location schema to interpret location data
        """
        thing = Thing.from_yaml_file(directory=directory, default={}, options=options)
        location = Location.from_yaml_file(
            directory=directory, schema=schema, options=options
        )
        sign = Sign.from_yaml_file(directory=directory, thing=thing, options=options)
        return cls(
            options=options,
            schema=schema,
            directory=directory,
            thing=thing,
            location=location,
            sign=sign,
        )

    def __getitem__(
        self, key: Union[defaulted_data.Key, tuple[str, int]]
    ) -> defaulted_data.Value:
        """Uses self.thing[item] on internal thing."""
        return self._thing[key]

    def get(self, key: Union[defaulted_data.Key, tuple[str, int]], default: Any) -> Any:
        """Call self.thing.get(key, default)."""
        return self._thing.get(key, default)

    def __setitem__(
        self,
        key: Union[defaulted_data.Key, tuple[str, int]],
        value: Union[defaulted_data.Value, dict[str, defaulted_data.Value]],
    ):
        """Calls self.thing[key] = value"""
        self._thing[key] = value

    def __delitem__(self, key: defaulted_data.Key):
        """Calls del self.thing[key]."""
        del self._thing[key]

    def __contains__(self, key: defaulted_data.Key):
        """Calls key in self.thing."""
        key in self.thing

    def best(self, translated_key: str, **backup: Any):
        """Calls best on self.thing."""
        return self._thing.best(translated_key, **backup)

    @property
    def where(self):
        """Where the thing is as a printable string."""
        return "" if self.location is None else str(self.location)

    @property
    def directory(self) -> str:
        """Directory where information about this thing is saved."""
        return self._directory

    @directory.setter
    def directory(self, new_directory: str):
        """Change directory where information about this thing is saved.

        Move the existing data but does not save the current in-memory data.
        Use save() for that.

        Deletes original directory if it is empty.

        Args:
            new_directory: where the thing data should be saved from now on.
        Raises:
            FileExistsException:
                - if new_directory is a regular file
                - if there are files with the special names for data in the new directory
            (if there is no location saved in this thing and a LOCATION_FILE already exists
            the error is also raised even if currently no data would be overwritten)

        """
        if self._directory == new_directory:
            # nothing to be done
            return
        if os.path.isfile(new_directory):
            raise FileExistsError(
                f"{new_directory} is a regular file. "
                f"Cannot save thing data since it is not a directory."
            )
        if os.path.exists(new_directory):
            # must be directory
            for reserved in constant.RESERVED_FILENAMES:
                if os.path.exists(os.path.join(new_directory, reserved)):
                    raise FileExistsError(
                        f"{os.path.join(new_directory, reserved)} exists. Do not overwrite it."
                    )
        else:
            os.makedirs(new_directory)
        # setting new directory deletes old and creates new file
        self._thing.directory = new_directory
        self._location.directory = new_directory
        self._sign.directory = new_directory
        self._directory = new_directory
        assert self.consistent()
        try:
            os.rmdir(self._directory)
        except (OSError, FileNotFoundError):
            # not empty or not existing
            pass

    def markdown_representation(self):
        """Create representation in Markdown syntax for this thing."""
        sec = self.get(("name", 1), "")
        prim = self.get(("name", 0), sec)
        title = f"- **{prim}**"
        if prim != sec and sec:
            title += f" (**{sec}**)"
        return f"{title}: {self.where}"

    def alt_names_markdown(self):
        """Create markdown lines with references of alternative names.

        Each line is a dictionary entry mapping the alt name to the
        markdown line.
        """
        # if there is a primary name all other names are only in
        # parentheses behind the primary name (see markdown_representation)
        # and therefore not in the correct alphabetical place
        # so add it to alternative names
        prim = self.best("name", backup="")
        return {
            alt_name: f"- **{alt_name}** → {prim} {self.where}"
            for alt_name in filter(
                lambda other_name: other_name and other_name != prim,
                itertools.chain(
                    cast(collections.abc.Mapping, self.get("name", {})).values(),
                    *cast(collections.abc.Mapping, self.get("name_alt", {})).values(),
                ),
            )
        }

    def save(self) -> None:
        """Save all information into a directory.

        If target files already exists, they are overwritten.

        Calling this save should not be really needed since the data
        is saved upon change. But who knows if I missed something.
        Raises:
            yaml.representer.RepresenterError:
                If any data is not safe for yaml writing and was not caught
                by checks in location, sign, thing.
        """
        self._thing.save()
        self._sign.save()
        self._location.save()
