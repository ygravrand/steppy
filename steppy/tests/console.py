# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""


class Console(object):

    def __init__(self, config=None):
        pass

    def start(self):
        pass

    def print_(self, msg):
        print(str(msg))

    big_print = print_
