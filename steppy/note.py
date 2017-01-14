# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message


NOTES = 'C C# D D# E F F# G G# A A# B'.split(' ')


class Note(object):

    def __init__(self, note='', velocity=127, duration=0.2,
                 channel=0, numeric_note=None):
        self.note = numeric_note or self.parse_note(note)
        self.velocity = velocity
        self.duration = duration
        self.channel = channel

    def __repr__(self):
        return '%s (%s) - %.2f [%s] (%s)' % (self.as_text,
                                             self.note,
                                             self.duration,
                                             self.velocity,
                                             self.channel)

    def parse_note(self, note):
        if not note:
            return 60
        key, octave = note[:-1], note[-1]
        return 12 + int(octave) * 12 + NOTES.index(key)

    @property
    def as_text(self):
        return self.get_note_label(self.note)

    @staticmethod
    def get_note_label(numeric_note):
        return '%s%s' % (NOTES[numeric_note % 12],
                         int((numeric_note - 12) / 12))

    @staticmethod
    def from_note(note):
        if note:
            return Note(numeric_note=note.note,
                        velocity=note.velocity,
                        duration=note.duration,
                        channel=note.channel)

    @property
    def start_message(self):
        return Message('note_on',
                       note=self.note,
                       velocity=self.velocity,
                       channel=self.channel)

    @property
    def end_message(self):
        return Message('note_off',
                       note=self.note,
                       velocity=self.velocity,
                       channel=self.channel)
