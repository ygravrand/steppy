# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""
import pyfiglet

from multiprocessing import Process, Queue


class Console(object):

    configspec = {
        'console': {
            'font': 'string(default="basic")',
            'queue_size': 'integer(default=10)'
        }
    }

    def __init__(self, config=None):
        self.font = config['console']['font'] if config else 'basic'
        self.queue = Queue(config['console']['queue_size'] if config else 10)
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
        self.queue.put((True, str(msg)))

    def print_(self, msg):
        self.queue.put((False, str(msg)))
