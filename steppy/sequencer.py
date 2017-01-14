# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import gevent

from gevent import monkey; monkey.patch_all()  # noqa: E702
from mido import Message

from . import steps_persister
from .controllers.base_controller import BaseController
from .inputs import Inputs
from .outputs import Outputs
from .scheduler import Scheduler
from .sequencer_events import SequencerEvents


class Sequencer(object):

    def __init__(self, console, steps, tempo, controllers_config=None):
        self.console = console
        self.steps = steps
        self.tempo = tempo
        self.inputs = Inputs()
        self.outputs = Outputs()
        self.synths = []
        self.current_synth_index = None
        self.events = SequencerEvents()
        self.scheduler = Scheduler(self, console, steps, tempo)
        self.paused = False
        self._next_step_on_note = False
        self._saved_note = None  # The note currently played by the user
        self.protected = False

        if controllers_config is not None:
            controllers_config.init_controllers(self)
            self.inputs.add_controllers(*controllers_config.inputs)
            self.outputs.add_controllers(*controllers_config.outputs)
            self.set_synths(*controllers_config.synths)

    def set_synths(self, *controllers):
        self.synths = controllers
        if self.synths:
            self.current_synth_index = 0

    def output(self, controller, *messages):
        assert isinstance(controller, BaseController), \
            '``output`` first argument must be a controller (found %s)' % \
            (controller.__class__.__name__ if controller else 'None')
        self.outputs.send(controller, *messages)

    def on(self, event, controller, fun):
        self.events.on(event, controller, fun)

    def set_event(self, event, *args):
        self.events.set_event(event, args, self.outputs.enabled_controllers)

    @property
    def step_count(self):
        return self.steps.step_count

    @property
    def current_step(self):
        return self.steps.current_step

    def get_step(self, pos=None):
        return self.steps.get_step(pos)

    @property
    def next_step_on_note(self):
        return self._next_step_on_note

    @next_step_on_note.setter
    def next_step_on_note(self, on):
        self.big_print('NEXT STEP ON  NOTE %s' % ('on' if on else 'off'))
        self._next_step_on_note = on

    def big_print(self, msg):
        gevent.idle()
        self.console.big_print(msg)

    def start(self):
        try:
            self.console.start()
            print('Activating inputs')
            self.inputs.activate_inputs()
            self.set_event(SequencerEvents.START)
            print('Starting scheduler')
            self.scheduler.start()
        except KeyboardInterrupt:
            self.stop()

    def clock_start(self):
        self.outputs.send_to_all(Message(type='start'), Message(type='clock'))

    def stop(self):
        # Give a chance to send stop messages...
        self.set_event(SequencerEvents.STOP)
        # And close ports
        self.inputs.close()
        self.outputs.close()
        steps_persister.save(self.steps)
        raise SystemExit()

    def pause(self):
        if self.paused:
            self.next_step_on_note = not self.next_step_on_note
            # Call listeners
            self.set_event(SequencerEvents.PAUSE, self.steps)
        else:
            self._pause()

    def _pause(self):
        self.paused = True
        self.scheduler.pause()
        self.big_print('PAUSE')
        self.print_step()
        # Call listeners
        self.set_event(SequencerEvents.PAUSE, self.steps)

    def resume(self):
        if self.paused:
            self.big_print('RESUME')
            self.paused = False
            self.scheduler.resume()
            # Call listeners
            self.set_event(SequencerEvents.RESUME, self.steps.current_step)

    def print_step(self, pos=None):
        self.big_print(self.steps.get_current_step_str(pos))

    def begin_step(self, step):
        if not self.paused:
            self.set_event(SequencerEvents.STEP_BEGIN, step)

    def end_step(self, step):
        # If saved note was played for 'too long', force its end
        if self._saved_note and \
           self._saved_note.duration > self.tempo.get_step_duration(self.steps.steps_per_beat):
            self.note_release(True)
        if not self.paused:
            self.set_event(SequencerEvents.STEP_END, step)

    def begin_note(self, step):
        if self.current_synth_index is not None:
            self.output(self.synths[self.current_synth_index], *step.start_messages)

    def end_note(self, step):
        if self.current_synth_index is not None:
            self.output(self.synths[self.current_synth_index], step.end_message)

    def prev_step(self):
        if self.paused:
            step = self.steps.prev_step()
            # Play note
            self.scheduler.schedule_note(step)
            # Call listeners
            self.set_event(SequencerEvents.PAUSE, self.steps)
            self.print_step()

    def next_step(self, play_note=True):
        if self.paused:
            step = self.steps.next_step()
            # Play note
            if play_note:
                self.scheduler.schedule_note(step)
            # Call listeners
            self.set_event(SequencerEvents.PAUSE, self.steps)
            self.print_step()

    def note_pressed(self, note):
        if not self.protected:
            self._saved_note = note
            self.tempo.start_recording_duration()

    def note_release(self, force=False):
        if not self.protected:
            if self._saved_note:
                self._saved_note.duration = 1.0 if force else \
                    self.tempo.compute_elapsed_duration(self.steps.steps_per_beat)
                self.set_step_note(self._saved_note)
                self._saved_note = None

    def set_step_note(self, note):
        # Full attributes: pitch, duration, velocity,...
        self.steps.set_step_note(note)
        self.print_step()
        if self.paused:
            if self.next_step_on_note:
                # Move forward but don't play note, it is confusing
                self.next_step(False)
            else:
                # Call listeners
                self.set_event(SequencerEvents.PAUSE, self.steps)
                # Play note
                self.scheduler.schedule_note(self.steps.get_step())

    def set_step_pitch(self, value, pos=None):
        self.steps.set_step_pitch(value, pos)
        step = self.steps.get_step(pos)
        self.big_print('%d PITCH: %s' % (step.pos + 1, value))
        if self.paused:
            # Play note
            self.scheduler.schedule_note(step)

    def set_step_duration(self, value, pos=None):
        self.steps.set_step_duration(value, pos)
        step = self.steps.get_step(pos)
        self.big_print('%d DUR : %.2f' % (step.pos + 1, value))
        if self.paused:
            # Play note
            self.scheduler.schedule_note(step)

    def set_step_velocity(self, value, pos=None):
        self.steps.set_step_velocity(value, pos)
        step = self.steps.get_step(pos)
        self.big_print('%d VEL : %s' % (step.pos + 1, value))
        if self.paused:
            # Play note
            self.scheduler.schedule_note(step)

    def set_step_cc(self, control, value, pos=None):
        self.steps.set_step_cc(control, value)
        step = self.steps.get_step(pos)
        self.big_print('%d CC %s : %s' % (step.pos + 1, control, value))
        if self.paused:
            # Play note
            self.scheduler.schedule_note(step)

    def set_tempo(self, value):
        self.tempo.bpm = value
        self.big_print('BPM: %s' % value)

    def toggle_step(self, step_index):
        if step_index < self.step_count:  # Some controllers can send toggles on steps outside our step count
            step = self.steps.toggle_step(step_index)
            if self.paused:
                if self.next_step_on_note and step_index == self.current_step.pos:
                    # We toggled the current step: this is like a note. Move forward
                    self.next_step(False)
                else:
                    # Play note
                    self.scheduler.schedule_note(step)
                    # Force status refresh for listeners
                    self.set_event(SequencerEvents.PAUSE, self.steps)
            self.big_print('%d : %s' % (step.pos + 1, 'on' if step.on else 'off'))
            return step

    def increase_step_count(self):
        old_step_count = self.steps.step_count
        self.steps.increase_step_count()
        self.big_print('%d -> %d STEPS' % (old_step_count, self.steps.step_count))
        if self.paused:
            # Force status refresh for listeners
            self.set_event(SequencerEvents.PAUSE, self.steps)

    def toggle_protect(self):
        self.protected = not self.protected
        self.big_print('PROTECT: ' + ('ON' if self.protected else 'OFF'))

    def next_synth(self):
        if len(self.synths) > 1:
            self.current_synth_index = (self.current_synth_index + 1) % len(self.synths)
            self.big_print('SYNTH: %s' % (self.synths[self.current_synth_index]))
