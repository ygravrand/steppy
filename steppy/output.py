# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import mido


class Output(object):

    def __init__(self, controller, port_name=''):
        self.controller = controller
        port_name = port_name or controller.port_name
        print('Opening output: %s' % port_name)
        self.interface = None
        try:
            self.interface = mido.open_output(port_name, autoreset=True)
        except:
            print('Error opening output: %s' % port_name)

    @property
    def enabled(self):
        return self.interface is not None

    def send(self, *messages):
        for message in messages:
            if self.interface:
                self.interface.send(message)

    def close(self):
        if self.interface:
            print('All notes off')
            self.interface.send(mido.Message(type='control_change', control=123, value=0))
            self.interface.reset()
            self.interface.close()
