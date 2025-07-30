#!/usr/bin/env python3
"""Collection of function to clean up data.

Also used for storing code that might be useful
for cleaning data but is not in use right now."""

import argparse
import json
import os
import logging

import yaml

from . import constant
from . import inventory_io
from .box import BoxedThing


SHORTCUTS = {
    "sq": (18, 10),
    "sqtp": (6.5, 6.5),
    "rectp": (8.5, 5.5),
    "sb": (5.9, 1.6),
    "es": (30, 10),
    "ef": (9, 6.5),
    "wd": (6, 2.1),
}
"""Shortcuts for sign sizes.

"s": "width height"
"s": "sq" -> square (bigger) cardboard box: 18 x 10
"s": "sqtp" -> square Tetrapak: 6.5 x 6.5
"s": "rectp" -> rectangular Tetrapak: 8.5 x 5.5
"s": "sb" -> Schäferbox mit Einsteckhalterung: 6.0x1.4 cm
"s": "es" -> Eurokiste lange Seite (groß): 30 x 10 cm
"s": "ef" -> Eurokiste kurze Seite (zum Einstecken): 9 x 6.5
"s": "wd" -> kleine weiße Döschen: 6 x 2.1 cm
"""

LOGGER = logging.getLogger(__name__)


def add_arg_parsers(subparsers):
    """Add command line options to support the datacleanup functionality.

    Args:
        subparsers: object to add sub parsers to
    """

    parser_example = subparsers.add_parser(
        "example", description="This command does nothing"
    )
    parser_example.add_argument(
        "--verbose", "-v", action="count", help="Also this option does nothing."
    )
    parser_example.set_defaults(func=example_action)

    parser_normalize = subparsers.add_parser(
        "normalize",
        description=(
            "read thing list and write it"
            " so that further automatic"
            " alterations make smaller diffs"
        ),
    )
    parser_normalize.set_defaults(func=normalize_thing_list)

    parser_printed = subparsers.add_parser(
        "printed",
        description=(
            'Add the "printed" attribute'
            + " to all things that have sign info so that they"
            + " are not printed next time."
        ),
    )
    parser_printed.set_defaults(func=add_printed)

    parser_shortcutreplacement = subparsers.add_parser(
        "shortcut",
        description=(
            "Replace shortcut 's': " + "'width height' by " + "appropriate values."
        ),
    )
    parser_shortcutreplacement.set_defaults(func=convert_shortcuts)

    parser_unprinted = subparsers.add_parser(
        "unprinted", description='Remove the "printed" attribute from all things.'
    )
    parser_unprinted.set_defaults(func=remove_printed)

    parser_use_ids = subparsers.add_parser(
        "useIDs", description="Replace names in thing references by their IDs."
    )
    parser_use_ids.set_defaults(func=use_ids)

    parser_locations_file = subparsers.add_parser(
        "locationsFile",
        description="Add locations from a locations.yaml file to their things.",
    )
    parser_locations_file.set_defaults(func=convert_locations_file)


def example_action(args):
    """Does nothing.

    Is an example for a function that is called via a subparser.
    """
    LOGGER.debug(f"Example action: counted: {args.verbose}")


def normalize_thing_list(args):
    """Read thing list and write it again."""
    things = inventory_io.Inventory.from_json_files(directory=args.dataDirectory)
    things.save()


def use_ids(args):
    """Read thing list, replace references in 'part_of' to other things by their ids and write.

    Note that if 'part_of' values are given by a default value (e.g. from wikidata data),
    it is still "replaced" in the main thing. Maybe this is what we want, maybe not.

    Only replace if ids for all elements of 'part_of' lists are found.
    Otherwise, log warning.
    """
    things = inventory_io.Inventory.from_json_files(directory=args.dataDirectory)
    for thing in things:
        try:
            parents = thing["part_of"]
        except KeyError:
            continue
        parent_ids = []
        for parent_name in parents:
            # first check if it is already an id
            try:
                things.get_by_id(parent_name)
            except KeyError:
                # expected
                pass
            else:
                parent_ids.append(parent_name)
                continue
            # otherwise search by name:
            possible_parents = list(things.get_by_best("name", parent_name))
            if len(possible_parents) == 1:
                parent_ids.append(things.get_id(possible_parents[0]))
            elif len(possible_parents) == 0:
                logging.getLogger("datacleanup: use_ids").warning(
                    f"Got no thing with name {parent_name}."
                )
                break
            else:
                logging.getLogger("datacleanup: use_ids").warning(
                    f"Got several things with name {parent_name}."
                )
                break
        else:
            # if no break was encountered, all parent_names could be matched
            assert len(parent_ids) == len(parents), (
                "No error was noticed but a parent got lost for "
                f'{thing.best("name")} from {parents} to {parent_ids}.'
            )
            thing["part_of"] = parent_ids
    print("Should all be saved, but do it again.")
    things.save()


def add_printed(args):
    """Add to all things the attribute printed=True."""

    def add_printed_once(thing: BoxedThing) -> None:
        if thing.sign.should_be_printed():
            thing.sign["printed"] = True

    transform_all(args, add_printed_once)


