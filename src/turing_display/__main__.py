#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99


__author__ = 'Dieter Vansteenwegen'
__project__ = 'Turing display driver'
__project_link__ = 'https://www.boxfish.be'

from . import TuringDisplay  # noqa: F401


def test_display():
    """Test function to initialize and test the Turing display."""
    display = TuringDisplay(port='AUTO', width=480, height=320)
    display.initialize_display(reset=True, brightness=100)
    display.turn_on(display_test_pattern=True)
    display.display_test_text()


def check_logging_requirements():
    """Check if logging requirements are met."""
    import logging
    import os

    log_level = os.getenv('ENABLE_TURING_DISPLAY_DEBUG', 'FALSE').upper()
    if log_level == 'TRUE':
        print('Enabling debug logging for turing_display')
        logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    check_logging_requirements()
    test_display()
