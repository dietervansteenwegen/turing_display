#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Turing display driver'
__project_link__ = 'https://www.boxfish.be'

import logging
import queue
from typing import Optional

from turing_display.__version__ import __version__
from turing_display.lcd.lcd_comm_base import Orientation
from turing_display.lcd.lcd_comm_rev_a import LcdCommRevA
from turing_display.resources import get_data_path

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
        # Send initialization commands
        self.lcd.initialize_comm()
        # Turn on display, set brightness and LEDs for supported HW
        self.turn_on(brightness=brightness)

        # Set orientation
        self.lcd.set_orientation(self._orientation)

    def turn_on(
        self,
        brightness: Optional[int] = None,
        display_test_pattern: Optional[bool] = False,
    ):
        # Turn screen on in case it was turned off previously
        self.lcd.screen_on()

        if brightness:
            # Set brightness
            self.lcd.set_brightness(brightness)
        if display_test_pattern:
            # Display test pattern
            self.display_test_pattern()
        # Set backplate RGB LED color (for supported HW only)
        # self.lcd.set_backplate_led_color(
        # config.THEME_DATA['display'].get('DISPLAY_RGB_LED', (255, 255, 255))
        # )

    def turn_off(self):
        # Turn screen off
        self.lcd.screen_off()

        # Turn off backplate RGB LED
        # self.lcd.set_backplate_led_color(led_color=(0, 0, 0))  # TODO, check supported for all

    def display_test_pattern(self):
        fn = get_data_path('test_pattern_480x320.png')
        self.lcd.display_bitmap(
            bitmap_path=str(fn), x=0, y=0, width=self._width, height=self._height
        )

    # def display_static_image(self):
    #     if config.THEME_DATA.get('static_images', False):
    #         for image in config.THEME_DATA['static_images']:
    #             log.debug(f'Drawing Image: {image}')
    #             self.lcd.display_bitmap(
    #                 bitmap_path=config.THEME_DATA['PATH']
    #                 + config.THEME_DATA['static_images'][image].get('PATH'),
    #                 x=config.THEME_DATA['static_images'][image].get('X', 0),
    #                 y=config.THEME_DATA['static_images'][image].get('Y', 0),
    #                 width=config.THEME_DATA['static_images'][image].get('WIDTH', 0),
    #                 height=config.THEME_DATA['static_images'][image].get('HEIGHT', 0),
    #             )

    # def display_static_text(self):
    #     if config.THEME_DATA.get('static_text', False):
    #         for text in config.THEME_DATA['static_text']:
    #             log.debug(f'Drawing Text: {text}')
    #             self.lcd.display_text(
    #                 text=config.THEME_DATA['static_text'][text].get('TEXT'),
    #                 x=config.THEME_DATA['static_text'][text].get('X', 0),
    #                 y=config.THEME_DATA['static_text'][text].get('Y', 0),
    #                 width=config.THEME_DATA['static_text'][text].get('WIDTH', 0),
    #                 height=config.THEME_DATA['static_text'][text].get('HEIGHT', 0),
    #                 font=config.FONTS_DIR
    #                 + config.THEME_DATA['static_text'][text].get(
    #                     'FONT', 'roboto-mono/RobotoMono-Regular.ttf'
    #                 ),
    #                 font_size=config.THEME_DATA['static_text'][text].get('FONT_SIZE', 10),
    #                 font_color=config.THEME_DATA['static_text'][text].get('FONT_COLOR', (0, 0, 0)),
    #                 background_color=config.THEME_DATA['static_text'][text].get(
    #                     'BACKGROUND_COLOR', (255, 255, 255)
    #                 ),
    #                 background_image=_get_full_path(
    #                     config.THEME_DATA['PATH'],
    #                     config.THEME_DATA['static_text'][text].get('BACKGROUND_IMAGE', None),
    #                 ),
    #                 align=config.THEME_DATA['static_text'][text].get('ALIGN', 'left'),
    #                 anchor=config.THEME_DATA['static_text'][text].get('ANCHOR', 'lt'),
    #             )
