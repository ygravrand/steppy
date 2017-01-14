# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from collections import OrderedDict


class BaseController(object):

    def __init__(self, sequencer, port_name=''):
        self.sequencer = sequencer
        self.port_name = port_name
        self.rules_chains = OrderedDict()

    def register(self, name, func, rules_chain):
        """Register a function which will be called when the rules chain matches.
        In:
          - ``name`` -- A name for this registration
          - ``func`` -- A callable which will be given as arguments:
            - ``matched_messages`` -- The list of message having matched the rules chain
            - ``matched_rules`` -- The list of rules in the rules chain
          - ``rules_chain`` -- The rules chain
        """
        self.rules_chains[name] = (func, rules_chain)

    def handle_message(self, msg):
        print('Msg received: %s' % msg)
        for name, (func, rules_chain) in self.rules_chains.items():
            match, partial_match, res = rules_chain.run(func, msg)
            if match:
                print('%s : %s' % (name, res))

    def get_rules_chain_by_name(self, name):
        if name in self.rules_chains:
            return self.rules_chains[name][1]

    def __repr__(self):
        return self.port_name or 'GENERIC'
