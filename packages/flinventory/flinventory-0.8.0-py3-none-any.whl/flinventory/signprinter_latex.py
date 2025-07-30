#!/usr/bin/env python3
"""Create a latex document with signs (For printing and glueing to boxes).

Todo:
    rename font size to text scale. Because it is used to scale instead of setting
    a font size. So the 'normal' is not 12 (pt) but 1.
"""
import argparse
import importlib.resources
import os.path
import logging
import subprocess
from typing import Union, Iterable, Optional, cast

from .box import BoxedThing
from .sign import Sign
from . import constant
from . import thingtemplate_latex

TEMPLATE_PACKAGE = thingtemplate_latex
TEMPLATE_PRE = "signlist-header.tex"
# importlib.resources.read_text("flinventory", "signlist-header.tex"))
TEMPLATE_POST = "signlist-footer.tex"
TEMPLATE_SIGN = "sign.tex"
DUMMY_IMAGE = "dummyImage.jpg"
AUX_DIR = "latexAux"
LATEXMK_OPTIONS = [
    "latexmk",
    f"-aux-directory={AUX_DIR}",
    "-pdf",
    "-interaction=nonstopmode",
    "-f",
]
# only the tex file needs to be added to the list

UNIT = "cm"  # todo: replace by length_unit in options, includes scaling the constants
# estimated by one example word
# at standard fontsize german
STANDARD_LETTER_LENGTH = 0.2  # in cm at font size 12pt
STANDARD_LETTER_HEIGHT = (12 + 1) * 0.03515  # in cm at font size 12 + linesep
# weird number is size of pt in LaTeX in cm
STANDARD_FONT_SIZE_GERMAN = 1
STANDARD_FONTSIZE_ENGLISH = 0.8
# amount of space the location string is shifted down
# (usually negative amount to shift up)
STANDARD_LOCATION_SHIFT_DOWN = r"-.8\baselineskip"
# in symbols:
STANDARD_LINE_LENGTH = 15
# how much bigger german should roughly be than english
GERMAN_TO_ENGLISH_SHARE = 1.25
# how big the image should be in parts of entire sign (in portrait mode)
IMAGE_SHARE = 0.5
# how much of the sign height can actually be used for text (due to margins)
# (in landscape mode)
TEXT_SHARE = 0.7
# minimum ration width/height for using landscape mode
LANDSCAPE_MIN_RATIO = 2
# paper text width (a4 = 21 cm wide) in cm
PAPER_TEXT_WIDTH = 20
# minimal height of sign for including an image (in cm)
MINIMAL_HEIGHT_FOR_IMAGE = 3
STANDARD_WIDTH = 8
# width of signs without given width [cm]
STANDARD_HEIGHT = 8
# height of signs without given height [cm]
MAX_WIDTH = 18  # otherwise too wide for A4 page
# maximum width of a sign [cm]
MAX_HEIGHT = 28  # otherwise too long for A4 page
# maximum height for a sign [cm]


def sanitize_latex_code(latex: Union[str, int, float]):
    """Make a string insertable into LaTeX code.

    Replace &, \\, ....
    """
    try:
        for orig, new in [
            ("\\", "\\textbackslash{}"),
            ("{", "\\{"),
            ("}", "\\}"),
            ("$", "\\$"),
            ("&", "\\&"),
            ("#", "\\#"),
            ("^", ""),  # better: → \textasciicircum{} (requires the textcomp package)
            ("_", "\\_"),
            ("~", "\\textasciitilde{}"),
            ("%", "\\%"),
            ("<", "\\textless{}"),
            (">", "\\textgreater{}"),
            ("|", "\\textbar{}"),
        ]:
            latex = cast(str, latex).replace(orig, new)
    except AttributeError:
        pass
    return latex


class LaTeXError(Exception):
    """Exception saying that LaTeX exited non-gracefully."""

    def __init__(
        self, message: str, call: list[str], input_file: str, return_code: int
    ):
        """Create LaTeXError.

        Args:
            message: general message as for every exception
            call: LaTeX call sent to the console
            input_file: tex file processed (probably included in call)
            return_code: Return call of the LaTeX command, non-zero
        """
        super().__init__(message)
        self.call = call
        self.input_file = input_file
        self.return_code = return_code


