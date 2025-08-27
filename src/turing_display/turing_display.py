#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Turing display driver'
__project_link__ = 'https://www.boxfish.be'

import logging

from .__version__ import __version__

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TuringDisplay:
    def __init__(self):
        log.warning(f'TuringDisplay (v{__version__}) initialized.')
