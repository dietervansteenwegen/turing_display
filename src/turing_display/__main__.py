#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99


__author__ = 'Dieter Vansteenwegen'
__project__ = 'Turing display driver'
__project_link__ = 'https://www.boxfish.be'

from . import TuringDisplay  # noqa: F401


def test_display():
    """Test function to initialize and test the Turing display."""
    display = TuringDisplay(port='/tty/ttyACM0', width=480, height=320)
    display.initialize_display(reset=True, brightness=100)
    display.turn_on(display_test_pattern=True)


if __name__ == '__main__':
    test_display()
