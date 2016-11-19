# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message

from steppy.steps import Steps
from steppy.sequencer import Sequencer
from steppy.tempo import Tempo
from steppy.controllers.mininova import MiniNova


def get_mininova():
    steps = Steps()
    tempo = Tempo()
    seq = Sequencer(steps, tempo)
    mini = MiniNova(seq)
    return mini


def test_tempo():
    mini = get_mininova()
    tempo = mini.sequencer.tempo
    tempo_rules_chain = mini.get_rules_chain_by_name('TEMPO')

    last_msg = Message('control_change', control=99, value=2)
    mini.handle_message(last_msg)
    assert tempo_rules_chain.partial_match
    assert last_msg in tempo_rules_chain.matched_messages
    assert not tempo_rules_chain.full_match

    last_msg = Message('control_change', control=98, value=63)
    mini.handle_message(last_msg)
    assert tempo_rules_chain.partial_match
    assert last_msg in tempo_rules_chain.matched_messages
    assert not tempo_rules_chain.full_match

    last_msg = Message('control_change', control=6, value=0)
    mini.handle_message(last_msg)
    assert tempo_rules_chain.partial_match
    assert last_msg in tempo_rules_chain.matched_messages
    assert not tempo_rules_chain.full_match

    last_msg = Message('control_change', control=38, value=84)
    mini.handle_message(last_msg)
    assert not tempo_rules_chain.partial_match
    assert last_msg in tempo_rules_chain.matched_messages
    assert tempo_rules_chain.full_match
    assert tempo.bpm == 84


def test_overlapping_rules():
    mini = get_mininova()
    arpeg0_on_rule = mini.get_rules_chain_by_name('ARPEG #0 on')
    arpeg0_off_rule = mini.get_rules_chain_by_name('ARPEG #0 off')
    arpeg1_on_rule = mini.get_rules_chain_by_name('ARPEG #1 on')
    arpeg1_off_rule = mini.get_rules_chain_by_name('ARPEG #1 off')

    # *** ARPEG 0
    last_msg = Message('control_change', control=99, value=60)  # MSB
    mini.handle_message(last_msg)
    assert arpeg0_on_rule.partial_match
    assert not arpeg0_on_rule.full_match
    assert arpeg1_on_rule.partial_match
    assert not arpeg1_on_rule.full_match

    last_msg = Message('control_change', control=98, value=32)  # LSB
    mini.handle_message(last_msg)
    assert arpeg0_on_rule.partial_match
    assert not arpeg0_on_rule.full_match
    assert not arpeg1_on_rule.partial_match
    assert not arpeg1_on_rule.full_match

    last_msg = Message('control_change', control=6, value=127)  # MSB data
    mini.handle_message(last_msg)
    assert not arpeg0_on_rule.partial_match
    assert arpeg0_on_rule.full_match
    assert not arpeg1_on_rule.partial_match
    assert not arpeg1_on_rule.full_match

    # ARPEG 0 OFF
    last_msg = Message('control_change', control=99, value=60)  # MSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=98, value=32)  # LSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=6, value=0)  # MSB data
    mini.handle_message(last_msg)
    assert arpeg0_off_rule.full_match

    # ARPEG 0 ON
    last_msg = Message('control_change', control=99, value=60)  # MSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=98, value=32)  # LSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=6, value=127)  # MSB data
    mini.handle_message(last_msg)
    assert arpeg0_on_rule.full_match

    # ARPEG 1 ON
    last_msg = Message('control_change', control=99, value=60)  # MSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=98, value=33)  # LSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=6, value=127)  # MSB data
    mini.handle_message(last_msg)
    assert arpeg1_on_rule.full_match

    # ARPEG 1 OFF
    last_msg = Message('control_change', control=99, value=60)  # MSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=98, value=33)  # LSB
    mini.handle_message(last_msg)

    last_msg = Message('control_change', control=6, value=0)  # MSB data
    mini.handle_message(last_msg)
    assert arpeg1_off_rule.full_match
    assert not arpeg0_off_rule.full_match
