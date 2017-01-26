# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from ..note import Note
from ..rules import RulesChain, Rule
from .base_controller import BaseController


class Virtual(BaseController):

    def __init__(self, sequencer, console, port_name):
        super(Virtual, self).__init__(sequencer, console, port_name)

        self.register('NOTE ON', self.on_note_on, RulesChain(Rule(type_='note_on', velocity='!0')))
        self.register('NOTE OFF #1', self.on_note_off, RulesChain(Rule(type_='note_on', velocity=0)))
        self.register('NOTE OFF #2', self.on_note_off, RulesChain(Rule(type_='note_off')))

    def on_note_on(self, msgs, rules):
        self.sequencer.note_pressed(Note(numeric_note=msgs[0].note,
                                         velocity=msgs[0].velocity))

    def on_note_off(self, msgs, rules):
        self.sequencer.note_release()
