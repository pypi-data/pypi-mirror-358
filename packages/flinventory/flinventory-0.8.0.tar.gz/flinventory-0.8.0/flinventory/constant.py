#!/usr/bin/env python
"""Collection of constants.

By extracting it into a file that is not importing any other one,
this can be imported everywhere without circular import problem.
"""
import os.path

from typing import Any, Self, Union, Optional
import yaml
import pycountry

try:
    import slugify
except ModuleNotFoundError:
    print(
        "module slugify not found. "
        "Install it system-wide or create a conda environment "
        "with the environment.yml named bikeparts "
        "or a virtual environment with the necessary packages liste in environment.yml."
    )
    import sys

    sys.exit(1)

VALID_LANGUAGES = {}
for gl_language in pycountry.languages:
    try:
        VALID_LANGUAGES[gl_language.alpha_2] = gl_language
    except AttributeError:
        VALID_LANGUAGES[gl_language.alpha_3] = gl_language


class InvalidLanguageError(Exception):
    """Raised if an invalid language code is used."""


SCHEMA_FILE = "schema.yaml"
"""File name of the schema."""

OPTION_FILE = "preferences.yaml"
"""File name of the preferences."""

THING_DIRECTORY = "things"
"""Directory within the main data directory with a directory for every thing"""
THING_FILE = "thing.yaml"
"""File name for thing (non-localised information) data in directory for a single thing."""
LOCATION_FILE = "location.yaml"
"""File name for location data in directory for a single thing."""
SIGN_FILE = "sign.yaml"
"""File name for sign data in directory for a single thing."""
IMAGE_FILE_BASE = "image"
"""File base name (without extension) for image file."""
IMAGE_FILE_TYPES = ["jpg", "png", "jpeg", "PNG", "JPG", "JPEG", "webp"]
"""All supported image file types."""
RESERVED_FILENAMES = {THING_FILE, LOCATION_FILE, SIGN_FILE} | {
    IMAGE_FILE_BASE + filetype for filetype in IMAGE_FILE_TYPES
}
"""List of all reserved file names in a thing data directory."""
DISPLAY_RESOURCES = "website_resources"
"""The directory within main_data_directory with the favicon and possibly more data for UIs."""

YAML_DUMP_OPTIONS = {
    "Dumper": yaml.SafeDumper,
    "sort_keys": False,
    "allow_unicode": True,
    "indent": 2,
}
"""Options for dumping to yaml files. Should be the same everywhere."""


def normalize_file_name(file_name: str) -> str:
    """Normalize a string such that it is a file name that makes no problems."""
    return slugify.slugify(
        file_name,
        separator="_",
        # allow . in file name:
        regex_pattern=r"[^-a-z0-9_.]+",
        replacements=[
            ["Ü", "Ue"],
            ["ü", "ue"],
            ["Ä", "Ae"],
            ["ä", "ae"],
            ["Ö", "Oe"],
            ["ö", "oe"],
            ["ẞ", "Ss"],
            ["ß", "ss"],
        ],
    ).replace(
        ".jpeg", ".jpg"
    )  # this replacement after slugify
    # to also replace JPEG by jpg (slugify lowers)


