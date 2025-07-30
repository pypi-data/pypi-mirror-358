#!/usr/bin/env python3
"""Create a list of things to hang in the place with all the stuff (e.g. a bike shed)."""
import logging

import pypandoc

import argparse
import os.path
from typing import cast

try:
    import treelib
except ModuleNotFoundError:
    print(
        "module treelib not found. "
        "Install it system-wide or create a conda environment "
        "with the environment.yml named inventory."
    )
    import sys

    sys.exit(1)

from .box import BoxedThing
from .signprinter_latex import SignPrinterLaTeX
from . import inventory_io

HEADER_MARKDOWN_THING_LIST = [
    "---",
    "classoption:",
    "- twocolumn",
    "geometry:",
    "- margin=0.5cm",
    "- bottom=1.5cm",
    "---",
    "",
    "# Fahrradteile" "",
]


def add_arg_parsers(subparsers):
    """Make a command-line argument parser as a child of parent_parser.

    Supply information from command-line arguments.

    Args:
        subparsers: list of subparsers to add to. Type is private to argparse module.
    """
    parser = subparsers.add_parser(
        "label",
        description="""Create lists and signs for things in the inventory.

        The output directory is created. If the outputfiles are
        not directly in the output directory, the directories
        where the output files are supposed to land must exist.

        Output files overwrite existing files.
        """,
    )
    parser.add_argument(
        "-l",
        "--list",
        dest="list",
        action="store_true",
        help="Create pdf list. Uses LaTeX via pandoc, might take a bit longer.",
    )
    parser.add_argument(
        "--signs",
        action="store_true",
        help="Create pdf signs as pdf. Uses LaTeX, might take a bit longer.",
    )

    parser.set_defaults(func=generate_labels)

    parser_single_sign = subparsers.add_parser(
        "single_sign", description="Create a single sign as svg."
    )
    parser_single_sign.add_argument(
        "thing_id",
        help="Thing id of the thing the sign is for. "
        "This is the directory name of the thing.",
    )
    parser_single_sign.set_defaults(func=generate_single_sign_svg)


def get_markdown_list(things):
    """Get markdown representation of thing list."""
    # each item can appear several times since alternative names
    # might not be unique: things can be similar.
    # so for every thing we need a list of lines
    lines = {}

    def add_line(name: str, new_line: str):
        if name in lines:
            lines[name].append(new_line)
        else:
            lines[name] = [new_line]

    for thing in things:
        if thing.get("category", False):
            continue
        add_line(thing.best("name", backup="?"), thing.markdown_representation())
        for alt_name, line in thing.alt_names_markdown().items():
            add_line(alt_name, line)
    markdown = "\n".join(
        HEADER_MARKDOWN_THING_LIST
        + [
            line
            for name in sorted(list(lines.keys()), key=str.lower)
            for line in lines[name]
        ]
    )
    return markdown


def get_tree(things: inventory_io.Inventory) -> str:
    """Create a simple tree structure visualizing the things."""
    tree = treelib.Tree()
    nodes = []
    tree.create_node("Fahrrad", "fahrrad-0")
    for thing in things:
        name = str(thing.best("name", backup="?"))
        parents = cast(tuple, thing.get("part_of", ["fahrrad"]))
        for instance_nr, parent in enumerate(parents):
            node_id = f"{things.get_id(thing)}-{instance_nr}"
            # doesn't work well with categories that appear several times, whatever:
            parent = parent + "-0"
            nodes.append((name, node_id, parent))
    delayed_nodes = []
    inserted_node = True  # save if in previous run,
    # some node got removed from the list of all nodes
    while inserted_node:
        logging.debug("Start insertion walkthrough")
        inserted_node = False
        for node in nodes:
            try:
                tree.create_node(node[0], node[1], node[2])
            except treelib.exceptions.NodeIDAbsentError:
                delayed_nodes.append(node)
            except treelib.exceptions.DuplicatedNodeIdError as e:
                logging.error(f"{node[1]} twice: {e}")
                inserted_node = True
            else:
                inserted_node = True
        nodes = delayed_nodes
        delayed_nodes = []
    if len(nodes) > 0:
        logging.error("Remaining nodes:" + ", ".join((str(node) for node in nodes)))
    return tree.show(stdout=False)