class SignPrinterLaTeX:
    # pylint: disable=too-many-instance-attributes
    """Class encapsulating algorithm for creating printable signs from thing list.

    Bad design choice: you have to create an object but actually this object is never used,
    could all just be module or class functions.
    """

    def __init__(self, paths):
        """Create SignPrinter by reading in template files."""
        # pylint: disable-next=unbalanced-tuple-unpacking
        self.pre, self.sign, self.post = self._read_templates()
        self.output_dir = paths.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.signs_file = paths.output_signs_latex
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _read_templates() -> list[str]:
        """Read the templates from the files.

        Returns:
            (iterable) main template, css header,
            single size sign html file, double size sign html file
        """
        # todo remove function by using importlib, which gives directly the text
        file_contents = []
        for filename in [TEMPLATE_PRE, TEMPLATE_SIGN, TEMPLATE_POST]:
            file_contents.append(
                importlib.resources.read_text(TEMPLATE_PACKAGE, filename)
            )
        return file_contents

    def controlled_length(
        self,
        sign: Sign,
        key: str,
        backup: Union[int, float],
        maximum: Union[int, float],
    ):
        """Get the value for the key if it exists and is a number and < max, otherwise backup."""
        value = sign.get(key, backup)
        try:
            value = float(value)
        except ValueError:
            self.logger.error(
                f"{key} {value} is not a number. Use {backup} {UNIT} instead."
            )
            return backup
        if value <= 0:
            self.logger.error(
                f"{key} {value} is non-positive and therefore not a valid sign {key}. "
                f"Use {backup} {UNIT} instead."
            )
            return backup
        if value == int(value):
            return min(int(value), maximum)
        return min(value, maximum)

    def width(self, thing: BoxedThing) -> Union[int, float]:
        """Get the width of a sign, using backup and max size.

        In UNIT.
        """
        return self.controlled_length(
            thing.sign, key="width", backup=STANDARD_WIDTH, maximum=MAX_WIDTH
        )

    def height(self, thing: BoxedThing) -> Union[int, float]:
        """Get the height of the sign of a boxed thing, using backup and max size."""
        return self.controlled_length(
            thing.sign, key="height", backup=STANDARD_HEIGHT, maximum=MAX_HEIGHT
        )

    def image_height_vspace(
        self, thing: BoxedThing, sign_height: Union[int, float]
    ) -> tuple[Union[int, float], Union[int, float]]:
        """Get the height of the image in the portrait sign.

        In UNIT.
        Args:
            thing: the thing for which the sign is
            sign_height: height of the sign. Needed for backup height.
        """
        if sign_height < MINIMAL_HEIGHT_FOR_IMAGE:
            return (
                self.controlled_length(
                    thing.sign, key="imageheight", backup=0, maximum=sign_height
                ),
                r"-1.5\baselineskip",
            )
        return (
            self.controlled_length(
                thing.sign,
                key="imageheight",
                backup=sign_height * IMAGE_SHARE,
                maximum=sign_height,
            ),
            "1pt",
        )

    def if_use_landscape_template(self, thing: BoxedThing):
        """Return if we want to use the landscape template for this thing.

        The landscape template has the image to the right of the text
        instead of below it. So a portrait sign is usually still wider
        than high.
        """
        try:
            return thing.sign.get("landscape")
        except KeyError:
            try:
                return self.width(thing) >= self.width(thing) * LANDSCAPE_MIN_RATIO
            except KeyError:
                return True

    def guess_font_size(self, thing):
        """Guess good font size.

        Based on the length of the name and the size of the sign.

        Returns:
            guessed font size primary language, guessed font size secondary language in UNIT
        """
        # at first we do not support landscape signs
        # if self.if_use_landscape_template(thing):
        #    return self.guess_font_size_landscape(thing)
        return self.guess_font_size_portrait(thing)

    def guess_font_size_landscape(thing):
        """Guess good font sizes for the landscape template."""
        assert False, "landscape latex signs are not supperted"
        # for simplicity assume only one line
        width = self.width(thing)
        height = self.height(thing)
        used_width = width - height  # that is approximately the part the image uses
        german = thing.sign.get(("name", 0), "")
        english = thing.sign.get(("name", 1), "")
        german_expected_width_at_standard = len(german) * STANDARD_LETTER_LENGTH
        german_max_by_width = (
            STANDARD_FONT_SIZE_GERMAN * used_width / german_expected_width_at_standard
        )
        german_max_by_height = (
            height
            * TEXT_SHARE
            / (GERMAN_TO_ENGLISH_SHARE + 1)
            * GERMAN_TO_ENGLISH_SHARE
        )
        english_expected_width_at_standard = (
            len(english)
            * STANDARD_LETTER_LENGTH
            * STANDARD_FONTSIZE_ENGLISH
            / STANDARD_FONT_SIZE_GERMAN
        )
        english_max_by_width = (
            STANDARD_FONTSIZE_ENGLISH * used_width / english_expected_width_at_standard
        )
        english_max_by_height = height * TEXT_SHARE / (GERMAN_TO_ENGLISH_SHARE + 1)
        return (
            min(german_max_by_width, german_max_by_height),
            min(english_max_by_width, english_max_by_height),
        )

    def guess_font_size_portrait(self, thing: BoxedThing):
        # pylint: disable=too-many-locals
        """Guess what a good font size is for this sign.

        Based on the length of the name and the size of the sign.

        Returns:
            guessed font size primary, guessed font size secondary in UNIT
        """
        # use german and english as aliases for primary and secondary language
        # because it's easier to read
        german = thing.get(("name", 0), "")
        english = thing.get(("name", 1), "")
        german_words = german.replace("-", "- ").split() or [" "]
        english_words = english.replace("-", " ").split() or [" "]
        # ignore cases with more than 2 lines, should be considered by hand
        max_font_sizes: list[list[int | float]] = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        # there are 4 line number cases, see below in for loop
        GERMAN_INDEX = 0  # pylint: disable=invalid-name
        ENGLISH_INDEX = 1  # pylint: disable=invalid-name
        SUM_INDEX = 2  # pylint: disable=invalid-name
        # self.logger.debug("g: {}; e: {}, width: {}, heigth: {}".format(
        #     german, english, *thing.sign.size  # unpacking pair
        # ))
        width = self.width(thing)
        height = self.width(thing)
        for german_number_lines, english_number_lines, case in [
            (1, 1, 0),
            (1, 2, 1),
            (2, 1, 2),
            (2, 2, 3),
        ]:
            german_length = max(
                (
                    max(len(word) for word in german_words)
                    if german_number_lines == 2
                    else len(german)
                ),
                1,
            )
            english_length = max(
                (
                    max(len(word) for word in english_words)
                    if english_number_lines == 2
                    else len(english)
                ),
                1,
            )
            german_expected_width_at_standard = german_length * STANDARD_LETTER_LENGTH
            german_max_by_width = (
                STANDARD_FONT_SIZE_GERMAN * width / german_expected_width_at_standard
            )
            text_height = height * (
                1 if height < MINIMAL_HEIGHT_FOR_IMAGE else IMAGE_SHARE
            )
            german_max_by_height = (
                STANDARD_FONT_SIZE_GERMAN
                * text_height
                / STANDARD_LETTER_HEIGHT
                / (german_number_lines * GERMAN_TO_ENGLISH_SHARE + english_number_lines)
                * GERMAN_TO_ENGLISH_SHARE
            )
            english_expected_width_at_standard = (
                english_length
                * STANDARD_LETTER_LENGTH
                * STANDARD_FONTSIZE_ENGLISH
                / STANDARD_FONT_SIZE_GERMAN
            )
            # in factor size compared to normal size
            english_max_by_width = (
                STANDARD_FONTSIZE_ENGLISH * width / english_expected_width_at_standard
            )
            # in cm:
            english_max_by_height = (
                STANDARD_FONTSIZE_ENGLISH
                * text_height
                / STANDARD_LETTER_HEIGHT
                / (german_number_lines * GERMAN_TO_ENGLISH_SHARE + english_number_lines)
            )
            logging.info(
                f"german: {german}, english: {english}, case: {case} "
                f"lines: ({german_number_lines}, {english_number_lines}, {case},"
                f"german_max_by_height: {german_max_by_height}, "
                f"german_max_by_width: {german_max_by_width}, "
                f"english_max_by_height: {english_max_by_height}, "
                f"english_max_by_width: {english_max_by_width}"
            )
            max_font_sizes[case][GERMAN_INDEX] = min(
                [german_max_by_height, german_max_by_width]
            )
            max_font_sizes[case][ENGLISH_INDEX] = min(
                [english_max_by_height, english_max_by_width]
            )
            max_font_sizes[case][SUM_INDEX] = (
                max_font_sizes[case][GERMAN_INDEX] + max_font_sizes[case][ENGLISH_INDEX]
            )
            # self.logger.debug(
            #     "case: {}; gmaxH: {:.3f}; gmaxW: {:.3f}; emaxH: {:.3f}; emaxW: {:.3f}".format(
            #         case, german_max_by_height, german_max_by_width,
            #         english_max_by_height, english_max_by_width
            #     )
            # )
        german_max, english_max, _ = max(
            max_font_sizes, key=lambda case: case[SUM_INDEX]
        )
        # self.logger.debug("used fs: g: {:.3f}, e: {:.3f}".format(german_max, english_max))
        return german_max, english_max

    def get_font_size(self, thing: BoxedThing):
        """Determine font size of sign for thing.

        Take font size in the thing.
        Guess font size if not specified.

        Returns:
            (german font size, english font size)
        """
        default_german_font_size, default_english_font_size = self.guess_font_size(
            thing
        )
        german_font_size = thing.sign.get(("fontsize", 0), default_german_font_size)
        english_font_size = thing.sign.get(("fontsize", 1), default_english_font_size)
        logging.info(
            f"{thing.best('name')} font factor: (de) {german_font_size} (en) {english_font_size}"
        )
        return german_font_size, english_font_size

    def create_latex_single_sign(self, thing: BoxedThing) -> str:
        """Create latex code (as str) that shows one sign in a minimal document."""
        return "\n".join(
            (
                r"\documentclass[12pt]{standalone}",
                *(self.pre.splitlines()[2:]),
                self.create_sign(thing),
                self.post,
            )
        )

    def create_latex(self, things: Iterable[BoxedThing]) -> str:
        """Create latex code (as str) that shows all signs.

        Arguments:
            things: list of things to be described
        Return:
            latex code with document with all signs that should be printed
        """
        content_latex = [self.pre]
        current_line_filled_width = 0
        for thing in [
            tmp_thing for tmp_thing in things if tmp_thing.sign.should_be_printed()
        ]:
            if current_line_filled_width + self.width(thing) > PAPER_TEXT_WIDTH:
                content_latex.append(
                    ""
                )  # empty line in code makes new line (= row) in pdf
                current_line_filled_width = 0.0
            content_latex.append(self.create_sign(thing))
            current_line_filled_width += self.width(thing)
        content_latex.append(self.post)
        return "\n".join(content_latex)

    def get_values_for_template(self, thing: BoxedThing):
        """Get values for the insertion into the templates.

        Only the values that are common for portrait
        and landscape template:
            widthAdjusted (width - 0.14cm)
            textscaleGerman
            GermanName
            textscaleEnglish
            EnglishName
            imagepath
            imageheight
            location
        """
        german = thing.sign.get(("name", 0), "")
        english = thing.sign.get(("name", 1), "")

        width = self.width(thing)
        height = self.height(thing)
        width = width - 0.14  # todo: fix latex template or create constant
        insertions = {
            "PrimaryName": sanitize_latex_code(german),
            "SecondaryName": sanitize_latex_code(english),
            "location": sanitize_latex_code(
                str(thing.location.long_name)
                if thing.sign.get("location_long", True)
                else str(thing.where)
            ),
            "height": height,
            "widthAdjusted": width,
        }

        if not insertions["location"]:  # empty string
            logging.warning(f"Print sign for {german} ({english}) without location.")

        insertions["imageheight"], insertions["vspace"] = self.image_height_vspace(
            thing, height
        )

        # at first only portrait sign, landscape sign can be implemented later
        # if self.if_use_landscape_template(thing):  # would need different condition
        if image_path := thing.thing.image_path():  # not None or ""
            rel_path_to_image = os.path.relpath(image_path, self.output_dir)
            insertions["imagepath"] = rel_path_to_image
        else:
            if insertions["imageheight"] > 0:
                # otherwise no image is printed and we do not need an unneccessary warning
                logging.getLogger(__name__).warning(
                    f"Missing image for {thing.best('name')}."
                )
            insertions["imagepath"] = DUMMY_IMAGE
            try:
                image_file = open(os.path.join(self.output_dir, DUMMY_IMAGE), mode="bw")
            except FileExistsError:
                pass
            else:
                dummy_image = importlib.resources.read_binary(
                    TEMPLATE_PACKAGE, DUMMY_IMAGE
                )
                with image_file:
                    image_file.write(dummy_image)
        font_sizes = self.get_font_size(thing)
        insertions["textscalePrimary"] = font_sizes[0]  # /12
        insertions["textscaleSecondary"] = font_sizes[1]  # /12

        insertions["locationShiftDown"] = thing.sign.get(
            "location_shift_down", STANDARD_LOCATION_SHIFT_DOWN
        )
        return insertions

    def create_sign(self, thing):
        """Create a sign based on the template sign.tex."""
        # text that is to be inserted into the template
        insertions = self.get_values_for_template(thing)
        # no landscape yet
        # if self.if_use_landscape_template(thing):
        #    return self.signhtml_landscape.format(
        #        **insertions # unpacking dictionary
        #        )
        return self.sign.format(**insertions)

    def save_signs_latex(self, things: list[BoxedThing]) -> str:
        """Save signs as tex-file to file path.

        Ignore things that should not be printed as saved in things.sign['printed'].

        Arguments:
            things: list of things to visualize
        Returns:
            path to created file.
        """
        things.sort(key=self.height)
        file_signs = os.path.join(self.output_dir, self.signs_file)
        print(f"Print LaTeX file to {file_signs}.")
        with open(file_signs, mode="w", encoding="UTF-8") as latex_file:
            latex_file.write(self.create_latex(things))
        return file_signs

    def create_signs_pdf(self, things: list[BoxedThing]):
        """Create a pdf and latex files with signs.

        Raises:
            ProgramMissingError: if no latexmk is available
            LaTeXError: if LaTeX exited with non-zero return code
        Returns:
            path to created pdf file
        """
        self.save_signs_latex(things)
        latex: (
            subprocess.CalledProcessError
            | subprocess.CompletedProcess
            | argparse.Namespace
        )
        try:
            latex = subprocess.run(
                LATEXMK_OPTIONS + [self.signs_file],
                cwd=self.output_dir,
                capture_output=True,
                text=True,
                check=True,
            )  # text=True makes output a str instead of bytes
        except FileNotFoundError as program_missing:
            latex = argparse.Namespace(
                stdout="No LaTeX output.", stderr="LaTeX not found."
            )
            if program_missing.filename == LATEXMK_OPTIONS[0]:
                raise constant.MissingProgramError(
                    LATEXMK_OPTIONS[0],
                    program_missing.errno,
                    f"Program {LATEXMK_OPTIONS[0]} missing.",
                    program_missing.filename,
                ) from program_missing
            raise program_missing
        except subprocess.CalledProcessError as latex_error:
            latex = latex_error  # includes output, stderr
            message = (
                f"Latex finished with returncode {latex.returncode}."
                f"Check in {os.path.join(self.output_dir, AUX_DIR)} for details."
            )
            print(message)
            raise LaTeXError(
                message,
                call=latex_error.cmd,
                input_file=self.signs_file,
                return_code=latex_error.returncode,
            ) from latex_error
        finally:
            with open(
                os.path.join(self.output_dir, AUX_DIR, "latex_output.txt"),
                mode="w",
                encoding="utf-8",
            ) as stdout_file:
                stdout_file.write(latex.stdout)
            with open(
                os.path.join(self.output_dir, AUX_DIR, "latex_error.txt"),
                mode="w",
                encoding="utf-8",
            ) as stderr_file:
                stderr_file.write(latex.stderr)
        pdf_file = os.path.join(
            self.output_dir, os.path.splitext(self.signs_file)[0] + ".pdf"
        )
        assert os.path.isfile(pdf_file), f"{pdf_file} was not created (yet)"
        return pdf_file

    def create_sign_svg(self, thing: BoxedThing) -> Optional[str]:
        """Create a svg from a pdf with a sign for this thing.

        Args:
            thing: the thing which sign should be created
        Returns:
            path of the created svg file. None if error
        Raises:
            ProgramMissingError: if latexmk or pdf2svg is not available
        """
        tex = self.create_latex_single_sign(thing)
        tex_hash = str(abs(hash(tex)))
        file_tex = tex_hash + ".tex"
        path_tex = os.path.join(self.output_dir, tex_hash + ".tex")
        file_pdf = tex_hash + ".pdf"
        path_pdf = os.path.join(self.output_dir, file_pdf)
        file_svg = tex_hash + ".svg"
        path_svg = os.path.join(self.output_dir, file_svg)
        if os.path.isfile(path_tex) and os.path.isfile(path_svg):
            self.logger.info(f"Do not regenerate {tex_hash}.")
            return path_svg
        with open(path_tex, mode="w") as file_tex_f:
            file_tex_f.write(tex)
        try:
            latex = subprocess.run(
                LATEXMK_OPTIONS + [file_tex],
                cwd=self.output_dir,
                capture_output=True,
                text=True,
            )  # text=True makes output a str instead of bytes
        except FileNotFoundError as program_missing:
            if program_missing.filename == LATEXMK_OPTIONS[0]:
                raise constant.MissingProgramError(
                    LATEXMK_OPTIONS[0],
                    program_missing.errno,
                    f"Program {LATEXMK_OPTIONS[0]} missing.",
                    program_missing.filename,
                ) from program_missing
            else:
                raise program_missing
        with open(
            os.path.join(self.output_dir, AUX_DIR, f"latex_output_{tex_hash}.txt"),
            mode="w",
        ) as stdout_file:
            stdout_file.write(latex.stdout)
        with open(
            os.path.join(self.output_dir, AUX_DIR, f"latex_error.{tex_hash}.txt"),
            mode="w",
        ) as stderr_file:
            stderr_file.write(latex.stderr)
        if latex.returncode != 0:
            error_message = (
                f"Latex for {thing.best('name', backup=tex_hash)} "
                f"finished with returncode {latex.returncode}."
                f"Check in {os.path.join(self.output_dir, AUX_DIR)} ({tex_hash}) for details."
            )
            self.logger.error(error_message)
            print(error_message)
            return None
        try:
            svg = subprocess.run(
                ["pdf2svg", path_pdf, path_svg],
                capture_output=True,
                text=True,
            )  # text=True makes output a str instead of bytes
        except FileNotFoundError as program_missing:
            if program_missing.filename == "pdf2svg":
                raise constant.MissingProgramError(
                    "pdf2svg",
                    program_missing.errno,
                    "Program pdf2svg missing.",
                    program_missing.filename,
                ) from program_missing
            else:
                raise program_missing
        with open(
            os.path.join(self.output_dir, AUX_DIR, f"svg_output_{tex_hash}.txt"),
            mode="w",
        ) as stdout_file:
            stdout_file.write(svg.stdout)
        with open(
            os.path.join(self.output_dir, AUX_DIR, f"svg_error.{tex_hash}.txt"),
            mode="w",
        ) as stderr_file:
            stderr_file.write(svg.stderr)
        if svg.returncode != 0:
            error_message = (
                f"svg for {thing.best('name', backup=tex_hash)} "
                f"finished with returncode {svg.returncode}."
                f"Check in {os.path.join(self.output_dir, tex_hash)}* for details."
            )
            self.logger.error(error_message)
            print(error_message)
            return None
        if os.path.isfile(path_svg):
            return path_svg
        error_message = (
            f"svg for {thing.best('name', backup=tex_hash)} "
            f"finished with returncode 0 but the svg was not created. "
            f"Check in {os.path.join(self.output_dir, tex_hash)}* for details."
        )
        self.logger.error(error_message)
        print(error_message)
        return None
