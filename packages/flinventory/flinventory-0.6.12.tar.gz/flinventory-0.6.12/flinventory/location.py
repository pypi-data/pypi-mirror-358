"""Locations as specified (by example) in locations.json.

The schema how locations are hierachically defined is defined in
locations.json.

Recognised keys are:
- seperator (str)
- schema (dict)
  - name      (str|int) : what this location is called
  - shortcut  (str|int) : how this location is called in a short location string
  - levelname (str) : key for specifying subelements
  - default   (str) : name of default subelement. This is only used to help UIs to suggest
                      something. It is not used to fill missing data.
  - subs      (dict): same information for the subelements (a list of schemas)
                      if non-existing, all names are accepted
  - subschema (dict): information given to all subelements
- locations (dict): where the things are
  - keys      (str) : given by levelname
  - values    (str|int): the possible values given by the keys in the
                         subs Schema or any value if no subs are given
"""

import logging

import pathlib

from typing import Any, Union, Optional, Self, Literal
import os.path
import yaml

from . import constant

Value = Union[str, int, float, bool]
"""Valid level specifier types (values in location dict)."""


class InvalidLocationSchema(Exception):
    """Raised if the schema is invalid.

    Should be raised "from" the original exception.
    """


class InvalidLocation(Exception):
    """Raised if a location is invalid.

    Should be raised "from" the original exception.
    """


