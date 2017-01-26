# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message

from steppy.steps import Steps
from steppy.sequencer import Sequencer
from steppy.tempo import Tempo
from steppy.controllers.launchcontrol import LaunchControl

from .console import Console


def get_launchcontrol():
    console = Console()
    seq = Sequencer(console, Steps(console), Tempo())
    lc = LaunchControl(seq, console)
    return lc


def test_rotaries():
    lc = get_launchcontrol()
    rotary_8_rules_chain = lc.get_rules_chain_by_name('ROTARIES: FIRST ROW #8')

    last_msg = Message('control_change', channel=8, control=28, value=65)
    lc.handle_message(last_msg)
    print(rotary_8_rules_chain.rules)
    assert rotary_8_rules_chain.full_match
    assert last_msg in rotary_8_rules_chain.matched_messages

    print('------')

    last_msg = Message('control_change', channel=8, control=28, value=66)
    lc.handle_message(last_msg)
    print(rotary_8_rules_chain.rules)
    assert rotary_8_rules_chain.full_match
    assert last_msg in rotary_8_rules_chain.matched_messages
