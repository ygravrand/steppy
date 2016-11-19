# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message

from .rules import Rule, RulesChain


def msb_lsb_rules_chain(msb, msb_value=None, lsb=None, lsb_value=None):
    # Create rules for NRPN/MSB and NRPN/LSB messages.
    # In:
    #  - ``msb`` -- MSB message number to wait for
    #  - ``msb_value`` -- If not None, also filters on MSB data entry value
    #  - ``lsb`` -- LSB message number to wait for
    #  - ``lsb_value`` -- If not None, also filters on LSB data entry value
    # Return:
    #  - A Rule aggregating the sequence of events to wait for
    chain = RulesChain(
        Rule(type_='control_change', control=99, value=msb),
        Rule(type_='control_change', control=98, value=lsb or 0)
    )

    criteria = {'value': msb_value} if msb_value is not None else {}
    chain.add_rule(Rule(type_='control_change', control=6, **criteria))  # Data entry MSB

    if lsb is not None and lsb_value is not None:
        chain.add_rule(Rule(type_='control_change', control=38, value=lsb_value))  # Data entry LSB
    return chain


def msb_lsb_output(msb, msb_value, lsb=None, lsb_value=None):
    return [
        Message('control_change', control=99, value=msb),
        Message('control_change', control=98, value=lsb or 0),
        Message('control_change', control=6, value=msb_value),
        Message('control_change', control=38, value=lsb_value or 0)
    ]
