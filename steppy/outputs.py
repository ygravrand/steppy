# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from .output import Output


class Outputs(object):
    """Class aggregating the outputs of each controller"""

    def __init__(self):
        self.outputs = []
        self.output_by_controller = {}

    def add_controllers(self, *controllers):
        """Add the given controllers' output to the list of outputs we send to"""
        for controller in controllers:
            output_ = Output(controller)
            if output_.enabled:
                self.outputs.append(output_)
                self.output_by_controller[output_.controller] = output_

    def send(self, controller, *messages):
        """Send messages to a specific controller"""
        if controller in self.output_by_controller:
            self.output_by_controller[controller].send(*messages)

    def send_to_all(self, *messages):
        """Send messages to all controllers' outputs"""
        for output in self.outputs:
            output.send(*messages)

    def close(self):
        for output_ in self.outputs:
            output_.close()

    @property
    def enabled_controllers(self):
        return [output_.controller for output_ in self.outputs]
