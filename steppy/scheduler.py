# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import gevent
import signal
import sys
import time
import traceback

from gevent import queue

from .note_scheduler import NoteScheduler


class SchedulerEvents(object):

    SCHEDULE_STEP = 'on_schedule_step'
    PAUSE = 'on_pause'
    RESUME = 'on_resume'
    STEP_END = 'on_step_end'
    # STOP = 'on_stop'


class Scheduler(object):

    def __init__(self, sequencer, steps, tempo):
        self.sequencer = sequencer
        self.steps = steps
        self.tempo = tempo
        self.paused = False
        self.note_scheduler = NoteScheduler(sequencer, steps, tempo)
        self.control_queue = queue.Queue()
        self._target_time = None
        self._iteration = 0

    #def get_next_step_start_abs_time(self, step):
    #    now = t.time()
    #    return now + self.tempo.get_step_duration(self.steps.steps_per_beat)

    ##### PUBLIC API

    def schedule_note(self, step=None):
        self.note_scheduler.schedule_note(step or self.steps.current_step)

    def pause(self):
        self.on_pause()

    def resume(self):
        self.control_queue.put((SchedulerEvents.RESUME,))

    def end_step(self, step):
        self.on_step_end()

    #def stop(self):
    #    self.control_queue.put((SchedulerEvents.STOP,))

    def start(self):
        # print('*** Registering signal handlers ***')
        # self._register_signal_handlers()
        print('*** Starting note scheduler ***')
        self.note_scheduler.start()
        self._target_time = self._initial_time = time.time()
        g = gevent.Greenlet(self._gevent_loop)
        g.start()
        g.join()

    ####

    def _gevent_loop(self):
        print('** Scheduler: loop begin **')
        self.sequencer.clock_start()
        while True:
            while self.paused:
                self._execute_next_command(True)
                self._target_time = time.time()
            step = self.steps.current_step
            self.on_step_begin(step)
            self._iteration += 1
            self._target_time += self.tempo.get_step_duration(self.steps.steps_per_beat)
            gevent.sleep(self._target_time - time.time())
            # print('Total drift:', 1000*(time.time() - (self._initial_time + self._iteration * self.tempo.get_step_duration(self.steps.steps_per_beat))), 'ms')
            self.on_step_end(step)

    def _execute_next_command(self, wait=False):
        msg = self.control_queue.get(wait)
        ev, payload = msg[0], msg[1:]
        getattr(self, ev)(*payload)

    def on_step_begin(self, step):
        self.note_scheduler.schedule_note(step)
        self.sequencer.begin_step(step)

    def on_step_end(self, step):
        if not self.paused:
            self.sequencer.end_step(step)
            self.steps.next_step()

    def on_resume(self):
        if self.paused:
            print('[Scheduler] Resuming...')
            self.paused = False

    def on_pause(self):
        if not self.paused:
            print('[Scheduler] Pausing...')
            self.paused = True
