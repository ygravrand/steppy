# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import gevent
import mido

from .input import Input


class Inputs(object):
    """Class aggregating the inputs of each controller"""

    def __init__(self, *controllers):
        self.inputs = [Input(controller) for controller in controllers]
        self.input_by_interface = {input_.interface: input_ for
                                   input_ in self.inputs}

    def add_controllers(self, *controllers):
        """Add the given controllers' input to the list of inputs we receive from"""
        for controller in controllers:
            input_ = Input(controller)
            self.inputs.append(input_)
            self.input_by_interface[input_.interface] = input_

    def activate_inputs(self):
        """Main activation method: launches a greenlet waiting for messages forever"""
        inputs_listener = gevent.Greenlet(self.receive_loop)
        inputs_listener.start()
        return inputs_listener

    def receive(self):
        """Receive from all inputs of all controllers"""
        for interface, msg in mido.ports.multi_receive([input_.interface
                                                        for input_ in self.inputs
                                                        if input_.interface is not None],
                                                       yield_ports=True):
            self.handle_message(interface, msg)

    def handle_message(self, interface, msg):
        if interface in self.input_by_interface:
            self.input_by_interface[interface].handle_message(msg)

    def close(self):
        for input_ in self.inputs:
            input_.close()

    def receive_loop(self):
        while True:
            self.receive()

    @property
    def enabled_controllers(self):
        return [input_.controller for input_ in self.inputs]