class Options:
    """Collections of kinda global options.

    The following **class** members are just for documentation. There are never
    filled or intended to be used but instead the **instance** members of the same name.

    Maybe one could use the class members and not pass the options object around
    but instead refer to the class and its members. But then it would be a huge hassle
    to support for different options in the same program in case one ever wants that.
    """

    separator: str
    """How different parts of location shortcuts are separated."""

    languages: list[str]
    """Language codes in order of preference.

    The corresponding language can be found in VALID_LANGUAGES.
    """

    main_data_directory: str
    """The directory with all data."""

    length_unit: str
    """length unit (preferably mm) for all lengths, mainly sign size.

    For backwards compatibility, the default is cm (centimeter).

    Should be a length unit that LaTeχ understands.
    """

    sign_max_width: float
    """Maximum width for a sign in length_unit.

    Should be set if length_unit is set to fit to it.
    By default 18 which in cm fits to A4 portrait page.
    """

    sign_max_height: float
    """Maximum height for a sign in length_unit.

    Should be set if length_unit is set to fit to it.
    By default 28 which in cm fits to A4 portrait page.
    """

    @classmethod
    def from_file(cls, directory: str = ".") -> Self:
        """Parse options from the options file.

        No possibility to set the config file. Convention over customization!
        Args:
            directory: the directory in which to find the config file
        """
        try:
            option_file = open(
                os.path.join(directory, OPTION_FILE), mode="r", encoding="utf-8"
            )
        except FileNotFoundError:
            return cls({"main_data_directory": directory})
        with option_file:
            return cls(yaml.safe_load(option_file) | {"main_data_directory": directory})

    def __init__(self, options: dict[str, Any]):
        """Create options from content of option file."""
        self.languages = options.get("languages", ["de", "en"])
        if isinstance(self.languages, str):
            self.languages = [self.languages]
        if not isinstance(self.languages, list):
            raise ValueError(
                "Language codes must be a list of strings of "
                "valid language codes or a single valid language code."
            )
        for language in self.languages:
            if language not in VALID_LANGUAGES:
                raise ValueError(
                    f"{language} is not a valid language code. "
                    f"Valid language codes are {VALID_LANGUAGES}."
                )
        if not self.languages:
            # empty list
            raise ValueError("We need to use at least one language.")

        for simple_option, default, data_type in (
            ("separator", "-", str),
            ("long_separator", " > ", str),
            ("length_unit", "cm", str),
            ("sign_max_height", 28, (int, float)),
            ("sign_max_width", 18, (int, float)),
        ):
            vars(self)[simple_option] = options.get(simple_option, default)
            if not isinstance(vars(self)[simple_option], data_type):
                raise ValueError(
                    f"{simple_option} unit must a {data_type}, "
                    f"not {vars(self)[simple_option]} "
                    f"of type {type(vars(self)[simple_option])}"
                )

        self.main_data_directory = options.get("main_data_directory", ".")

    def to_yaml(self) -> None:
        """Write options to options file.

        Overwrites existing options file. Therefore, delete all invalid options
        and add all defaults.
        """
        with open(
            os.path.join(self.main_data_directory, OPTION_FILE),
            mode="w",
            encoding="utf-8",
        ) as option_file:
            yaml.dump(
                {
                    "separator": self.separator,
                    "languages": self.languages,
                    "length_unit": self.length_unit,
                    "sign_max_height": self.sign_max_height,
                    "sign_max_width": self.sign_max_width,
                },
                option_file,
                **YAML_DUMP_OPTIONS,
            )


def merge_lists(orig: list[Any], additional: list[Any]) -> list[Any]:
    """Add all elements of additional to orig that are not in there yet.

    Duplicates in orig and additional individually are preserved.
    """
    return orig + [element for element in additional if element not in orig]


def fix_deprecated_language_keys(
    data: dict[str, Any], options: Options, delimiter: str = "_"
) -> None:
    """Change language suffixes into subelements.

    Deprecated. Probably does not work anymore.

    For each key xyz_LA move data["xyz_LA"] into data["xyz"]["LA"]
    where LA is a recognized language suffix.

    If the value is a list, merge it with an existing list.

    Args:
        data: dictionary that is changed
        options: options including the language suffixes
        delimiter: what splits the language from the actual key
    Raises:
        ValueError: if I would overwrite data. The keys that are processed
        before the error are changed. (Yes, this is a bug.)
    """
    for key in data:
        if any(key.endswith(f"{delimiter}{LA}") for LA in options.languages):
            new_key, language = key.rsplit(delimiter, 1)
            if new_key in data:
                if not isinstance(new_key, dict):
                    raise ValueError(
                        f"{new_key} has no support for languages, "
                        f"cannot insert {key}: {data[key]}"
                    )
                if data[new_key][language] == data[key]:
                    # already there
                    del data[key]
                elif isinstance(data[new_key][language], list):
                    if isinstance(data[key], list):
                        data[new_key][language] = merge_lists(
                            data[new_key][language], data[key]
                        )
                    else:
                        data[new_key][language].append(data[key])
                    del data[key]
                elif isinstance(data[new_key][language], dict):
                    raise NotImplementedError(
                        "Inserting into dictionaries at level 2 not supported."
                    )
                elif isinstance(data[key], (str, int, float, bool)):
                    raise ValueError(
                        f"Value {data[new_key][language]} for key {new_key} in {language} "
                        f"would be overwritten by value {data[key]} for key {new_key}."
                    )
                else:
                    raise NotImplementedError(
                        "Did not think of this possibility of"
                        f"key = {key}, "
                        f"value = {data[key]}, "
                        f"type = {type(data[key])}, "
                        f"new_key = {new_key}, "
                        f"language = {language}, "
                        f"existing value = {data[key][language]}, "
                    )
            # else: new_key not in data
            data[new_key] = {language: data[key]}


class MissingProgramError(OSError):
    """Error raised if an external program is called that does not exist."""

    def __init__(self, program_name: str, *args):
        """Create a MissingProgramError.

        Args:
            program_name: the name of the missing program
            see OSError
        """
        super().__init__(*args)
        self.program_name = program_name
