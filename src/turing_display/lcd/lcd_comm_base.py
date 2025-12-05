# turing-smart-screen-python - a Python system monitor and library for
# USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2021-2023  Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import copy
import logging
import math
import os
import platform
import queue
import sys
import threading
import time
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Dict, Optional, Tuple

import serial
from PIL import Image, ImageDraw, ImageFont

from turing_display.lcd.color import Color, parse_color
from turing_display.lcd.exceptions import LcdInvalidParameterError, LcdNotConnectedError

log = logging.getLogger('turing_display')


class Orientation(IntEnum):
    PORTRAIT = 0
    LANDSCAPE = 2
    REVERSE_PORTRAIT = 1
    REVERSE_LANDSCAPE = 3


class LcdBase(ABC):
    def __init__(
        self,
        com_port: str = 'AUTO',
        display_width: int = 320,
        display_height: int = 480,
        update_queue: Optional[queue.Queue] = None,
    ):
        self.lcd_serial = None

        # String containing absolute path to serial port
        # e.g. "COM3", "/dev/ttyACM1" or "AUTO" for auto-discovery
        self.com_port = com_port

        # Display always start in portrait orientation by default
        self.orientation = Orientation.PORTRAIT
        # Display width in default orientation (portrait)
        self.display_width = display_width
        # Display height in default orientation (portrait)
        self.display_height = display_height

        # Queue containing the serial requests to send to the screen.
        # An external thread should run to process requests
        # on the queue. If you want serial requests to be done in sequence, set it to None
        self.update_queue = update_queue

        # Mutex to protect the queue in case a thread want to add
        # multiple requests (e.g. image data) that should not be
        # mixed with other requests in-between
        self.update_queue_mutex = threading.Lock()

        # Create a cache to store opened images, to avoid opening and
        # loading from the filesystem every time
        self.image_cache = {}  # { key=path, value=PIL.Image }

        # Create a cache to store opened fonts, to avoid opening and
        # loading from the filesystem every time
        self.font_cache: Dict[
            Tuple[str, int],  # key=(font, size)
            ImageFont.FreeTypeFont,  # value= a loaded freetype font
        ] = {}

    def get_width(self) -> int:
        """Returns the current display width accounting for current orientation.

        In portrait or reverse portrait, returns display_width; in landscape or reverse landscape,
        returns display_height.

        Returns:
            int: Display width in current orientation
        """
        return (
            self.display_width
            if (
                self.orientation == Orientation.PORTRAIT
                or self.orientation == Orientation.REVERSE_PORTRAIT
            )
            else self.display_height
        )

    def get_height(self) -> int:
        return (
            self.display_height
            if (
                self.orientation == Orientation.PORTRAIT
                or self.orientation == Orientation.REVERSE_PORTRAIT
            )
            else self.display_width
        )

    def open_serial(self):
        if self.com_port == 'AUTO':
            self.com_port = self.auto_detect_com_port()
            if not self.com_port:
                log.error('Cannot find COM port automatically please select COM port manually')
                try:
                    sys.exit(0)
                except Exception:
                    os._exit(0)
            else:
                log.debug(f'Auto detected COM port: {self.com_port}')
        else:
            log.debug(f'Static COM port: {self.com_port}')

        try:
            self.lcd_serial = serial.Serial(self.com_port, 115200, timeout=1, rtscts=True)
        except Exception as e:
            log.error(f'Cannot open COM port {self.com_port}: {e}')
            try:
                sys.exit(0)
            except Exception:
                os._exit(0)

    def close_serial(self):
        if self.lcd_serial and self.lcd_serial.is_open:
            self.lcd_serial.close()

    def serial_write(self, data: bytes):
        self.lcd_serial.write(data)  # type: ignore #  self. lcd_serial is already checked

    def serial_read(self, size: int) -> bytes:
        self.check_port()
        return self.lcd_serial.read(size)  # type: ignore #  self. lcd_serial is already checked

    def check_port(self):
        if not (self.lcd_serial and self.lcd_serial.is_open):
            msg = 'COM port not opened'
            raise LcdNotConnectedError(msg)

    def serial_flush_input(self):
        self.check_port()
        self.lcd_serial.reset_input_buffer()  # type: ignore #  self. lcd_serial is already checked

    def write_data(self, byte_buffer: bytearray):
        self.check_port()
        self.write_line(bytes(byte_buffer))

    def send_line(self, line: bytes):
        if self.update_queue:
            # Queue the request. Mutex is locked by caller to queue multiple lines
            self.update_queue.put((self.write_line, [line]))
        else:
            # If no queue for async requests: do request now
            self.write_line(line)

    def write_line(self, line: bytes):
        try:
            self.serial_write(line)
            if platform.system() == 'Darwin':
                # macOS needs the serial buffer to be flushed regularly to avoid
                # bitmap corruption on the display
                # See https://github.com/mathoudebine/turing-smart-screen-python/issues/7
                self.lcd_serial.flush()  # pyright: ignore[reportOptionalMemberAccess]
        except serial.SerialTimeoutException:
            # We timed-out trying to write to our device, slow things down.
            log.warning('(Write line) Too fast! Slow down!')
        except serial.SerialException:
            # Error writing data to device: close and reopen serial port, try to write again
            log.error(
                'SerialException: Failed to send serial data to device. '
                'Closing and reopening COM port before retrying once.'
            )
            self.close_serial()
            time.sleep(1)
            self.open_serial()
            # todo: retry only once, then raise exception
            self.serial_write(line)

    def read_data(self, read_size: int):
        try:
            response = self.serial_read(read_size)
            # logger.debug("Received: [{}]".format(str(response, 'utf-8')))
        except serial.SerialTimeoutException:
            # We timed-out trying to read from our device, slow things down.
            log.warning('(Read data) Too fast! Slow down!')
        except serial.SerialException:
            # Error writing data to device: close and reopen serial port, try to read again
            log.error(
                'SerialException: Failed to read serial data from device. '
                'Closing and reopening COM port before retrying once.'
            )
            self.close_serial()
            time.sleep(1)
            self.open_serial()
            # todo: retry only once, then raise exception
            return self.serial_read(read_size)
        else:
            return response

    @staticmethod
    @abstractmethod
    def auto_detect_com_port() -> Optional[str]:
        pass

    @abstractmethod
    def initialize_comm(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def screen_off(self):
        pass

    @abstractmethod
    def screen_on(self):
        pass

    @abstractmethod
    def set_brightness(self, level: int):
        pass

    @abstractmethod
    def set_orientation(self, orientation: Orientation):
        pass

    @abstractmethod
    def display_pil_image(
        self,
        image: Image.Image,
        x: int = 0,
        y: int = 0,
        image_width: int = 0,
        image_height: int = 0,
    ):
        pass

    def display_bitmap(
        self, bitmap_path: str, x: int = 0, y: int = 0, width: int = 0, height: int = 0
    ):
        image = self.open_image(bitmap_path)
        self.display_pil_image(image, x, y, width, height)

    def _check_position_and_size(self, x: int, y: int, width: int, height: int):
        if any(param < 0 for param in [x, y, width, height]):
            err_msg = 'All parameters should be >= 0'
            raise LcdInvalidParameterError(err_msg)
        if x >= self.display_width or y >= self.get_height():
            err_msg = 'X and Y coordinates must be within the display.'
            raise LcdInvalidParameterError(err_msg)
        if x + width > self.get_width() or y + height > self.get_height():
            err_msg = 'Object doesn´t fit on display.'
            breakpoint()
            raise LcdInvalidParameterError(err_msg)

    def _check_in_boundaries(self, x: int, y: int):
        if not x <= self.get_width() - 1:
            msg = f'X coordinate {x} is out of display width boundary'
            raise ValueError(msg)
        if not y <= self.get_height() - 1:
            msg = f'Y coordinate {y} is out of display height boundary'
            raise ValueError(msg)

    def display_text(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        font: str = './res/fonts/roboto-mono/RobotoMono-Regular.ttf',
        font_size: int = 20,
        font_color: Color = (0, 0, 0),
        background_color: Color = (255, 255, 255),
        background_image: Optional[str] = None,
        align: str = 'left',
        anchor: str = 'la',
    ):
        # Convert text to bitmap using PIL and display it
        # Provide the background image path to display text with transparent background

        font_color = parse_color(font_color)
        background_color = parse_color(background_color)
        self._check_in_boundaries(x, y)

        if len(text) > 0:
            err_msg = 'Text must not be empty'
            raise LcdInvalidParameterError(err_msg)
        if font_size <= 0:
            err_msg = 'Font size must be > 0'
            raise LcdInvalidParameterError(err_msg)

        # If only width is specified, assume height based on font size (one-line text)
        if width > 0 and height == 0:
            height = font_size

        if background_image is None:
            # A text bitmap is created with max width/height by default :
            # text with solid background
            text_image = Image.new('RGB', (self.get_width(), self.get_height()), background_color)
        else:
            # The text bitmap is created from provided background image :
            # text with transparent background
            text_image = self.open_image(background_image)

        # Get text bounding box
        ttfont = self.open_font(font, font_size)
        d = ImageDraw.Draw(text_image)

        if width == 0 or height == 0:
            left, top, right, bottom = d.textbbox(
                (x, y), text, font=ttfont, align=align, anchor=anchor
            )

            # textbbox may return float values, which is not good for the bitmap operations below.
            # Let's extend the bounding box to the next whole pixel in all directions
            left, top = math.floor(left), math.floor(top)
            right, bottom = math.ceil(right), math.ceil(bottom)
        else:
            left, top, right, bottom = x, y, x + width, y + height

            if anchor.startswith('m'):
                x = int((right + left) / 2)
            elif anchor.startswith('r'):
                x = right
            else:
                x = left

            if anchor.endswith('m'):
                y = int((bottom + top) / 2)
            elif anchor.endswith('b'):
                y = bottom
            else:
                y = top

        # Draw text onto the background image with specified color & font
        d.text((x, y), text, font=ttfont, fill=font_color, align=align, anchor=anchor)

        # Restrict the dimensions if they overflow the display size
        left = max(left, 0)
        top = max(top, 0)
        right = min(right, self.get_width())
        bottom = min(bottom, self.get_height())

        # Crop text bitmap to keep only the text
        text_image = text_image.crop(box=(left, top, right, bottom))

        self.display_pil_image(text_image, left, top)

    # Load image from the filesystem, or get from the cache if it has already been loaded previously
    def open_image(self, bitmap_path: str) -> Image.Image:
        if bitmap_path not in self.image_cache:
            log.debug(f'Bitmap {bitmap_path} is now loaded in the cache')
            self.image_cache[bitmap_path] = Image.open(bitmap_path)
        return copy.copy(self.image_cache[bitmap_path])

    def open_font(self, name: str, size: int) -> ImageFont.FreeTypeFont:
        if (name, size) not in self.font_cache:
            self.font_cache[(name, size)] = ImageFont.truetype(name, size)
        return self.font_cache[(name, size)]
