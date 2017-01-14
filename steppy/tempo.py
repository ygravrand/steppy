# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import time


class DurationComputer(object):

    def __init__(self):
        self._start = time.time()

    @property
    def duration(self):
        assert self._start
        return time.time() - self._start


class Tempo(object):

    def __init__(self, bpm=120):
        self._bpm = None
        self.bpm = bpm
        self._duration_computer = None

    @property
    def bpm(self):
        return self._bpm

    @bpm.setter
    def bpm(self, bpm):
        self._bpm = bpm

    def get_note_duration(self, steps_per_beat, step):
        assert step.duration > 0 and step.duration <= 1
        assert steps_per_beat > 0 and steps_per_beat % 2 == 0
        return step.duration * 60.0 / (self.bpm * steps_per_beat)

    def get_step_duration(self, steps_per_beat):
        assert steps_per_beat > 0 and steps_per_beat % 2 == 0
        return 60.0 / (self.bpm * steps_per_beat)

    def start_recording_duration(self):
        self._duration_computer = DurationComputer()

    def compute_elapsed_duration(self, steps_per_beat):
        if self._duration_computer:
            dur = self._duration_computer.duration
            return min(dur / self.get_step_duration(steps_per_beat), 1.0)
