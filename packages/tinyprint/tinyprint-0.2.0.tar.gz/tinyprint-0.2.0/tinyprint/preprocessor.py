from __future__ import annotations

import abc
from functools import cached_property
from tempfile import TemporaryDirectory
from typing import Callable, TypeAlias, Optional

from escpos.escpos import Escpos  # type: ignore
from escpos.constants import TXT_STYLE
import marko  # type: ignore
from PIL import Image  # type: ignore
from pdf2image import convert_from_path  # type: ignore

from tinyprint.jobconfig import Resource, Orientation
from tinyprint.job import Job

Page: TypeAlias = Callable[[Escpos], None]


class Preprocessor(abc.ABC):
    def __init__(self, job: Job):
        self.job = job

    @abc.abstractmethod
    def __call__(self, resource: Resource) -> tuple[Page, ...]: ...


class ImagePreprocessor(Preprocessor):
    def __call__(self, resource: Resource):
        return (get_image_printer(resource, self.job),)


def get_image_printer(resource, job):
    path, fragment_height = resource.path, resource.fragment_height
    profile = job.printer.profile

    # Immediately load & process image - in case image path is volatile
    # (as it's the case if PdfPreprocessor parses us an img path), we
    # don't loose the image. The downside of this is that we need to keep
    # the image in our RAM. But because we resize, and the resolution of
    # the ESC/POS printer is usually quite low, this is acceptable and
    # should only create problem in case of very large books.
    with Image.open(path) as im:
        if job.config.orientation != Orientation.HORIZONTAL:
            im = im.rotate(angle=-90, expand=True)
        max_width = profile.profile_data["media"]["width"]["pixels"]
        assert max_width != "Unknown", "max_width of printer unknown!"
        max_width = int(max_width * profile.img_scale_factor)
        width = im.width
        heigth = im.height
        factor = max_width / width
        final_im = im.resize(
            (
                int(width * factor * profile.img_x_scale_factor),
                int(heigth * factor * profile.img_y_scale_factor),
            )
        )

    color = ("black", "red")[resource.color]

    def _(printer):
        printer._raw(TXT_STYLE["color"][color])
        try:
            # Add extra space between to make spaces between cuts even
            # XXX Does number '10' need to change depending on printer?
            if job.config.cut:
                printer.line_spacing(10)
                printer.ln()
                printer.line_spacing()

            img_kwargs = dict(job.printer.profile.img_kwargs)
            if fragment_height:
                img_kwargs["fragment_height"] = fragment_height

            printer.image(
                final_im,
                **img_kwargs,
            )
        finally:
            final_im.close()

    return _


class PdfPreprocessor(ImagePreprocessor):
    def __call__(self, resource: Resource):
        pdf_path = resource.path
        with TemporaryDirectory() as tmp_path:
            image_list = convert_from_path(pdf_path, output_folder=tmp_path, dpi=600)
            if self.job.config.orientation == Orientation.HORIZONTAL:
                image_list = [im.rotate(angle=-90, expand=True) for im in image_list]
            page_list = []
            for i, img in enumerate(image_list):
                p = f"{tmp_path}/{i}.png"
                img.save(p)
                page_list.extend(super().__call__(Resource(p, 0)))
        return tuple(page_list)


class MarkdownPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown = marko.Markdown(renderer=_EscposRenderer)
        self.markdown._setup_extensions()

    def __call__(self, resource: Resource):
        with open(resource.path, "r") as f:
            md = f.read()

        def _(printer):
            self.markdown.renderer.set_printer(printer)
            self.markdown.renderer.set_job(self.job)
            self.markdown(md)

        return (_,)


class _EscposRenderer(marko.renderer.Renderer):
    # Ref: https://github.com/frostming/marko/blob/master/marko/html_renderer.py

    # TODO Add auto page breaks

    def render_raw_text(self, element) -> str:
        self._printer.text(element.children)
        # XXX: Temporarily disable auto-line break until it can be configured in UI
        # word_list = element.children.split(" ")
        # max_char_count = self.max_char_count
        # for word in word_list:
        #     char_count = len(word)
        #     # If word is too big for one line, just skip line breaking.
        #     if char_count > max_char_count:
        #         self._printer.text(word)
        #         self.line_position = self.line_position % max_char_count
        #         continue
        #     add_whitespace = self.line_position > 0
        #     new_pos = self.line_position + char_count + add_whitespace
        #     diff = new_pos - max_char_count
        #     if diff <= 0:
        #         if add_whitespace:
        #             self._printer.text(" ")
        #         self._printer.text(word)
        #         self.line_position = new_pos
        #     else:  # diff > 0
        #         space_count = max_char_count - self.line_position
        #         if space_count:
        #             self._printer.text(" " * space_count)
        #         self._printer.text(word)
        #         self.line_position = char_count
        return ""

    def render_emphasis(self, element) -> str:
        self._set(bold=True)
        self.render_children(element)
        self._set(bold=False)
        return ""

    def render_image(self, element) -> str:
        resource = Resource(path=element.dest)
        get_image_printer(resource, self._job)(self._printer)
        return ""

    def render_strong_emphasis(self, element) -> str:
        return self.render_emphasis(element)

    def render_blank_line(self, element=None):
        self.render_line_break(line_count=1)
        return ""

    def render_line_break(self, element=None, line_count: Optional[int] = None) -> str:
        soft = element.soft if element else True
        if line_count is None:
            if soft:
                line_count = 1
            else:
                line_count = 2
        self._printer.ln(line_count)
        self.line_position = 0
        return ""

    def render_paragraph(self, element) -> str:
        self.render_children(element)
        self.render_line_break()
        return ""

    def render_heading(self, element) -> str:
        self.max_char_count = self.printer_profile.big_char_count
        self._set(double_height=True, double_width=True)
        self.render_children(element)
        self._set(double_height=False, double_width=False, normal_textsize=True)
        self.render_line_break(line_count=3)
        self.max_char_count = self.printer_profile.default_char_count
        return ""

    def set_printer(self, printer):
        self._printer = printer

    def set_job(self, job):
        self._job = job

    def _set(self, *args, **kwargs):
        if self._printer:
            self._printer.set(*args, **kwargs)
        else:
            raise RuntimeError("printer not yet set")

    @property
    def line_position(self):
        try:
            return self._line_position
        except AttributeError:
            return 0

    @line_position.setter
    def line_position(self, line_position: int):
        self._line_position = line_position

    @cached_property
    def printer_profile(self):
        return self._job.printer.profile

    @property
    def max_char_count(self):
        try:
            return self._max_char_count
        except AttributeError:
            self.max_char_count = self.printer_profile.default_char_count
            return self.max_char_count

    @max_char_count.setter
    def max_char_count(self, max_char_count: int):
        self._max_char_count = max_char_count
