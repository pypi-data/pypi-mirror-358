from dataclasses import dataclass
import functools
import logging
import mimetypes
import threading
import traceback
import time
from typing import Optional

from escpos.config import Config as escpos_Config  # type: ignore
from escpos.constants import ESC, PAPER_PART_CUT, GS  # type: ignore
from escpos.printer import Dummy  # type: ignore
from escpos.printer.usb import Usb as UsbPrinter  # type: ignore
import six

import usb  # type: ignore

import tinyprint
from tinyprint.jobconfig import JobConfig, Resource
from tinyprint import xescpos


@dataclass
class Job:
    """Pre-process input files & prints them with ESC/POS printer."""

    config: JobConfig
    is_printing: bool = False
    _print_job: Optional[threading.Thread] = None

    def print(self):
        self.is_printing = True
        self._print_job = threading.Thread(target=self._print)
        self._print_job.start()

    def wait(self, timeout: Optional[float] = None):
        """Wait/block until print job is finished"""
        if self._print_job:
            self._print_job.join(timeout)
            self._print_job = None
            self.is_printing = False

    def stop(self):
        """Stop currently running print job"""
        if self._print_job and self._print_job.is_alive():
            self._logger.info("  stop print! >")
            self.is_printing = False
            self.wait()

    def _print(self):
        self._logger.info("< preprocess input ...")
        page_tuple = self._generate_page_tuple()
        self._logger.info("  finished preprocessing >")
        self._logger.info("< create ESC/POS codes ...")
        cmd_list = self._generate_cmd_list(page_tuple)
        self._logger.info("  finished creating ESC/POS codes >")
        self._logger.info("< start printing")
        self._send_to_printer(cmd_list)
        self._logger.info("  finished printing >")
        self.is_printing = False

    def close(self):
        self._logger.info("close printer")
        self.stop()
        self.printer.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.wait()
        self.close()

    def __del__(self):
        self.close()

    def _generate_cmd_list(self, page_tuple):
        dummy = Dummy()
        for copy_index in range(self.config.copy_count):
            for i, page in enumerate(page_tuple):
                try:
                    page(dummy)
                except Exception:
                    tb = traceback.format_exc()
                    self._logger.warn(f"error when printing page {i+1}: {tb}")
        output_list = dummy._output_list
        if self.config.cut:
            return self._add_auto_cut(output_list)
        else:
            return [getattr(cmd, "cmd", cmd) for cmd in output_list]

    def _add_auto_cut(self, output_list: list[bytes | xescpos.Cmd]) -> list[bytes]:
        # NOTE In case we want to cut the paper after each image,
        # we need to take special care to avoid whitespace between
        # each image. This whitespace happens if we just use the
        # default 'cut' method, because then the printer needs to
        # feed the paper until it reaches the cutting point (when
        # finished printing an image, some parts of the paper are
        # still inside the printer). So what we need to do is:
        #
        #   - print image 1
        #   - print image 2 partially
        #   - cut paper
        #   - print image 2 partially
        #   - print image 3 partially
        #   - cut paper
        #   - ...
        #
        # XXX This cutting currently only works for 'bitImageColumn' images
        # XXX This cutting currently only works for RessourceType PDF/ImageList
        processed_list = []
        img_cut_index = self.printer.profile.img_cut_index
        for cmd in output_list:
            match cmd:
                case xescpos.Cmd():
                    processed_list.append(cmd.cmd)
                    if cmd.index == img_cut_index:
                        processed_list.extend(
                            [
                                ESC + b"2",
                                PAPER_PART_CUT,
                                ESC + b"3" + six.int2byte(16),
                            ]
                        )
                case _:
                    processed_list.append(cmd)
        return processed_list

    def _generate_page_tuple(self):
        page_list = []
        for resource in self.config.resource_list:
            preprocessor = self.resource_to_preprocessor(resource)
            page_list.extend(preprocessor(resource))
        return tuple(page_list)

    def _send_to_printer(self, cmd_list: list[bytes]):
        printer = self.printer
        sleep_time = self.config.sleep_time or printer.profile.sleep_time
        try:
            for cmd in cmd_list:
                if not self.is_printing:
                    break
                try:
                    printer._raw(cmd)
                    # NOTE ( USB device printer fix )
                    #
                    # Do not lose any command:
                    # Python sends faster commands than the matrix
                    # printer can print. And the USB device doesn't
                    # block until one print command is finished, but
                    # returns immediately. If we run into a USBTimeout,
                    # this becomes a serious problem, because then
                    # we restart the printer & only resend the last command.
                    # In case the previous command wasn't processed yet,
                    # we'd lose this command (usually the paper cut).
                    # To avoid this, we wait for a little time, to better
                    # synchronize Python and the Matrix printer.
                    if sleep_time and len(cmd) > 5:
                        time.sleep(sleep_time)
                # NOTE ( USB device printer fix )
                # Don't give up when a time out happens - it seems USB
                # connection is sometimes unstable & breaks.
                except usb.core.USBTimeoutError:
                    logging.warn("timed out ... reset printer")
                    # We first read all data from printer to reduce the
                    # likelihood that the printer outputs glitchy gibberish
                    # to the print.
                    while printer._read():
                        time.sleep(0.01)
                    # Then reset printer to make it workable again
                    time.sleep(10)
                    printer.close()
                    time.sleep(10)
                    printer.open()
                    time.sleep(10)
                    # Finally try send command again
                    printer._raw(cmd)
        finally:
            # No matter what happens - make final cut.
            # Final cut
            #   66 => move to cut position
            #   00 => then make full cut
            printer._raw(GS + b"V" + six.int2byte(66) + b"\x00")

    @functools.cached_property
    def printer(self):
        if not self.config.printer_config:
            self._logger.warn("no printer config: use dummy printer")
            return Dummy()
        c = escpos_Config()
        c.load(self.config.printer_config)
        p = c.printer()
        patch_printer_profile(p)
        return p

    @functools.cached_property
    def _logger(self):
        """The class based logger."""
        cls = type(self)
        logger = logging.getLogger(f"{cls.__module__}.{cls.__name__}")
        logger.setLevel(tinyprint.config.LOGGING_LEVEL)
        return logger

    def resource_to_preprocessor(self, resource: Resource):
        path = resource.path
        p = None
        if _is_binary_file(path):
            m = mimetypes.guess_type(path)
            if m[0]:
                if m[0].startswith("image"):
                    p = _ImagePreprocessor()
                elif m[0] == "application/pdf":
                    p = _PdfPreprocessor()
        else:
            p = _MarkdownPreprocessor()
        if not p:
            raise NotImplementedError(f"can't guess type of {path}")
        return p(self)


