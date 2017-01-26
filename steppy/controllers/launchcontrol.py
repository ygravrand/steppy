# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from mido import Message

from ..rules import Rule, RulesChain
from ..sequencer_events import SequencerEvents
from .base_controller import BaseController


class LaunchControl(BaseController):

    FACTORY_TPL = 8

    OFF = 0
    RED_LOW = 13
    RED_MEDIUM = 14
    RED_HIGH = 15
    AMBER_LOW = 29
    AMBER_HIGH = 63
    YELLOW = 62
    GREEN_LOW = 28
    GREEN_HIGH = 60

    def __init__(self, sequencer, console, port_name='Launch Control'):
        super(LaunchControl, self).__init__(sequencer, console, port_name)

        self.sequencer.on(SequencerEvents.STEP_BEGIN, self, self.on_step_begin)
        self.sequencer.on(SequencerEvents.STEP_END, self, self.on_step_end)
        self.sequencer.on(SequencerEvents.PAUSE, self, self.on_pause)
        self.sequencer.on(SequencerEvents.RESUME, self, self.on_resume)
        self.sequencer.on(SequencerEvents.START, self, self.on_start)
        self.sequencer.on(SequencerEvents.STOP, self, self.on_stop)

        self.register('BUT DOWN LEFT', self.handle_pause_button,
                      RulesChain(Rule(type_='control_change', control=116, value=0)))

        self.register('PLAY_HOLD', self.handle_play_button,
                      RulesChain(Rule(type_='control_change', control=117, value=127)))

        self.register('BUT DOWN RIGHT', lambda *args, **kw: self.sequencer.resume(),
                      RulesChain(Rule(type_='control_change', control=117, value=0)))

        self.register('BUT UP LEFT', self.handle_upper_left_button,
                      RulesChain(Rule(type_='control_change', control=114, value=0)))

        self.register('BUT UP RIGHT', self.handle_upper_right_button,
                      RulesChain(Rule(type_='control_change', control=115, value=0)))

        for i in range(0, 9):
            self.register('ROTARIES: FIRST ROW #%d' % (i + 1),
                          lambda msgs, rules, i=i: self.handle_rotaries_first_row(msgs, i),
                          RulesChain(Rule(type_='control_change', control=21 + i)))

        for i in range(0, 9):
            self.register('ROTARIES: SECOND ROW #%d' % (i + 1),
                          lambda msgs, rules, i=i: self.handle_rotaries_second_row(msgs, i),
                          RulesChain(Rule(type_='control_change', control=41 + i)))

        for i in range(0, 9):
            note = (9 + i) if i < 4 else (21 + i)
            self.register('PAD PRESS: #%d' % (i + 1),
                          lambda msgs, rules, i=i: self.handle_pad_press(msgs, i),
                          RulesChain(Rule(type_='note_on', channel=8, note=note)))
            self.register('PAD RELEASE: #%d' % (i + 1),
                          lambda msgs, rules, i=i: self.handle_pad_release(msgs, i),
                          RulesChain(Rule(type_='note_off', channel=8, note=note)))

    def _output_led_sysex(self, template, led, value):
        self.sequencer.output(self,
                              Message(type='sysex',
                                      data=[0, 32, 41, 2, 10, 120,
                                            template, led % 8, value]))

    def _output_led_button_sysex(self, template, led, on):
        self.sequencer.output(self,
                              Message(type='sysex',
                                      data=[0, 32, 41, 2, 10, 120,
                                            template, (led % 4 + 8), 127 if on else 0]))

    def _display_step(self, step, high):
        if high:
            self._output_led_sysex(self.FACTORY_TPL, step.pos, self.RED_HIGH if step.on else self.AMBER_HIGH)
        else:
            self._output_led_sysex(self.FACTORY_TPL, step.pos, self.RED_MEDIUM if step.on else self.AMBER_LOW)

    def on_step_begin(self, step):
        if step.pos % 8 == 0:
            self.on_pause(self.sequencer.steps)
        else:
            prev_step = self.sequencer.get_step(self.sequencer.steps.get_previous_step_index())  # DEMETER!
            self._display_step(prev_step, False)
            self._display_step(step, True)

    def on_step_end(self, step):
        self._display_step(step, False)

    def on_pause(self, steps):
        current_step = steps.current_step
        # Take the 8 next steps closest to the current step
        steps_start = 8 * int(current_step.pos / 8)
        for i, step in enumerate(steps.steps[steps_start:steps_start + 8]):
            if step.on:
                if self.sequencer.next_step_on_note:
                    color = self.GREEN_LOW if step != current_step else self.GREEN_HIGH
                else:
                    color = self.RED_MEDIUM if step != current_step else self.RED_HIGH
            else:
                color = self.AMBER_LOW if step != current_step else self.AMBER_HIGH
            self._output_led_sysex(self.FACTORY_TPL, i, color)

        # pause_color = self.GREEN_HIGH if self.sequencer.next_step_on_note else self.RED_HIGH
        self._output_led_button_sysex(self.FACTORY_TPL, 2, True)
        self._output_led_button_sysex(self.FACTORY_TPL, 3, False)

    def on_resume(self, step):
        self._clear()
        self._output_led_button_sysex(self.FACTORY_TPL, 3, True)

    def on_start(self):
        self._clear()
        self._output_led_button_sysex(self.FACTORY_TPL, 3, True)

    def on_stop(self):
        self._clear()

    def _clear(self):
        for i in range(0, 8):
            self._output_led_sysex(self.FACTORY_TPL, i, self.OFF)
        for i in range(0, 4):
            self._output_led_button_sysex(self.FACTORY_TPL, i, False)

    def handle_rotaries_first_row(self, msgs, i):
        val = msgs[0].value
        self.sequencer.set_step_pitch(val, i)

    def handle_rotaries_second_row(self, msgs, i):
        val = msgs[0].value / 127
        self.sequencer.set_step_duration(val, i)

    def handle_pad_press(self, msgs, i):
        step = self.sequencer.get_step(i)
        self._output_led_sysex(self.FACTORY_TPL, i, self.AMBER_HIGH if step.on else self.RED_HIGH)

    def handle_pad_release(self, msgs, i):
        target_pos = 8 * self.sequencer.steps.get_current_row() + i
        self.sequencer.toggle_step(target_pos)
        step = self.sequencer.get_step(target_pos)
        self._display_step(step, self.sequencer.current_step.pos == step)

    def handle_upper_left_button(self, *args, **kw):
        if self.sequencer.paused:
            self.sequencer.prev_step()
        else:
            self.sequencer.toggle_protect()

    def handle_upper_right_button(self, *args, **kw):
        if self.sequencer.paused:
            self.sequencer.next_step()
        else:
            self.sequencer.next_synth()

    def handle_pause_button(self, *args, **kw):
        self.sequencer.pause()

    def handle_play_button(self, *args, **kw):
        pass
        # self.sequencer.set_transpose_mode()
