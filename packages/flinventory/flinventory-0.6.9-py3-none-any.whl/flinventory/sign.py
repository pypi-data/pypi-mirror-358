#! /usr/bin/env python
"""Class sign that contains the info for a sign for a thing."""
import itertools

import logging
import os.path

import pathlib
import yaml
from typing import Optional
from typing_extensions import override

from . import constant
from . import defaulted_data


class Sign(defaulted_data.DefaultedDict):
    """Contains info about a sign."""

    def __init__(
        self,
        data: defaulted_data.Data,
        thing: defaulted_data.DefaultedDict,
        options: constant.Options,
        directory: Optional[str],
    ):
        """Create a sign.

        Args:
            data: dict with data, e.g. read from yaml file
            thing: similar structured dict object from which to use data if
                it is not overwritten in data. Useful for the name which is usually
                given by the thing for which this is a sign but can be replaced by a
                different version of the name in data
            options: languages and other inventory-wide options
            directory: directory where to save this sign data when changed.
                The file where the data is saved is directory/{constant.SIGN_FILE}
                If None, it not saved. (Can be set later to save.)
        """
        self._directory = None  # to avoid saving during initialisation
        for source, target in [
            ("fontsize_de", ("fontsize", "de")),
            ("fontsize_en", ("fontsize", "en")),
            ("fontsize_main", ("fontsize", "de")),
            ("fontsize_secondary", ("fontsize", "en")),
        ]:
            try:
                data[target] = data[source]
                del data[source]
                # could throw exception if source was in default but probably will never happen
            except KeyError:
                pass  # fine, not there
        super().__init__(
            data=data,
            default=thing,
            non_defaulted=["width", "height", "printed", "landscape", "fontsize"],
            lists=thing.lists,
            translated=thing.translated + ("fontsize",),
            default_order=itertools.chain(
                thing.default_order,
                (
                    "width",
                    "height",
                    "location_shift_down",
                    "fontsize",
                    "printed",
                ),
            ),
            options=options,
        )
        self._logger = logging.getLogger(__name__)
        self._directory = directory

    @property
    def directory(self) -> Optional[str]:
        """The directory in which the sign data file is saved.

        None if data is not saved.
        """
        return self._directory

    @directory.setter
    def directory(self, new_directory: Optional[str]):
        """Set the directory in which the data file is saved.

        Save the data there if it is not None.
        The old data file is removed.
        """
        pathlib.Path(os.path.join(self._directory, constant.SIGN_FILE)).unlink(
            missing_ok=True
        )
        self._directory = new_directory
        self.save()

    def printable(self) -> bool:
        """True if width and height are given."""
        return "width" in self and "height" in self

    def should_be_printed(self) -> bool:
        """True if printable and not printed."""
        return self.printable() and not bool(self.get("printed", False))

    def save(self):
        """Save data to yaml file.

        Do not check if something is overwritten.

        Delete file if no data is there to be written.

        If self.directory is None, do nothing.
        Todo: include git add and commit.
        """
        if self._directory is None:
            return
        jsonable_data = self.to_jsonable_data()
        path = pathlib.Path(os.path.join(self._directory, constant.SIGN_FILE))
        if not jsonable_data:
            if path.is_file():
                self._logger.info(f"Delete {path}")
            path.unlink(missing_ok=True)
        else:
            os.makedirs(self._directory, exist_ok=True)
            with open(path, mode="w", encoding="utf-8") as sign_file:
                yaml.dump(
                    self.to_jsonable_data(), sign_file, **constant.YAML_DUMP_OPTIONS
                )
            self._logger.info(
                f"Saved {self.get(('name', 0), self._directory)} sign to {path}."
            )

    @override
    def __setitem__(self, key, value):
        """self[key] = value as in DefaultedDict but saved afterward."""
        super().__setitem__(key, value)
        self.save()

    @override
    def __delitem__(self, key):
        """del self[key] as in DefaultedDict but saved afterward."""
        super().__delitem__(key)
        self.save()

    @classmethod
    def from_yaml_file(
        cls,
        directory: str,
        thing: defaulted_data.DefaultedDict,
        options: constant.Options,
    ):
        """Create a sign from data in a file.

        Args:
            directory: directory with sign file
            thing: thing for which this is a sign. Used as default data.
            options: inventory-wide options
        """
        path = pathlib.Path(os.path.join(directory, constant.SIGN_FILE))
        try:
            sign_file = open(path, mode="r", encoding="utf-8")
        except FileNotFoundError:
            return cls({}, thing, options, directory)
        with sign_file:
            return cls(yaml.safe_load(sign_file), thing, options, directory)
