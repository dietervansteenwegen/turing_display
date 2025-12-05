#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Turing display driver'
__project_link__ = 'https://www.boxfish.be'

import logging
import queue
from typing import Optional

from .__version__ import __version__
from .lcd.lcd_comm_base import Orientation
from .lcd.lcd_comm_rev_a import LcdCommRevA
from .resources import get_data_path

log = logging.getLogger('turing_display')


def _get_full_path(path, name):
    if name:
        return path + name
    else:
        return None


class TuringDisplay:
    def __init__(
        self,
        width: int = 480,
        height: int = 320,
        port: Optional[str] = 'AUTO',
        orientation: Optional[Orientation] = Orientation.LANDSCAPE,
        update_queue: Optional[queue.Queue] = None,
    ):
        log.debug(f'TuringDisplay (v{__version__}) initialized.')
        self.lcd = LcdCommRevA(update_queue=update_queue)
        self._width = width
        self._height = height
        self._orientation = orientation
        port = port

    def initialize_display(self, reset: bool = True, brightness: int = 127):
        if reset:
            self.lcd.reset()
        self.lcd.initialize_comm()
        self.turn_on(brightness=brightness)
        self.lcd.set_orientation(self._orientation)

    def turn_on(
        self,
        brightness: Optional[int] = None,
        display_test_pattern: Optional[bool] = False,
    ):
        self.lcd.screen_on()

        if brightness:
            self.lcd.set_brightness(brightness)
        if display_test_pattern:
            self.display_test_pattern()

    def turn_off(self):
        self.lcd.screen_off()

    def display_test_pattern(self):
        fn = get_data_path('test_pattern_480x320.png')
        self.lcd.display_bitmap(
            bitmap_path=str(fn), x=0, y=0, width=self._width, height=self._height
        )

    def display_test_text(self):
        self.lcd.display_text(
            text='Turing Display\nTest Pattern',
            x=0,
            y=0,
            width=self._width,
            height=self._height,
            font_size=24,
            font_color=(255, 0, 0),
            background_color=(0, 0, 0),
            align='center',
            anchor='mm',
        )