def create_listpdf(markdown: str, pdffile):
    """Create a pdf file that can be printed that lists all things.

    Args:
        markdown: path to markdown file that is converted
        pdffile: path to created pdf file
    """
    markdown = markdown.replace("\u2640", "(weiblich)").replace("\u2642", "männlich")
    pypandoc.convert_text(
        markdown,
        format="md",
        to="pdf",
        outputfile=pdffile,
        extra_args=[
            "-V",
            "geometry:top=1cm,bottom=1cm,left=1cm,right=1.5cm",
            "-V",
            "classoption=twocolumn",
        ],
    )


def generate_labels(options: argparse.Namespace):
    """Create lists and signs based on command-line options.

    Args:
        options: command line options given
    """
    os.makedirs(options.output_dir, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(options.output_dir, options.logfile),
        level=logging.DEBUG,
        filemode="w",
    )
    logging.info("Create thing list")
    all_things: list[BoxedThing] = inventory_io.Inventory.from_json_files(
        options.dataDirectory
    )
    with open(
        os.path.join(options.output_dir, options.output_tree),
        mode="w",
        encoding="UTF-8",
    ) as treefile:
        logging.info("Start creating tree view.")
        treefile.write(get_tree(all_things))
    logging.info("Start creating markdownlist.")
    markdown = get_markdown_list(all_things)
    try:
        with open(
            list_md_file_name := os.path.join(
                options.output_dir, options.output_mdlist
            ),
            mode="w",
            encoding="UTF-8",
        ) as mdfile:
            mdfile.write(markdown)
    except IOError as io_error:
        logging.error(f"IOError {io_error} occured during writing list Markdown file.")
        if options.list:
            logging.info("Create no list pdf since the markdown file does not exist..")
    else:
        if options.list:
            create_listpdf(
                markdown,
                os.path.join(options.output_dir, options.output_pdflist),
            )
    logging.info("Start creating sign LaTeX.")
    sign_printer_latex = SignPrinterLaTeX(options)
    if options.signs:
        sign_printer_latex.create_signs_pdf(all_things)
    else:
        sign_printer_latex.save_signs_latex(all_things)


def generate_single_sign_svg(options: argparse.Namespace):
    """Generate sign for a single thing, given by options.thing_id.

    Args:
        options: command line options given
    """
    logging.basicConfig(
        filename=os.path.join(options.output_dir, options.logfile),
        level=logging.DEBUG,
        filemode="w",
    )
    logging.info("Create thing sign")
    all_things = inventory_io.Inventory.from_json_files(options.dataDirectory)
    logging.info("Start creating sign svg.")
    try:
        thing = all_things.get_by_id(options.thing_id)
    except KeyError as id_not_found:
        print("key error:")
        print(id_not_found)
        possible_things = list(all_things.get_by_best("name", options.thing_id))
        if len(possible_things) == 1:
            thing = possible_things[0]
        else:
            error_message = (
                f"No thing with the id {options.thing_id} and 0 or >1 thing "
                f"with this name. Do not do anything."
            )
            logging.error(error_message)
            print(error_message)
            return
    sign_printer_latex = SignPrinterLaTeX(options)
    svg_path = sign_printer_latex.create_sign_svg(thing)
    if svg_path:
        print(
            f"sign svg created for {thing.best('name', backup="?")} "
            f"({options.thing_id}): find it at {svg_path}"
        )
    else:
        print(
            f"Error at creating sign for {thing.best('name', backup="?")} "
            f"({options.thing_id})."
        )