class Schema:
    """Schema as described in module docstring, possibly with sub-schemas.

    Not yet possible: creation of json based on Schema.
    Do not know if I might need that.
    """

    def __init__(self, json_content: dict[str, Any]):
        """Create schema with sub schemas."""
        # just save it to be able to give it back
        self.json = json_content
        try:
            self._name = json_content["name"]
        except KeyError as key_error:
            raise InvalidLocationSchema("Name is mandatory for schema.") from key_error
        self._name = (
            self._name.strip() if isinstance(self._name, str) else int(self._name)
        )
        if self._name == "":
            raise InvalidLocationSchema(
                "A schema name must not be the empty/ a pure whitespace string."
            )
        try:
            self._shortcut = json_content["shortcut"]
        except KeyError:
            self._shortcut = (
                self._name[0] if isinstance(self._name, str) else int(self._name)
            )
        self._levelname = json_content.get("levelname", None)
        self._default = json_content.get("default", None)
        if isinstance(self._default, str):
            self._default = self._default.strip()
            if self._default == "":
                raise InvalidLocationSchema(
                    "A default subschema key must not be the empty string."
                )
        if self._levelname is None and self._default is not None:
            raise InvalidLocationSchema(
                "A default subschema makes no sense if no levelname is given."
            )
        self._sub_schema_default, self._subs = self._initialise_subs(json_content)
        if self._levelname is None and self._subs is not None:
            raise InvalidLocationSchema(
                f"If sub schemas for {self._name} are mentioned, "
                "also a levelname is necessary "
                "to specify the subschema."
            )

    @classmethod
    def _initialise_subs(
        cls, json_content: dict[str, Any]
    ) -> tuple[dict[str, Any], Optional[list[Self]]]:
        """Read sub element information and return info accordingly.

        Returns:
            - sub_schema_default
            - subs
        """
        sub_schema_default = json_content.get("subschema", {})
        try:
            if "name" in sub_schema_default or "shortcut" in sub_schema_default:
                raise InvalidLocationSchema(
                    "It does not make sense to give all "
                    "sub elements the same name or shortcut."
                )
        except TypeError as typeerror:
            # mainly check this here to make pylint happy with the "in" statements
            raise InvalidLocationSchema("subschema must be a dict.") from typeerror
        subs = None
        try:
            sub_element_list = json_content["subs"]
        except KeyError:
            pass
        else:
            subs = []
            try:
                sub_element_iter = iter(sub_element_list)
            except TypeError as typeerror:
                raise InvalidLocationSchema(
                    "subs contains something that is not a list"
                ) from typeerror
            for sub_element in sub_element_iter:
                if isinstance(sub_element, (str, int)):
                    subs.append(cls(sub_schema_default | {"name": sub_element}))
                elif isinstance(sub_element, dict):
                    subs.append(cls(sub_schema_default | sub_element))
                else:
                    raise InvalidLocationSchema(
                        'Elements of list in "subs" must be '
                        "str, int (name) or dict (schema)."
                    )
            assert len(subs) == len(sub_element_list)
        return sub_schema_default, subs

    def get_subschema(self, key: str | int) -> Self:
        """Get the subschema for the given key.

        If subs are given, first their names are checked for a match,
        then their shortcuts.
        Otherwise, a generic schema based on the default schema is given.
        Then all keys are accepted.
        """
        if self._subs is None:
            return type(self)(self._sub_schema_default | {"name": key})
        suitably_named_subs = [sub for sub in self._subs if sub.name == key]
        if len(suitably_named_subs) == 1:
            return suitably_named_subs[0]
        if len(suitably_named_subs) > 1:
            raise InvalidLocationSchema(
                f"{self._levelname} has the name " f"{key} twice in subschemas."
            )
        suitably_named_subs = [sub for sub in self._subs if sub.shortcut == key]
        if len(suitably_named_subs) == 1:
            return suitably_named_subs[0]
        if len(suitably_named_subs) > 1:
            raise InvalidLocationSchema(
                f"{self._levelname} has the shortcut " f"{key} twice in subschemas."
            )
        raise InvalidLocation(
            f"The key {key} is not a valid subschema "
            f"for {self._name} (levelname: {self._levelname}.)"
        )

    @property
    def name(self) -> str | int:
        """Get the shortcut used in location strings."""
        return self._name

    @property
    def shortcut(self) -> str | int:
        """Get the shortcut used in location strings."""
        return self._shortcut

    @property
    def levelname(self) -> str:
        """Get levelname, which is the key in locations to specify the subschema.

        Raises:
            InvalidLocation if no subschemas are allowed due to missing levelname.
        """
        if self._levelname is None:
            raise InvalidLocation(f"The schema {self._name} has no levelname.")
        return self._levelname

    def get_schema_hierarchy(self, location_info: dict[str, Any]) -> list[Self]:
        """Return a list of nested schemas for this location starting with this.

        Default values are ignored.
        """
        if (
            self._levelname is None  # this schema has no subelements
            # no sub is given and no default is set
            or self._levelname not in location_info
            # sub is explicitly set to None
            or (
                self._levelname in location_info
                and location_info[self._levelname] is None
            )
        ):
            return [self]
        return [self] + self.get_subschema(
            location_info[self._levelname]
        ).get_schema_hierarchy(location_info)

    def get_valid_subs(
        self, shortcuts: Literal["yes", "only", "()", "*", "no"] = "yes"
    ) -> Optional[list[Union[str, int]]]:
        """A list of valid sub schemas. Usable for suggesting options.

        Args:
            shortcuts: if valid shortcuts should be listed as well:
                'no': shortcuts are not listed
                'yes': shortcuts listed in the same way as names,
                'only': only shortcuts are listed
                '()': shortcuts are listed in parentheses after the name (note: result
                    elements are not valid values)
                '*': shortcuts are marked with ** ** if they are in the name, otherwise like '()'
        Return:
            None if no levelname is given,
            an empty list if everything is valid
        """
        if self._levelname is None:
            return None
        if self._subs is None:
            return []
        if shortcuts == "no":
            return [sub.name for sub in self._subs]
        if shortcuts == "yes":
            return [name for sub in self._subs for name in (sub.name, sub.shortcut)]
        if shortcuts == "only":
            return [sub.shortcut for sub in self._subs]
        if shortcuts == "()":
            return [f"{sub.name} ({sub.shortcut})" for sub in self._subs]
        if shortcuts == "*":
            return [
                (
                    (
                        f"{str(sub.name)[:str(sub.name).index(str(sub.shortcut))]}"
                        f"**{sub.shortcut}**"
                        + str(sub.name)[
                            str(sub.name).index(str(sub.shortcut))
                            + len(str(sub.shortcut)) :
                        ]
                    )
                    if str(sub.shortcut) in str(sub.name)
                    else f"{sub.name} ({sub.shortcut})"
                )
                for sub in self._subs
            ]
        raise ValueError('shortcuts needs to be one of "yes", "only", "()", "*"')

    @classmethod
    def from_file(cls, directory):
        """Read schema from SCHEMA_FILE in directory.

        If file does not exist, create empty schema.
        """
        try:
            schema_file = open(os.path.join(directory, constant.SCHEMA_FILE))
        except FileNotFoundError:
            return cls({"name": "Workshop"})
        return cls(yaml.safe_load(schema_file))


