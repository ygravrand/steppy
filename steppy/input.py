# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import mido


class Input(object):
    """An single input initialized from a controller"""

    def __init__(self, controller, port_name=''):
        self.controller = controller
        port_name = port_name or controller.port_name
        print('Opening input: %s' % port_name)
        self.interface = None
        try:
            self.interface = mido.open_input(port_name, autoreset=True)
        except:
            print('Error opening input: %s' % port_name)

    @property
    def enabled(self):
        return self.interface is not None

    def handle_message(self, msg):
        self.controller.handle_message(msg)

    def close(self):
        if self.interface:
            self.interface.close()
