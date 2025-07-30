#!/usr/bin/env python
"""A thing in an inventory."""
import logging
import os.path
import pathlib
from typing import override, Optional
import yaml

from . import constant
from . import defaulted_data


class Thing(defaulted_data.DefaultedDict):
    """A thing in an inventory.

    In addition to the functionality of DefaultedDict,
    a thing has specific list and translated keys
    and save and open from file functionality.
    """

    def __init__(
        self,
        data: defaulted_data.Data,
        default: defaulted_data.Data,
        options: constant.Options,
        directory: str,
    ):
        """Create a new thing from some data.

        Args:
            data: data specific to this thing
            default: default values as in DefaultedDict
            options: inventory-wide options,
            directory: where to save data of this thing
        """
        self._directory = None  # None signals: no save
        super().__init__(
            data=data,
            default=default,
            non_defaulted=tuple(),
            translated=("name", "name_alt", "description"),
            lists=("name_alt", "part_of", "subclass_of"),
            default_order=("name", "name_alt", "part_of", "category", "url"),
            options=options,
        )
        self._directory = directory
        self._logger = logging.getLogger(__name__)

    @property
    def directory(self):
        """The directory in which the thing data file is saved."""
        return self._directory

    @directory.setter
    def directory(self, new_directory: str):
        """Set the directory in which the data file is saved.

        Save the data there.
        The old data file is removed.
        """
        if self._directory is not None:
            pathlib.Path(os.path.join(self._directory, constant.THING_FILE)).unlink(
                missing_ok=True
            )
        assert new_directory is not None
        self._directory = new_directory
        self.save()

    @override
    def __setitem__(self, key, value):
        """self[key] = value as in DefaultedDict but saved afterward."""
        super().__setitem__(key, value)
        if self._directory is not None:
            self.save()

    @override
    def __delitem__(self, key):
        """del self[key] as in DefaultedDict but saved afterward."""
        super().__delitem__(key)
        if self._directory is not None:
            self.save()

    def image_path(self) -> Optional[str]:
        """Path to the image of the thing, if it exists.

        If path is given and relative, it is assumed
        that it is relative to my directory.
        If it has no extension, try finding it with extension.
        Returns:
            If image is explicitly given, use this.
            Otherwise, look in my directory for a suitably
            named file with one of the image extensions.
            Is relative path if my directory is relative.
            None if no image was found.
        """
        path_base = self.get("image", constant.IMAGE_FILE_BASE)
        if not os.path.isabs(path_base):
            path_base = os.path.join(self.directory, path_base)
        for extension in ("", *(f".{ext}" for ext in constant.IMAGE_FILE_TYPES)):
            if os.path.isfile(path := path_base + extension):
                return path
        return None

    @classmethod
    def from_yaml_file(
        cls, directory: str, default: defaulted_data.Data, options: constant.Options
    ):
        """Create a thing from data in a file.

        Args:
            directory: directory with sign file
            default: thing for which this is a sign. Used as default data.
            options: inventory-wide options
        """
        path = pathlib.Path(os.path.join(directory, constant.THING_FILE))
        try:
            thing_file = open(path, mode="r", encoding="utf-8")
        except FileNotFoundError:
            logging.getLogger(__name__).warning(f"{path} not found. That is unusual.")
            return cls({}, default, options, directory)
        with thing_file:
            return cls(yaml.safe_load(thing_file), default, options, directory)

    def save(self):
        """Save data to yaml file.

        Do not check if something is overwritten.

        Delete file if no data is there to be written.
        Todo: include git add and commit.
        Raises:
            TypeError: if directory is None
        """
        jsonable_data = self.to_jsonable_data()
        path = pathlib.Path(os.path.join(self._directory, constant.THING_FILE))
        if not jsonable_data:
            if path.is_file():
                self._logger.info(f"Delete {path}")
            path.unlink(missing_ok=True)
        else:
            os.makedirs(self._directory, exist_ok=True)
            with open(path, mode="w", encoding="utf-8") as thing_file:
                yaml.dump(jsonable_data, thing_file, **constant.YAML_DUMP_OPTIONS)
            self._logger.info(
                f"Saved {self.get(('name', 0), self._directory)} sign to {path}."
            )
