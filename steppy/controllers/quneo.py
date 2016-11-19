# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from ..base_controller import BaseController
from ..note import Note
from ..rules import Rule, RulesChain
from ..sequencer_events import SequencerEvents


class Quneo(BaseController):

    HIGH = 127
    LOW = 30
    GREEN = 0
    RED = 1

    def __init__(self, sequencer, port_name='QUNEO'):
        super(Quneo, self).__init__(sequencer, port_name)

        self.sequencer.on(SequencerEvents.STEP_BEGIN, self, self.on_step_begin)
        self.sequencer.on(SequencerEvents.STEP_END, self, self.on_step_end)
        self.sequencer.on(SequencerEvents.PAUSE, self, self.on_pause)
        self.sequencer.on(SequencerEvents.RESUME, self, self.on_resume)
        self.sequencer.on(SequencerEvents.START, self, self.on_start)
        self.sequencer.on(SequencerEvents.STOP, self, self.on_stop)

        self.register('PAUSE', lambda *args, **kw: self.sequencer.pause(),
                      RulesChain(Rule(type_='note_off', note=42)))

        self.register('RESUME', lambda *args, **kw: self.sequencer.resume(),
                      RulesChain(Rule(type_='note_off', note=43)))

        self.register('PREV_STEP', lambda *args, **kw: self.sequencer.prev_step(),
                      RulesChain(Rule(type_='note_off', note=33)))

        self.register('NEXT_STEP', lambda *args, **kw: self.sequencer.next_step(),
                      RulesChain(Rule(type_='note_off', note=34)))

        self.register('STEP COUNT++', self.handle_increase_step_count,
                      RulesChain(Rule(type_='note_off', note=36)))

        # ROWS
        for i in range(0,32):
            self.register('PAD PRESS: #%d' % (i+1),
                          lambda msgs, i=i, **kw: self.handle_pad_press(msgs, i),
                          RulesChain(Rule(type_='note_on', note=78 - int(i/8) * 8 + (i%8))))
            self.register('PAD RELEASE: #%d' % (i+1),
                          lambda msgs, i=i, **kw: self.handle_pad_release(msgs, i),
                          RulesChain(Rule(type_='note_on', note=78 - int(i/8) * 8 + (i%8))))

    @property
    def _play_msgs(self):
        return [Note('B1').start_message,
                Note('A#1').end_message]

    @property
    def _pause_msgs(self):
        return [Note('B1').end_message,
                Note('A#1').start_message]

    @property
    def _stop_msgs(self):
        return [Note('B1').end_message,
                Note('A#1').end_message]

    def _leds_msgs(self, pos, on, color=None, double_row=True, intensity=None):
        if color is None:
            color = self.RED
        if intensity is None:
            intensity = self.HIGH
        # TODO clean...
        if pos < 8:
            rows = (6,)
        elif pos < 16:
            rows = (5,)
        elif pos < 24:
            rows = (4,)
        else:
            rows = (3,)
        return [getattr(Note(numeric_note=16*(i+1) + 2*(pos % 8) + color,
                             channel=1,
                             velocity=intensity),
                        'start_message' if on else 'end_message') \
                     for i in rows]

    def on_start(self):
        # Init leds
        self._reinit_leds(self.sequencer.steps)
        self.sequencer.output(self, *self._play_msgs)

    def on_stop(self):
        self.sequencer.output(self, *self._stop_msgs)
        for i in range(0, self.sequencer.step_count):
            self.sequencer.output(self, *self._leds_msgs(i, False, self.RED))
            self.sequencer.output(self, *self._leds_msgs(i, False, self.GREEN))

    def on_step_begin(self, step):
        prev_step = self.sequencer.get_step(self.sequencer.steps.get_previous_step_index())  # DEMETER!
        self.sequencer.output(self, *self._leds_msgs(step.pos, False, color=self.RED))
        self.sequencer.output(self, *self._leds_msgs(step.pos, False, color=self.GREEN))
        self.sequencer.output(self, *self._leds_msgs(prev_step.pos, False, color=self.RED))
        self.sequencer.output(self, *self._leds_msgs(prev_step.pos, False, color=self.GREEN))
        if step.on:
            self.sequencer.output(self, *self._leds_msgs(step.pos, True, color=self.RED, intensity=self.HIGH))
        else:
            # Orange
            self.sequencer.output(self, *self._leds_msgs(step.pos, True, color=self.GREEN, intensity=self.HIGH))
            self.sequencer.output(self, *self._leds_msgs(step.pos, True, color=self.RED, intensity=self.HIGH))
        if prev_step.on:
            self.sequencer.output(self, *self._leds_msgs(prev_step.pos, True, color=self.RED, intensity=self.LOW))
        else:
            # Yellow
            self.sequencer.output(self, *self._leds_msgs(prev_step.pos, True, color=self.GREEN, intensity=self.HIGH))
            self.sequencer.output(self, *self._leds_msgs(prev_step.pos, True, color=self.RED, intensity=self.LOW))

    def on_step_end(self, step):
        self.sequencer.output(self, *self._leds_msgs(step.pos, False))


    def _reinit_leds(self, steps):
        current_step = steps.current_step
        if self.sequencer.next_step_on_note:
            color, color_to_reset = self.GREEN, self.RED
        else:
            color, color_to_reset = self.RED, self.GREEN
        for i, step in enumerate(steps.steps):
            self.sequencer.output(self, *self._leds_msgs(i, False, color_to_reset))
        for i, step in enumerate(steps.steps):
            intensity = self.HIGH if step == current_step else self.LOW
            self.sequencer.output(self, *self._leds_msgs(i, True, color, step.on, intensity))
            if not step.on:
                # If step is off, we also send the other color to have a blend -> yellow
                self.sequencer.output(self, *self._leds_msgs(i, True, color_to_reset, step.on, self.HIGH))

    def on_pause(self, steps):
        self.sequencer.output(self, *self._pause_msgs)
        self._reinit_leds(steps)

    def on_resume(self, step):
        self.sequencer.output(self, *self._play_msgs)

    def handle_pad_press(self, msgs, i):
        self.sequencer.output(self, *self._leds_msgs(i, True, self.RED))
        self.sequencer.output(self, *self._leds_msgs(i, True, self.GREEN))

    def handle_pad_release(self, msgs, i):
        self.sequencer.output(self, *self._leds_msgs(i, False, self.RED))
        self.sequencer.output(self, *self._leds_msgs(i, False, self.GREEN))
        step = self.sequencer.toggle_step(i)
        if step:
            self.sequencer.print_str('%d : %s' % (i+1, 'on' if step.on else 'off'))

    def handle_increase_step_count(self, *args, **kw):
        self.sequencer.increase_step_count()
        # Init leds
        self.on_pause(self.sequencer.steps)
