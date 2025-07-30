"""Patching escpos library to cut between images without whitespace between

See comment at Job.print for more details.
"""

from dataclasses import dataclass
import logging
import time
from typing import Optional

import six  # type: ignore

from escpos.image import EscposImage  # type: ignore
from escpos.escpos import Escpos  # type: ignore
from escpos.constants import ESC, GS  # type: ignore
from escpos.exceptions import ImageWidthError  # type: ignore
from escpos.printer.usb import Usb as UsbPrinter  # type: ignore


@dataclass
class Cmd:
    index: int
    cmd: bytes


if 1:

    def _image(
        self,
        img_source,
        high_density_vertical: bool = True,
        high_density_horizontal: bool = True,
        impl: str = "bitImageRaster",
        fragment_height: int = 960,
        center: bool = False,
        cmd_index_offset: int = 0,
    ) -> Optional[int]:
        """Print an image.

        You can select whether the printer should print in high density or not. The default value is high density.
        When printing in low density, the image will be stretched.

        Esc/Pos supplies several commands for printing. This function supports three of them. Please try to vary the
        implementations if you have any problems. For example the printer `IT80-002` will have trouble aligning
        images that are not printed in Column-mode.

        The available printing implementations are:

            * `bitImageRaster`: prints with the `GS v 0`-command
            * `graphics`: prints with the `GS ( L`-command
            * `bitImageColumn`: prints with the `ESC *`-command

        When trying to center an image make sure you have initialized the printer with a valid profile, that
        contains a media width pixel field. Otherwise the centering will have no effect.

        :param img_source: PIL image or filename to load: `jpg`, `gif`, `png` or `bmp`
        :param high_density_vertical: print in high density in vertical direction *default:* True
        :param high_density_horizontal: print in high density in horizontal direction *default:* True
        :param impl: choose image printing mode between `bitImageRaster`, `graphics` or `bitImageColumn`
        :param fragment_height: Images larger than this will be split into multiple fragments *default:* 960
        :param center: Center image horizontally *default:* False

        """
        im = EscposImage(img_source)

        try:
            if self.profile.profile_data["media"]["width"]["pixels"] == "Unknown":
                logging.debug(
                    "The media.width.pixel field of the printer profile is not set. "
                    + "The center flag will have no effect."
                )

            max_width = int(self.profile.profile_data["media"]["width"]["pixels"])

            if im.width > max_width:
                raise ImageWidthError(f"{im.width} > {max_width}")

            if center:
                im.center(max_width)
        except KeyError:
            # If the printer's pixel width is not known, print anyways...
            pass
        except ValueError:
            # If the max_width cannot be converted to an int, print anyways...
            pass

        if im.height > fragment_height:
            fragments = im.split(fragment_height)
            cmd_index_offset = 0
            for fragment in fragments:
                cmd_index_offset = self.image(
                    fragment,
                    high_density_vertical=high_density_vertical,
                    high_density_horizontal=high_density_horizontal,
                    impl=impl,
                    fragment_height=fragment_height,
                    cmd_index_offset=cmd_index_offset,
                )
                # XXX dummy printer doesn't have '_sleep_in_fragment' method
                # self._sleep_in_fragment()
            return None

        if impl == "bitImageRaster":
            # GS v 0, raster format bit image
            density_byte = (0 if high_density_horizontal else 1) + (
                0 if high_density_vertical else 2
            )
            header = (
                GS
                + b"v0"
                + bytes((density_byte,))
                + self._int_low_high(im.width_bytes, 2)
                + self._int_low_high(im.height, 2)
            )
            self._raw(header + im.to_raster_format())

        if impl == "graphics":
            # GS ( L raster format graphics
            img_header = self._int_low_high(im.width, 2) + self._int_low_high(
                im.height, 2
            )
            tone = b"0"
            colors = b"1"
            ym = b"\x01" if high_density_vertical else b"\x02"
            xm = b"\x01" if high_density_horizontal else b"\x02"
            header = tone + xm + ym + colors + img_header
            raster_data = im.to_raster_format()
            self._image_send_graphics_data(b"0", b"p", header + raster_data)
            self._image_send_graphics_data(b"0", b"2", b"")

        if impl == "bitImageColumn":
            # ESC *, column format bit image
            density_byte = (1 if high_density_horizontal else 0) + (
                32 if high_density_vertical else 0
            )
            header = (
                ESC
                + b"*"
                + six.int2byte(density_byte)
                + self._int_low_high(im.width, 2)
            )
            self._raw(Cmd(cmd_index_offset, ESC + b"3" + six.int2byte(16)))
            for i, blob in enumerate(im.to_column_format(high_density_vertical)):
                cmd_index = i + 1 + cmd_index_offset
                self._raw(Cmd(cmd_index, header + blob + b"\n"))
            self._raw(ESC + b"2")
            return cmd_index_offset + i + 1

        return None

    Escpos.image = _image


if 1:

    # Usb printer: reduce likelihood for timeout gibberish

    _Usb_raw_original = UsbPrinter._raw

    def _Usb_raw(self, *args, **kwargs) -> None:
        _Usb_raw_original(self, *args, **kwargs)
        # NOTE Patch to reduce likelihood for timeout gibberish
        while self._read():
            time.sleep(0.01)

    UsbPrinter._raw = _Usb_raw