class Location(dict[str, Value]):
    """A location for stuff. Member var definition in schema.

    Values are accessed with dict member notation. `loc["shelf"] = 5`

    Attributes:
        _schema: schema defining the meaning of the keys
        _levels: list of schemas for all levels of the location hierarchy
        options: global options including the seperator
    """

    EMPTY: list[Any] = [None, "", [], {}]
    """Values that are considered empty and mean that nothing should be saved."""

    def __init__(
        self,
        schema: Schema,
        data: dict[str, Value],
        directory: str,
        options: constant.Options,
    ):
        """Create a location from data and the schema.

        schema: location schema
        data: location data as a dict
        directory: where to save this location to (saved to directory/{constant.LOCATION_FILE})
        options: general inventory options (separator is used)
        """
        self._directory = None  # no autosave during initialisation
        super().__init__(data)
        self.options = options
        self._directory = directory
        self._logger = logging.getLogger(__name__)
        self._schema = schema
        self._levels = self._schema.get_schema_hierarchy(self)
        self.canonicalize()

    def _shortcut(self):
        """Get string representation with shortcuts."""
        return self.options.separator.join(
            str(level.shortcut) for level in self._levels
        )

    @property
    def long_name(self):
        """Get the string representation with names."""
        return self.options.separator.join(str(level.name) for level in self._levels)

    @property
    def schema(self) -> Schema:
        """Return the schema given in the location file used to define this location.

        Please do not alter.
        """
        return self._schema

    def __str__(self):
        """Get string representation of the location.

        Uses the schema and the seperator.

        Assumes that the schema is valid.

        Raises:
            InvalidLocation: if the location info do not suit
            the schema
        Returns:
            shortcuts for places separated by
            seperator given at initialisation
            Can be an empty string if the top-level schema
            is not present or None.
        """
        return self._shortcut()

    def to_sortable_tuple(self):
        """Return the data of this location as sortable tuple."""
        return (level.name for level in self._levels)

    def canonicalize(self):
        """Replace shortcuts by entire names."""
        for index, level in list(enumerate(self._levels))[:-1]:
            # use super() because with self[key] = ... we get an infinite recursion:
            super().__setitem__(level.levelname, self._levels[index + 1].name)

    def __setitem__(self, level: str, value: Value) -> None:
        """Set one level info.

        Or deletes it if it's None or "" or [] or {} (see EMPTY)

        Update internal info.
        """
        if value in self.EMPTY:
            if level in self:
                del self[level]
        else:
            super().__setitem__(level, value)
        self._levels = self._schema.get_schema_hierarchy(self)
        if self._directory is not None:
            self.save()

    def __delitem__(self, key: str) -> None:
        """Deletes one information.

        Update internal info.
        """
        super().__delitem__(key)
        self._levels = self._schema.get_schema_hierarchy(self)
        if self._directory is not None:
            self.save()

    def __bool__(self):
        """True if something is saved."""
        return bool(super())

    def save(self):
        """Save location data to yaml file."""
        path = pathlib.Path(os.path.join(self._directory, constant.LOCATION_FILE))
        if len(self) > 0:  # not empty?
            os.makedirs(self._directory, exist_ok=True)
            with open(path, mode="w", encoding="utf-8") as location_file:
                yaml.dump(
                    data=self.to_jsonable_data(),
                    stream=location_file,
                    **constant.YAML_DUMP_OPTIONS,
                )
            self._logger.info(f"Saved {self.directory} location to {path}.")
        else:
            if path.is_file():
                self._logger.info(f"Delete {path}")
            path.unlink(missing_ok=True)

    def to_jsonable_data(self) -> dict[str, Value]:
        """Convert to dict with levelnames as keys.

        Sorts by schema hierarchy.
        """
        self._levels = self.schema.get_schema_hierarchy(self)
        as_dict: dict[str, Value] = {
            level.levelname: self._levels[index + 1].name
            for index, level in list(enumerate(self._levels))[:-1]
        }
        for key in self:
            as_dict.setdefault(key, self[key])
        return as_dict

    @classmethod
    def from_yaml_file(cls, directory: str, schema: Schema, options: constant.Options):
        """Create location from yaml file.

        Args:
            directory: file is directory/{constant.LOCATION_FILE}
            schema: location schema for interpreting the data
            options: inventory-wide options, in particular separator
        """
        path = pathlib.Path(os.path.join(directory, constant.LOCATION_FILE))
        try:
            location_file = open(path, mode="r", encoding="utf-8")
        except FileNotFoundError:
            return cls(schema=schema, data={}, directory=directory, options=options)
        with location_file:
            data = yaml.safe_load(location_file)
            return cls(
                schema=schema,
                data=data,
                directory=directory,
                options=options,
            )

    @property
    def directory(self) -> Optional[str]:
        """The directory in which the location data file is saved.

        If none, changes are not saved.
        """
        return self._directory

    @directory.setter
    def directory(self, new_directory):
        """Set the directory in which the data file is saved.

        Save the data there.
        The old data file is removed.
        """
        pathlib.Path(os.path.join(self._directory, constant.LOCATION_FILE)).unlink(
            missing_ok=True
        )
        self._directory = new_directory
        self.save()