def remove_printed(args):
    """Remove the attribute printed on all things."""

    def remove(thing: BoxedThing):
        try:
            del thing.sign["printed"]
        except KeyError:
            pass

    transform_all(args, remove)


def convert_shortcuts(args):
    """Convert the shortcuts to correct fields."""

    def replace_shortcut(thing: BoxedThing) -> None:
        try:
            value = thing.sign["s"]
        except KeyError:
            return  # no change
        if value in SHORTCUTS:
            thing.sign["width"] = SHORTCUTS[value][0]
            thing.sign["height"] = SHORTCUTS[value][1]
            del thing.sign["s"]
            return
        try:
            width, height = thing.sign["s"].split()
        except AttributeError:
            LOGGER.warning(
                f"Thing {thing.best('name', backup='?')} has attribute sign['s'] but it is not a string."
            )
            return
        except ValueError:
            LOGGER.warning(
                f"Thing {thing.best('name')} has attribute sign['s'] "
                f"but it is not exactly two items separated by space."
            )
            return
        try:
            width = int(width)
            if width <= 0:
                raise ValueError()
        except ValueError:
            try:
                width = float(width)
                if width <= 0:
                    raise ValueError()  # pylint: disable=raise-missing-from
            except ValueError:
                LOGGER.warning(
                    f"width {width} in thing {thing.best("name")} is not a positive number"
                )
                return
        try:
            height = int(height)
            if height <= 0:
                raise ValueError()
        except ValueError:
            try:
                height = float(height)
                if height <= 0:
                    raise ValueError()  # pylint: disable=raise-missing-from
            except ValueError:
                LOGGER.warning(
                    f"height {height} in thing {thing.best('name')} is not a positive number"
                )
                return
        thing.sign["width"] = width
        thing.sign["height"] = height
        del thing.sign["s"]
        assert "width" in thing.sign
        assert "height" in thing.sign
        assert "s" not in thing.sign

    transform_all(args, replace_shortcut)


def convert_locations_file(args):
    """Reads a deprecated locations.yaml file and adds the locations to the things.

    Assumes that the things are already split into one thing.yaml file per thing.

    The locations file must be called `locations.json` or `locations.yaml`.

    The schema in locations.json/yaml is dumped into the schema file if there is
    no schema file yet.
    """
    inventory = inventory_io.Inventory.from_json_files(args.dataDirectory)
    try:
        locations_file = open(os.path.join(args.dataDirectory, "locations.json"))
    except FileNotFoundError:
        try:
            locations_file = open(os.path.join(args.dataDirectory, "locations.yaml"))
        except FileNotFoundError:
            print("No locations.json file found. Do nothing.")
            return
        else:
            print("Use data from locations.yaml")
            data = yaml.safe_load(locations_file)
    else:
        print("Use data from locations.json.")
        data = json.load(locations_file)

    for key, location_dict in data.get("part_locations", data["locations"]).items():
        possible_things = list(inventory.get_by_best("name", key))
        if len(possible_things) == 1:
            thing = possible_things[0]
            for loc_key, value in location_dict.items():
                if loc_key.startswith("sign_"):
                    if loc_key.endswith("_de"):
                        thing.sign[loc_key[5:-3], "de"] = value
                    elif loc_key.endswith("_en"):
                        thing.sign[loc_key[5:-3], "en"] = value
                    else:
                        thing.sign[loc_key[5:]] = value
                else:
                    thing.location[loc_key] = value
        elif len(possible_things) == 0:
            logging.error(f"No thing found with name {key}")
        else:
            logging.error(f"{len(possible_things)} found with name {key}.")

    # inventory.save() # should not be necessary

    if not os.path.exists(
        schema_path := os.path.join(args.dataDirectory, constant.SCHEMA_FILE)
    ):
        with open(schema_path, mode="w") as schema_file:
            yaml.dump(data["schema"], schema_file, **constant.YAML_DUMP_OPTIONS)


def add_attribute_if(args, attribute, condition=lambda thing: True):
    """Add an attribute to all things that fulfill the condition.

    Can only add attributes to thing, not location nor sign.

    Attributes:
        args: command line options including directory of inventory
        attribute:
            function thing -> to be added attribute
            as (key, value) tuple
        condition:
            function thing -> bool: only add attribute if
            condition(thing) is True
    """

    def add_if(thing):
        if condition(thing):
            key, value = attribute(thing)
            thing[key] = value

    transform_all(args, add_if)


def transform_all(args, transformation):
    """Do something with all things: transformation."""
    things = inventory_io.Inventory.from_json_files(directory=args.dataDirectory)
    for thing in things:
        transformation(thing)
    things.save()


def logging_config(args):
    """Set the basic logging config."""
    try:
        os.mkdir(args.output_dir)
    except FileExistsError:
        pass  # everything fine
    logging.basicConfig(
        filename=os.path.join(args.output_dir, args.logfile),
        level=logging.DEBUG,
        filemode="w",
    )