def patch_printer_profile(printer):
    """Auto-add printer-dependent options that aren't in escpos profile"""
    profile = printer.profile

    # Default values in case printer is unknown
    profile.img_kwargs = {}
    profile.img_cut_index = 3
    profile.img_scale_factor = 1
    profile.img_x_scale_factor = 1
    profile.img_y_scale_factor = 1
    profile.sleep_time = 0

    # How many characters fit on one line with normal font size.
    # 42 is also default for TM-T88III.
    profile.default_char_count = 42
    # How many characters fit on one line with heading font size.
    # 21 is also default for TM-T88III.
    profile.big_char_count = 21

    # Special treatment for specific printer models.
    match profile.profile_data["name"]:
        case "TM-T88III":
            profile.img_kwargs = dict(
                impl="bitImageColumn",
                high_density_vertical=True,
                high_density_horizontal=True,
                center=False,
            )
            profile.default_char_count = 42
            profile.big_char_count = 21
            profile.img_cut_index = 4
        case "TM-U220B":
            profile.img_kwargs = dict(
                impl="bitImageColumn",
                high_density_vertical=False,
                high_density_horizontal=False,
                center=False,
                fragment_height=32,
            )
            # NOTE Numbers need less space than letters in case of this
            # printer (there is space for 40 numbers). Let's use the
            # smaller number to make sure everything always fits in one
            # line.
            profile.default_char_count = 33
            profile.big_char_count = 16
            profile.img_cut_index = 9
            # Profile is wrong, it's 200 dots, not 400
            # https://files.support.epson.com/pdf/pos/bulk/tm-u220_trg_en_std_reve.pdf
            # https://github.com/receipt-print-hq/escpos-printer-db/pull/87/commits/242299097
            profile.profile_data["media"]["width"]["pixels"] = 200

        case _:
            pass

    # Special treatment for specific connections to printer.
    match printer:
        case UsbPrinter():
            # Usb printer immediately returns, but is usually slower
            # than Python - improve synchronicity & sleep after each
            # print command. Otherwise we get a lot of timeouts &
            # printed gibberish. The time here seems to depend on the
            # printed material. If it's more dense & blackish / colorful,
            # then we need a higher value to not run into any trouble.
            # More spare material seems to be less problematic. Also
            # the problem becomes bigger if we print multiple pages.
            profile.sleep_time = 0.3
        case _:
            pass


def _is_binary_file(path):
    with open(path, "rb") as f:
        header = f.read(1024)
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    return bool(header.translate(None, textchars))


# XXX Fix circular import error


@functools.cache
def _ImagePreprocessor():
    from tinyprint.preprocessor import ImagePreprocessor

    return ImagePreprocessor


@functools.cache
def _PdfPreprocessor():

    from tinyprint.preprocessor import PdfPreprocessor

    return PdfPreprocessor


@functools.cache
def _MarkdownPreprocessor():

    from tinyprint.preprocessor import MarkdownPreprocessor

    return MarkdownPreprocessor
