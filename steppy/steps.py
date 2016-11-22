# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message

from .note import Note


class Step(object):

    def __init__(self, note, pos, on=False):
        self.note = note
        self.pos = pos
        self._on = on
        self.cc = None

    def __repr__(self):
        return '#%d - %s - %s' % (self.pos + 1, 'ON ' if self.on else 'OFF', self.note or '')

    @property
    def start_messages(self):
        res = []
        if self.cc:
            res.append(self.cc)
        if self.note:
            res.append(self.note.start_message)
        return res

    @property
    def end_message(self):
        if self.note:
            return self.note.end_message

    @property
    def duration(self):
        if self.note:
            return self.note.duration

    @property
    def on(self):
        return self._on and self.note is not None

    @on.setter
    def on(self, on):
        if self.note is not None:
            self._on = on

    def set_note(self, note):
        self.set_pitch(note.note)
        self.set_duration(note.duration)
        self.set_velocity(note.velocity)
        self.on = True

    def set_pitch(self, value):
        if self.note is None:
            self.note = Note()
        self.note.note = value

    def set_duration(self, value):
        if self.note is None:
            self.note = Note()
        self.note.duration = value

    def set_velocity(self, value):
        if self.note is None:
            self.note = Note()
        self.note.velocity = value

    def set_cc(self, control, value):
        self.cc = Message(type='control_change', control=control, value=value)

    def clear(self):
        self.note = None
        self.cc = None


class Steps(object):

    def __init__(self, step_count=8, steps_per_beat=4):
        self.steps_per_beat = steps_per_beat
        notes = [None] * step_count
        self.steps = [Step(note, i) for i, note in enumerate(notes)]
        self.current_step_index = -1

    @property
    def current_step(self):
        return self.steps[self.current_step_index]

    def get_previous_step_index(self):
        return self.current_step_index - 1 if self.current_step_index > 0 else len(self.steps) - 1

    def get_next_step_index(self):
        return (self.current_step_index + 1) % len(self.steps)

    @property
    def step_count(self):
        return len(self.steps)

    def get_current_row(self, steps_per_row=8):
        return int(self.current_step_index / steps_per_row)

    def increase_step_count(self):
        self.steps[len(self.steps):len(self.steps)*2] = [Step(Note.from_note(step.note), i+len(self.steps))
                for i, step in enumerate(self.steps)]
        print(self.steps)

    def clear(self):
        for step in self.steps:
            step.clear()

    def get_step(self, pos=None):
        return self.steps[pos] if pos is not None and pos >= 0 and pos < len(self.steps) else self.current_step

    def set_step_note(self, note, pos=None):
        self.get_step(pos).set_note(note)

    def set_step_pitch(self, value, pos=None):
        self.get_step(pos).set_pitch(value)

    def set_step_duration(self, value, pos=None):
        self.get_step(pos).set_duration(value)

    def set_step_velocity(self, value, pos=None):
        self.get_step(pos).set_velocity(value)

    def set_step_cc(self, control, value, pos=None):
        self.get_step(pos).set_cc(control, value)

    def prev_step(self):
        self.current_step_index = self.get_previous_step_index()
        if self.current_step_index == 0:
            print('#'*16)
        print(self.current_step)
        return self.current_step

    def next_step(self):
        self.current_step_index = self.get_next_step_index()
        if self.current_step_index == 0:
            print('#'*16)
        print(self.current_step)
        return self.current_step

    def toggle_step(self, pos):
        step = self.get_step(pos)
        if step:
            if not step.on and step.note is None:
                # Take the previous activated step's note
                lst = self.steps[pos::-1] + self.steps[:pos:-1]
                steps_on = [step_ for step_ in lst if step_.on]
                if steps_on:
                    step.note = Note.from_note(steps_on[0].note)
            step.on = not step.on
            return step

    def __repr__(self):
        return '[' + ', '.join(['ON ' if step.on else 'OFF' for step in self.steps]) + ']'

    def get_current_step_str(self, pos=None):
        step = self.get_step(pos)
        return '%d : %s %s' % (step.pos + 1,
                              step.note.as_text if step.note else '--',
                              ('(%.2f)' % step.duration) if step.duration else '')
