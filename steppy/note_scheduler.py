# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import gevent

from gevent import queue
from copy import deepcopy


class NoteSchedulerEvents(object):

    SCHEDULE_NOTE = 'on_schedule_note'
    STOP = 'on_stop'


class NoteScheduler(object):

    def __init__(self, sequencer, steps, tempo):
        self.sequencer = sequencer
        self.steps = steps
        self.tempo = tempo
        self.control_queue = queue.Queue()

    def start(self):
        g = gevent.Greenlet(self._start)
        g.start()

    def _start(self):
        while True:
            self._execute_command()


    def _get_note_end_abs_time(self, step):
        now = self._loop.time()
        return now + self.tempo.get_note_duration(self.steps.steps_per_beat, step)

    ##### PUBLIC API - will be called from other threads

    def schedule_note(self, step):
        if step.on:
            self.control_queue.put((NoteSchedulerEvents.SCHEDULE_NOTE, step))

    def stop(self):
        self.control_queue.put((NoteSchedulerEvents.STOP,))

    ####

    def on_schedule_note(self, step):
        if step.on:
            # "Freeze" current step. It could be modified in real time,
            # which is fine except if the pitch has changed and we output
            # the end message on the wrong note...
            step = deepcopy(step)
            self.sequencer.begin_note(step)
            gevent.sleep(self.tempo.get_note_duration(self.steps.steps_per_beat, step))
            self.sequencer.end_note(step)

    def on_stop(self):
        # Don't schedule anything and don't call the loop again
        # This is sufficient to stop.
        pass

    def _execute_command(self):
        msg = self.control_queue.get()
        ev, payload = msg[0], msg[1:]
        getattr(self, ev)(*payload)
