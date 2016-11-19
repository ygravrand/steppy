# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import pyfiglet

from multiprocessing import Process, Queue


class Console(object):

    def __init__(self, max_queue_size=1000):
        self.queue = Queue(max_queue_size)
        self._process = None

    def start(self):
        self._process = Process(target=self._start)
        self._process.start()
        return self._process

    def _start(self):
        while True:
            msg = self.queue.get()
            pyfiglet.print_figlet(msg, 'basic')

    def print_str(self, msg):
        self.queue.put(str(msg))
