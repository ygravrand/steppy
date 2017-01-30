# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""
import pyfiglet

from multiprocessing import Process, Queue
from six.moves import queue


class Console(object):

    configspec = {
        'console': {
            'font': 'string(default="basic")',      # pyfiglet font
            'queue_size': 'integer(default=10)',    # discard messages when more than ``queue_size`` are left to print
            'terse': 'boolean(default=True)'       # if True, print BIG messages only
        }
    }

    def __init__(self, config=None):
        self.font = config['console']['font'] if config else 'basic'
        self.queue = Queue(config['console']['queue_size'] if config else 10)
        self.terse = config['console']['terse'] if config else False
        self._process = None

    def start(self):
        self._process = Process(target=self._start)
        self._process.start()
        return self._process

    def _start(self):
        while True:
            big, msg = self.queue.get()
            if big:
                pyfiglet.print_figlet(msg, self.font)
            else:
                print(msg)

    def big_print(self, msg):
        try:
            self.queue.put((True, str(msg)), False)
        except queue.Full:
            pass

    def print_(self, msg):
        if not self.terse:
            try:
                self.queue.put((False, str(msg)), False)
            except queue.Full:
                pass
